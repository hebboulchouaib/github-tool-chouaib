"""Streamlit frontend for the GitHub Profile Analyzer."""
import re
import streamlit as st

#  Settings (easy to change) 
LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "C", "C++", "Go", "Rust", "PHP"]


#  Backend connection 
def demo_pipeline(username, criteria):
    """Fake data, used until the real backend is ready."""
    return {
        "profile": {"public_repos": 18, "followers": 42, "total_stars": 130,
                    "languages": ["Python", "JavaScript"]},
        "checks": {"min_repos": True, "min_followers": True,
                   "min_stars": True, "required_languages": False},
        "score": 75,
        "eligible": True,
    }


try:
    from src.pipeline import run_pipeline
    BACKEND_READY = True
except ImportError:
    run_pipeline = demo_pipeline
    BACKEND_READY = False


#   Helpers 
def extract_username(text):
    """'octocat' or 'https://github.com/octocat/repo' -> 'octocat'."""
    text = text.strip()
    match = re.search(r"github\.com/([A-Za-z0-9-]+)", text)
    return match.group(1) if match else text.strip("/@ ")


#  Inputs 
def ask_criteria():
    """Sidebar: returns the criteria chosen by the user."""
    with st.sidebar:
        st.header("⚙️ Criteria")
        return {
            "min_repos": st.slider("Minimum public repos", 0, 100, 5),
            "min_followers": st.slider("Minimum followers", 0, 500, 10),
            "min_stars": st.slider("Minimum total stars", 0, 1000, 20),
            "required_languages": st.multiselect("Required languages", LANGUAGES),
        }


def ask_username():
    """Main area: returns the username (from a username or a URL)."""
    mode = st.radio("Check by", ["Username", "Profile URL"], horizontal=True)
    example = "octocat" if mode == "Username" else "https://github.com/octocat"
    return extract_username(st.text_input(mode, placeholder=example))


#  Output 
def show_results(username, result):
    profile = result["profile"]
    st.subheader(f"Results for @{username}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Public repos", profile["public_repos"])
    col2.metric("Followers", profile["followers"])
    col3.metric("Total stars", profile["total_stars"])

    st.progress(min(int(result["score"]), 100), text=f"Score: {result['score']}/100")

    if result["eligible"]:
        st.success("Eligible")
    else:
        st.error("Not eligible")

    st.markdown("Criteria breakdown")
    for name, passed in result["checks"].items():
        st.write(f"{'OK' if passed else 'NO'} {name.replace('_', ' ').capitalize()}")

    if profile.get("languages"):
        st.markdown("Languages: " + ", ".join(profile["languages"]))


# Main 
def main():
    st.set_page_config(page_title="GitHub Eligibility Checker", page_icon="🔍", layout="wide")
    st.title("🔍 GitHub Profile Analyzer")
    st.caption("Check a developer's eligibility based on configurable criteria.")

    if not BACKEND_READY:
        st.warning("Backend not connected yet: showing demo data.")

    criteria = ask_criteria()
    username = ask_username()

    if not st.button("Analyze", type="primary"):
        return
    if not username:
        st.error("Please enter a username or URL.")
        return

    with st.spinner(f"Analyzing {username}..."):
        try:
            result = run_pipeline(username, criteria)
        except Exception as error:
            st.error(f"Analysis failed: {error}")
            return

    show_results(username, result)


main()
