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

#func filter profile of github : 

def filter_profile(data):
    profile_score = 0

    #  Check followers
    followers = data.get("followers", 0)

    if followers < 2:
        profile_score += 1
    elif followers > 6:
        profile_score += 2

    #  Check public repositories
    repos = data.get("public_repos", 0)

    if repos < 3:
        profile_score += 1
     elif repos > 5:
        profile_score += 3

    #  Check account age
    if account_older_than_year(data):
        profile_score += 2
    else:
        profile_score += 1

    #  Check commit count
    commits = data.get("commit_count", 0)

    if commits < 50:
        profile_score += 1
    elif commits > 80:
        profile_score += 3


    return profile_score
    
    
#def deep_filtering (data):
