import re
import streamlit as st

# Try to use the teammates' backend; fall back to demo data until it's ready.
try:
    from src.pipeline import run_pipeline  # expected: run_pipeline(username, criteria) -> dict
    BACKEND_READY = True
except Exception:
    BACKEND_READY = False

    def run_pipeline(username, criteria):
        return {
            "profile": {"name": username, "followers": 42, "public_repos": 18,
                        "total_stars": 130, "languages": ["Python", "JavaScript"]},
            "checks": {
                "min_repos": True, "min_followers": True,
                "min_stars": True, "required_languages": False,
            },
            "score": 75,
            "eligible": True,
        }


def extract_username(text: str) -> str:
    """Accepts 'octocat' or 'https://github.com/octocat/...' and returns 'octocat'."""
    text = text.strip()
    m = re.search(r"github\.com/([A-Za-z0-9-]+)", text)
    return m.group(1) if m else text.strip("/@ ")


st.set_page_config(page_title="GitHub Eligibility Checker", page_icon="🔍", layout="wide")
st.title("🔍 GitHub Profile Analyzer")
st.caption("Check a developer's eligibility based on configurable criteria.")

if not BACKEND_READY:
    st.warning("Backend not connected yet: showing demo data.")

# ---- Sidebar: criteria ----
with st.sidebar:
    st.header("⚙️ Criteria")
    min_repos = st.slider("Minimum public repos", 0, 100, 5)
    min_followers = st.slider("Minimum followers", 0, 500, 10)
    min_stars = st.slider("Minimum total stars", 0, 1000, 20)
    languages = st.multiselect(
        "Required languages",
        ["Python", "JavaScript", "TypeScript", "Java", "C", "C++", "Go", "Rust", "PHP"],
    )
    criteria = {
        "min_repos": min_repos,
        "min_followers": min_followers,
        "min_stars": min_stars,
        "required_languages": languages,
    }

# ---- Main: input ----
mode = st.radio("Check by", ["Username", "Profile URL"], horizontal=True)
placeholder = "octocat" if mode == "Username" else "https://github.com/octocat"
user_input = st.text_input(mode, placeholder=placeholder)

if st.button("Analyze", type="primary"):
    username = extract_username(user_input)
    if not username:
        st.error("Please enter a username or URL.")
    else:
        with st.spinner(f"Analyzing {username}..."):
            try:
                result = run_pipeline(username, criteria)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()

        p = result["profile"]
        st.subheader(f"Results for @{username}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Public repos", p["public_repos"])
        c2.metric("Followers", p["followers"])
        c3.metric("Total stars", p["total_stars"])

        st.progress(min(int(result["score"]), 100), text=f"Score: {result['score']}/100")

        if result["eligible"]:
            st.success("✅ Eligible")
        else:
            st.error("❌ Not eligible")

        st.markdown("**Criteria breakdown**")
        for name, ok in result["checks"].items():
            st.write(f"{'✅' if ok else '❌'} {name.replace('_', ' ').capitalize()}")

        if p.get("languages"):
            st.markdown("**Languages:** " + ", ".join(p["languages"]))
