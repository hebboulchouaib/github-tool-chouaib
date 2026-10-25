

import json
from datetime import datetime, timezone

#func that retrun num day ....
def account_older_than_year(data):
    created_at = data.get("created_at")

    if not created_at:
        return False

    created_date = datetime.fromisoformat(
        created_at.replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    return (now - created_date).days > 365

#func evaluate profile of github : 


def evalulate_profile(data):
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
    now = datetime.now(timezone.utc)

    if data.created_at:
        age_days = (now - data.created_at).days

        if age_days > 365:
            profile_score += 2
        else:
            profile_score += 1

    # Check commit count
    if data.total_commits < 50:
        profile_score += 1
    elif data.total_commits > 80:
        profile_score += 3

    return profile_score


#  this function will check for each repo the number of lang used in and store it .
#  so after we can see if there s another repos write with the same lang stored .
#  this mean he is strong at this lang . 

def check_lang(repos):
    languages = {}

    for repo in repos:
        lang = repo.get("language")

        if lang:
            if lang in languages:
                languages[lang] += 1
            else:
                languages[lang] = 1

    return languages


def lang_score(languages):
    power_lang = set()
    lang_score = 0

    for lang in languages:
        if languages[lang] > 2:
            power_lang.add(lang)
            lang_score += 1

    return lang_score, power_lang


# this func will se if the user is active in github or not by calculate the differnce between the pushed_date and the currently day   

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

def evaluate_repositories(repos):
    repo_score = 0

    for repo in repos:
        # Check original repository
        if repo.get("fork"):
            continue

        # Check if archived
        if repo.get("archived"):
            continue

        # Check stars
        stars = repo.get("stargazers_count", 0)

        if stars < 2:
            repo_score += 1
        elif stars > 5:
            repo_score += 2

        # Check description
        if repo.get("description"):
            repo_score += 1

    # Check language
    languages = check_lang(repos)
    score, power_lang = lang_score(languages)
    repo_score += score

    return repo_score, power_lang


#profile_data = {}
#repos = []
'''
profile_score = evalulate_profile(profile_data)
repo_score, strong_languages = evaluate_repositories(repos)
activity = activity_score(repos)
total_score = profile_score + repo_score + activity
#result = check_eligibility(profile_score, repo_score)

print("Profile score:", profile_score)
print("Repository score:", repo_score)
print("Activity score:", activity)
print("Total score:", total_score)
#print("Eligibility:", result)

