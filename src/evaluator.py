
from datetime import datetime, timezone
from src.fetcher import *

CLOSE_RATIO = 0.8

def account_older_than_year(data):
    now = datetime.now(timezone.utc)
    created_at = data.created_at

 
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return (now - created_at).days > 365

def lang_score(languages):
    power_lang = set()
    score = 0

    for lang, count in languages.items():
        if count > 2:
            power_lang.add(lang)
            score += 1

    return score, power_lang

def account_age_years(data):
    created_at = data.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - created_at).days / 365

def get_value(data, name):
    values = {
        "followers": data.followers,
        "repos": data.public_repos,
        "account_age": account_age_years(data),
        "commits": data.total_commits,
        "topics": len(data.topics),
        "external": data.external_repos_contributed_to,
    }
    return values[name]

def check_one(value, required):
    if value is None:
        return "unknown"
    if value >= required:
        return "accepted"
    if value >= required * CLOSE_RATIO:
        return "close"
    return "rejected"




def decide(data, requirements, required_languages=None):

    lines = []

    for name, required in requirements.items():
        value = get_value(data, name)
        lines.append((name, value, required, check_one(value, required)))

    if required_languages:
        known = [lang.lower() for lang in data.languages]
        missing = [lang for lang in required_languages if lang.lower() not in known]
        result = "rejected" if missing else "accepted"
        lines.append(("languages", list(data.languages), required_languages, result))

    results = [line[3] for line in lines]
    if "rejected" in results:
        decision = "REJECTED"
    elif "close" in results or "unknown" in results:
        decision = "NEED REVIEW"
    else:
        decision = "ACCEPTED"

    return decision, lines

def evaluate_profile(data):
    breakdown = []  

    # followers
    if data.followers > 6:
        points = 2
    elif data.followers >= 2:
        points = 1
    else:
        points = 0
    breakdown.append(("followers", data.followers, points))

    # public repos
    if data.public_repos > 5:
        points = 3
    elif data.public_repos >= 3:
        points = 1
    else:
        points = 0
    breakdown.append(("repos", data.public_repos, points))

    # account age
    older = account_older_than_year(data)
    points = 2 if older else 1
    breakdown.append(("account_age", older, points))

    # commits (None means no token, so no points can be given)
    if data.total_commits is None:
        points = None
    elif data.total_commits > 80:
        points = 3
    elif data.total_commits >= 50:
        points = 1
    else:
        points = 0
    breakdown.append(("commits", data.total_commits, points))

    # topics
    breakdown.append(("topics", len(data.topics), min(len(data.topics), 5)))

    # external contributions (None means no token)
    if data.external_repos_contributed_to is None:
        points = None
    else:
        points = min(5, data.external_repos_contributed_to // 3)
    breakdown.append(("external", data.external_repos_contributed_to, points))
    score = 0
    for name, value, points in breakdown:
        if points is not None:
            score += points

    return score, breakdown

MAX_POINTS = {
    "followers": 2, "repos": 3, "account_age": 2,
    "commits": 3, "topics": 5, "external": 5,
}

def get_level(score):
    if score < 5:
        return "Bad"
    if score < 10:
        return "Below average"
    if score == 10:
        return "Average"
    if score < 15:
        return "Above average"
    if score < 20:
        return "Good"
    return "Perfect"


def evaluate(data, requirements, required_languages=None):
    score, breakdown = evaluate_profile(data)

    measurable = 0
    for name, value, points in breakdown:
        if points is not None:
            measurable += MAX_POINTS[name]

    scaled = round(score / measurable * 20)
    decision, checks = decide(data, requirements, required_languages)

    return {
        "username": data.username,
        "score": scaled,
        "raw_score": score,
        "measurable_max": measurable,
        "level": get_level(scaled),
        "decision": decision,
        "breakdown": breakdown,
        "checks": checks,
    }

#test 
# profile = ProfileData(
#         username="lmcouli",
#         name="The Mcouli",
#         created_at=datetime(2011, 1, 25, 18, 44, 36, tzinfo=timezone.utc),
#         followers=1000,
#         public_repos=8,
#         repos_analyzed=6,
#         languages={"Python": 3, "C": 1, "Go": 1},
#         topics={"cli": 2, "api": 1},
#         total_commits=412,
#         external_repos_contributed_to=7,
#     )
# requ={
#      "followers": 2000,
#      "repos": 400,
#      "account_age": 3,
#      "commits": 40,
#      "topics": 4,
#      "external": 10
# }

# print(decide(profile, {"followers": 10, "commits": 100}))
# print(decide(profile, {"commits": 450})[0])
# print(decide(profile, {"commits": 1000})[0])
# print(decide(profile, {"followers": 10}, ["Python", "Rust"])[0])
# print(decide(profile, {"followers": 10}, ["python", "go"])[0])
# no_token = ProfileData(
#     username="lmcouli",
#     name="The Mcouli",
#     created_at=datetime(2011, 1, 25, 18, 44, 36, tzinfo=timezone.utc),
#     followers=1000,
#     public_repos=8,
#     repos_analyzed=6,
#     languages={"Python": 3, "C": 1, "Go": 1},
#     topics={"cli": 2, "api": 1},
#     total_commits=None,
#     external_repos_contributed_to=None,
# )

# print(decide(no_token, {"commits": 100})[0])
# result = evaluate(no_token, {"followers": 10})
# print(result["score"], result["level"], result["decision"])