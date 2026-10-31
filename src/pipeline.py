from urllib.parse import urlparse
import re
import pandas as pd
from src.evaluator import evaluate
from src.fetcher import (
    GitHubError,
    RateLimitError,
    UserNotFoundError,
    fetch_profile,
)


def extract_username(text):
    text = text.strip()
    if not text:
        return None

    if "/" not in text and "." not in text:
        return text
    if not text.startswith("http"):
        text = "https://" + text

    parsed = urlparse(text)
    if parsed.netloc not in ("github.com", "www.github.com"):
        return None

    parts = [p for p in parsed.path.split("/") if p]
    return parts[0] if parts else None


def error_result(username, message):
    return {
        "username": username, "score": None, "level": None,
        "decision": None, "error": message,
    }


def process_user(username, requirements, required_languages=None, token=None):
    try:
        profile = fetch_profile(username, token)
    except UserNotFoundError:
        return error_result(username, "User not found")
    except RateLimitError:
        return error_result(username, "GitHub rate limit reached, use a token or retry later")
    except GitHubError as error:
        return error_result(username, f"GitHub error: {error}")
    except ValueError:
        return error_result(username, "Invalid username")

    result = evaluate(profile, requirements, required_languages)
    result["error"] = None
    return result
#check if still needed with ilyes
def read_entries(text=None, file=None):
    entries = []

    if text:
        entries += [e for e in re.split(r"[\s,;]+", text) if e]

    if file is not None:
        name = str(getattr(file, "name", file)).lower()
        if name.endswith(".csv"):
            table = pd.read_csv(file)
        elif name.endswith((".xlsx", ".xls")):
            table = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file type, use .csv or .xlsx")

        column = table.columns[0]
        for candidate in table.columns:
            if str(candidate).strip().lower() in ("username", "link", "url", "github"):
                column = candidate
                break
        entries += [str(v).strip() for v in table[column].dropna() if str(v).strip()]

    return entries


def clean_usernames(entries):
    usernames = []
    invalid = []
    seen = set()

    for entry in entries:
        username = extract_username(entry)
        if username is None:
            invalid.append(entry)
        elif username.lower() not in seen:
            seen.add(username.lower())
            usernames.append(username)

    return usernames, invalid
    
def main_pipeline(entries, requirements, required_languages=None, token=None):
    
    if not requirements and not required_languages:
        raise ValueError("Select at least one requirement")

    usernames, invalid = clean_usernames(entries)

    results = []
    for username in usernames:
        results.append(process_user(username, requirements, required_languages, token))

    for entry in invalid:
        results.append(error_result(entry, "Not a valid GitHub link or username"))

    return results
