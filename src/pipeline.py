import evaluator
from urllib.parse import urlparse


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

def get_input():

    source = input("Enter the GitHub profile URL: ")

    source = extract_username
    if not source :
        print("unavalible url")
    else :    
       print("\nChoose the criteria to evaluate:")
       print("1. Number of public repositories")
       print("2. Number of followers")
       print("3. Account age")
       print("4. Programming languages")
       print("5. Recent activity")

       selected = input("Enter criteria numbers separated by commas: ")

       criteria = selected.split(",")
       print("Selected criteria:", criteria)

    return source, criteria

# print(get_input())