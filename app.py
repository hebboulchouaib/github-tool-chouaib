import streamlit as st
from src.pipeline import main_pipeline, read_entries

LANGUAGES=["Python","JavaScript","TypeScript","Java","C","C++","C#","PHP", "Go","Rust", "Kotlin", "Swift","SQL","Ruby","Dart"]

CRITERIA = {
    "repos": ("Minimum public repos", 100),
    "followers": ("Minimum followers", 500),
    "account_age": ("Minimum account age (years)", 20),
    "commits": ("Minimum total commits", 2000),
    "topics": ("Minimum topics", 20),
    "external": ("Minimum external repos contributed to", 50),
}


def ask_criteria():
    requirements = {}
    with st.sidebar:
        st.header(" Criteria")
        st.caption("0 means any value is accepted.")
        for name, (label, maximum) in CRITERIA.items():
            requirements[name] = st.slider(label, 0, maximum, 0)
        languages = st.multiselect("Required languages", LANGUAGES)
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
    rows = [
        {"username": r["username"], "score": r["score"], "level": r["level"],
         "decision": r["decision"],
         "review": r["error"] if r["error"] else "click the row to view"}
        for r in results
    ]
    event = st.dataframe(
        rows, on_select="rerun", selection_mode="single-row", hide_index=True
    )

    selected = event.selection.rows
    if not selected:
        return
    r = results[selected[0]]
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
            except Exception as error:
                st.error(f"Analysis failed: {error}")
                return

    if "results" in st.session_state:
        show_results(st.session_state["results"])
main()
