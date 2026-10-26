from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class ProfileData:
    username: str
    name: str
    created_at: datetime
    followers: int
    public_repos: int
    repos_analyzed: int
    languages: dict
    topics: dict
    language_bytes: object
    total_commits: int
    external_repos_contributed_to: int


def account_older_than_year(data):
    now = datetime.now(timezone.utc)
    created_at = data.created_at

 
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return (now - created_at).days > 365



def evaluate_profile(data):
    profile_score = 0

    # Check followers
    if data.followers < 2:
        profile_score += 1
    elif data.followers > 6:
        profile_score += 2

    # Check public repositories
    if data.public_repos < 3:
        profile_score += 1
    elif data.public_repos > 5:
        profile_score += 3

    # Check account age
    if account_older_than_year(data):
        profile_score += 2
    else:
        profile_score += 1

    # Check commits
    if data.total_commits < 50:
        profile_score += 1
    elif data.total_commits > 80:
        profile_score += 3

    # Check programming languages
    language_points, power_lang = lang_score(data.languages)
    profile_score += language_points

    # Check topics
    profile_score += len(data.topics)

    # Check external contributions
    profile_score += min(
        5, data.external_repos_contributed_to // 3
    )

    return profile_score, account_older_than_year(data)


def check_lang(data):
    return data.languages


def lang_score(languages):
    power_lang = set()
    score = 0

    for lang, count in languages.items():
        # languages used a lot (more than 2 repos) count as strong languages
        if count > 2:
            power_lang.add(lang)
            score += 1

    return score, power_lang


'''
def activity_score(repos):
    score = 0
    now = datetime.now(timezone.utc)

    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue

        pushed_at = repo.get("pushed_at")

        if not pushed_at:
            continue

        pushed_date = datetime.fromisoformat(
            pushed_at.replace("Z", "+00:00")
        )

        days = (now - pushed_date).days

        if days <= 30:
            score += 3
        elif days <= 90:
            score += 2
        elif days <= 180:
            score += 1

    return score

'''

# Test profile
profile = ProfileData(
    username="lmcouli",
    name="The Mcouli",
    created_at=datetime(
        2011, 1, 25, 18, 44, 36,
        tzinfo=timezone.utc
    ),
    followers=1000,
    public_repos=8,
    repos_analyzed=6,
    languages={"Python": 3, "C": 1, "Go": 1},
    topics={"cli": 2, "api": 1},
    language_bytes=None,
    total_commits=412,
    external_repos_contributed_to=7,
)

score, account_age = evaluate_profile(profile)
languages = check_lang(profile)
language_points, power_lang = lang_score(languages)


print("Username:", profile.username)
print("Profile score:", score, "/20 .")
if score >= 10:
    print("Result : ACCEPTED .")
elif 5 < score < 10:
    print("Result : NEED REVIEW .")
else:
    print("Result : REJECTED")

print("num commit : ", profile.total_commits)
print("account-age : ", account_age)
print("Languages:", languages)
print("Strong languages:", power_lang)


