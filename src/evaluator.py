
from datetime import datetime, timezone

CLOSE_RATIO = 0.8

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
    if required <= 0:
        return "accepted"
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


def percent_reached(value, required):
    if value is None or required <= 0:
        return None
    return min(value / required, 1.0)


def evaluate(data, requirements, required_languages=None):
    decision, checks = decide(data, requirements, required_languages)

    review = []   
    reached = []  
    for name, value, required, result in checks:
        if name == "languages":
            pct = None 
        elif required <= 0:
            continue    
        else:
            pct = percent_reached(value, required)
            if pct is not None:
                reached.append(pct)
        review.append((name, value, required, pct, result))

    if reached:
        score = int(sum(reached) / len(reached) * 20 + 0.5)  # round half up
        level = get_level(score)
    else:
        score = None
        level = "Not scored"

    return {
        "username": data.username,
        "score": score,
        "level": level,
        "decision": decision,
        "review": review,
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