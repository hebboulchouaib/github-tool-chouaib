import os

import streamlit as st
import datetime
from src.pipeline import main_pipeline, read_entries
from src.settings import CRITERIA, LANGUAGES

try:
    from src.agent import ask_agent, apply_filter, describe_filter
except ImportError:  
    ask_agent = None
    apply_filter = lambda results, flt: results
    describe_filter = lambda flt: ""

MAX_MESSAGE_CHARS = 300   
SESSION_LIMIT = 15        
DAILY_LIMIT = 300         


@st.cache_resource
def daily_usage():
    return {"day": "", "count": 0}


def quota_left():
    usage = daily_usage()
    today = datetime.date.today().isoformat()
    if usage["day"] != today:
        usage["day"], usage["count"] = today, 0
    return usage["count"] < DAILY_LIMIT

def apply_pending():
    for action in st.session_state.pop("pending", []):
        if action["type"] == "set_criteria":
            for name, value in action["values"].items():
                key = "languages" if name == "languages" else f"crit_{name}"
                st.session_state[key] = value
        elif action["type"] == "reset":
            if action["scope"] == "all":
                for name in CRITERIA:
                    st.session_state[f"crit_{name}"] = 0
            st.session_state["languages"] = []
        elif action["type"] == "filter":
            st.session_state["results_filter"] = action["values"]
        elif action["type"] == "clear_filter":
            st.session_state.pop("results_filter", None)


def chat_panel():
    st.divider()
    st.subheader("Assistant")
    if ask_agent is None or not os.environ.get("GEMINI_API_KEY"):
        st.caption("The assistant is off (no AI key configured). The sliders still work.")
        return

    history = st.session_state.setdefault("chat", [])
    for m in history[-6:]:
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.write(m["text"])

    left = SESSION_LIMIT - st.session_state.get("chat_used", 0)
    st.caption(f"{max(left, 0)} assistant messages left in this session")
    message = st.chat_input(
        "Describe who you are looking for, or ask about the results",
        max_chars=MAX_MESSAGE_CHARS, disabled=left <= 0,
    )
    if not message:
        return
    if not quota_left():
        st.error("The assistant reached its daily limit. The sliders still work; try again tomorrow.")
        return
    try:
        with st.spinner("The assistant is thinking..."):
            reply, actions = ask_agent(history[-6:], message, st.session_state.get("results"))
    except Exception as error:
        code = getattr(error, "code", None)
        if code == 429:
            st.error("The AI quota is used up for now. The sliders still work; try again later.")
        elif code in (401, 403):
            st.error("The AI key was rejected. The sliders still work.")
        elif code == 404:
            st.error("This AI model isn't available for the key. The sliders still work.")
        else:
            st.error(f"The assistant could not answer ({type(error).__name__}). The sliders still work.")
        return

    st.session_state["chat_used"] = st.session_state.get("chat_used", 0) + 1
    daily_usage()["count"] += 1

    needs_token = any(
        a["type"] == "set_criteria"
        and (a["values"].get("commits", 0) > 0 or a["values"].get("external", 0) > 0)
        for a in actions
    )
    if needs_token and not os.environ.get("GITHUB_TOKEN"):
        reply += "\n\nNote: commits and external contributions need a GitHub token, so they can't be measured here."

    history += [{"role": "user", "text": message}, {"role": "model", "text": reply}]
    if actions:
        st.session_state["pending"] = actions
    st.rerun()

def ask_criteria():
    requirements = {}
    with st.sidebar:
        st.header("Criteria")
        st.caption("0 means any value is accepted.")
        for name, (label, maximum) in CRITERIA.items():
            requirements[name] = st.slider(label, 0, maximum, key=f"crit_{name}")
        languages = st.multiselect("Required languages", LANGUAGES, key="languages")
        chat_panel()
    return requirements, languages

def ask_entries():
    text = st.text_area(
        "GitHub links or usernames",
        placeholder="ex: octocat\nor: https://github.com/torvalds",
        height=120,
    )
    file = st.file_uploader("...or upload a CSV / Excel file", type=["csv", "xlsx"])
    return text, file

def show_results(results):
    flt = st.session_state.get("results_filter", {})
    shown = apply_filter(results, flt)

    if flt:
        left, right = st.columns([5, 1])
        left.caption(f"Showing {len(shown)} of {len(results)} rows. Filter: {describe_filter(flt)}")
        if right.button("Clear filter"):
            st.session_state.pop("results_filter", None)
            st.rerun()
    if not shown:
        st.info("No rows match the filter.")
        return

    rows = [
        {"username": r["username"], "score": r["score"], "level": r["level"],
         "decision": r["decision"],
         "review": r["error"] if r["error"] else "click the row to view"}
        for r in shown
    ]
    event = st.dataframe(
        rows, on_select="rerun", selection_mode="single-row", hide_index=True,
        key="table_" + describe_filter(flt),
    )

    selected = event.selection.rows
    if not selected or selected[0] >= len(shown):
        return
    r = shown[selected[0]]
    if r["error"]:
        st.error(f"@{r['username']}: {r['error']}")
    else:
        show_review(r)


def show_review(r):
    st.subheader(f"Review: @{r['username']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", "-" if r["score"] is None else f"{r['score']}/20")
    col2.metric("Level", r["level"])
    col3.metric("Decision", r["decision"])
    if not r["review"]:
        st.info("No criteria were set, so nothing was scored or checked.")
        return

    st.markdown("**Where the score comes from**")
    st.dataframe(
        [
            {
                "criterion": name,
                "profile value": str(value),
                "minimum": str(required),
                "reached": "-" if pct is None else f"{pct:.0%}",
                "result": result,
            }
            for name, value, required, pct, result in r["review"]
        ],
        hide_index=True,
    )
    st.caption(
        "Score = average of the 'reached' column (each capped at 100%), scaled to 20. "
        "Languages only affect the decision."
    )

def main():
    st.set_page_config(page_title="GitHub Eligibility Checker", layout="wide")
    st.title("GitHub Profile Analyzer")
    st.caption("a tool that analyse github profile based on criteria chosen by the user")
    apply_pending()
    requirements, languages = ask_criteria()
    text, file = ask_entries()
    if st.button("Analyze", type="primary"):
        if not text.strip() and file is None:
            st.error("Please enter at least one username or link, or upload a file.")
            return
        with st.spinner("Analyzing..."):
            try:
                entries = read_entries(text=text, file=file)
                st.session_state["results"] = main_pipeline(entries, requirements, languages)
                st.session_state.pop("results_filter", None)
            except Exception as error:
                st.error(f"Analysis failed: {error}")
                return

    if "results" in st.session_state:
        show_results(st.session_state["results"])
main()
