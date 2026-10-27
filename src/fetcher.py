
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

import httpx

API = "https://api.github.com"
GRAPHQL_URL = f"{API}/graphql"
USERNAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")

COMMITS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) { totalCommitContributions }
  }
}
"""

EXTERNAL_REPOS_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositoriesContributedTo(first: 1, includeUserRepositories: false,
                              contributionTypes: [COMMIT, PULL_REQUEST]) {
      totalCount
    }
  }
}
"""


class GitHubError(Exception):
    pass


class UserNotFoundError(GitHubError):
    pass


class RateLimitError(GitHubError):
    pass


@dataclass(frozen=True)
class ProfileData:
    username: str
    name: str | None
    created_at: datetime
    followers: int
    public_repos: int
    repos_analyzed: int
    languages: dict[str, int] = field(default_factory=dict)
    topics: dict[str, int] = field(default_factory=dict)
    total_commits: int | None = None
    external_repos_contributed_to: int | None = None


def fetch_profile(username: str, token: str | None = None) -> ProfileData:
    """Fetch a user's public profile and summarize their owned repositories."""
    if not USERNAME_RE.fullmatch(username):
        raise ValueError(f"Invalid GitHub username: {username!r}")
    # An explicit token takes priority; otherwise use the environment setting.
    token = token or os.environ.get("GITHUB_TOKEN")

    user = _call("GET", f"{API}/users/{username}", token).json()
    created_at = datetime.fromisoformat(user["created_at"])

    repos = []
    page = 1
    while True:
        # GitHub returns at most 100 repositories per page.
        batch = _call(
            "GET",
            f"{API}/users/{username}/repos",
            token,
            params={"per_page": 100, "type": "owner", "page": page},
        ).json()
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    # Exclude forks so the summary reflects repositories the user created.
    own_repos = [repo for repo in repos if not repo["fork"]]
    languages = Counter(repo["language"] for repo in own_repos if repo["language"])
    topics = Counter(t for repo in own_repos for t in repo.get("topics") or [])

    total_commits = None
    external_repos = None
    if token:
        # These contribution totals require authenticated GraphQL requests.
        total_commits = _count_commits(username, created_at.year, token)
        data = _graphql(EXTERNAL_REPOS_QUERY, {"login": username}, token)
        external_repos = data["repositoriesContributedTo"]["totalCount"]

    return ProfileData(
        username=username,
        name=user["name"],
        created_at=created_at,
        followers=user["followers"],
        public_repos=user["public_repos"],
        repos_analyzed=len(own_repos),
        languages=dict(languages),
        topics=dict(topics),
        total_commits=total_commits,
        external_repos_contributed_to=external_repos,
    )


def _count_commits(username: str, first_year: int, token: str) -> int:
    # Query one calendar year at a time, ending the current year at today's date.
    now = datetime.now(UTC)
    total = 0
    for year in range(first_year, now.year + 1):
        if year == now.year:
            end = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            end = f"{year}-12-31T23:59:59Z"
        variables = {"login": username, "from": f"{year}-01-01T00:00:00Z", "to": end}
        data = _graphql(COMMITS_QUERY, variables, token)
        total += data["contributionsCollection"]["totalCommitContributions"]
    return total


def _graphql(query: str, variables: dict, token: str) -> dict:
    # Return the user's data, converting GraphQL errors into app-level exceptions.
    body = _call(
        "POST", GRAPHQL_URL, token, json={"query": query, "variables": variables}
    ).json()
    errors = body.get("errors")
    if errors:
        if any(error.get("type") == "RATE_LIMITED" for error in errors):
            raise RateLimitError("GitHub API rate limit exceeded")
        raise GitHubError(f"GraphQL error: {errors}")
    return body["data"]["user"]


def _call(method: str, url: str, token: str | None, **kwargs) -> httpx.Response:
    # Share headers, timeout, and HTTP error handling across REST and GraphQL calls.
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = httpx.request(method, url, headers=headers, timeout=10, **kwargs)
    except httpx.HTTPError as error:
        raise GitHubError(f"Network error: {error}") from error

    if response.status_code == 404:
        raise UserNotFoundError(f"Not found: {url}")
    if response.status_code in (403, 429) and (
        response.headers.get("x-ratelimit-remaining") == "0"
        or "rate limit" in response.text.lower()
    ):
        raise RateLimitError("GitHub API rate limit exceeded")
    if response.status_code >= 400:
        raise GitHubError(f"HTTP {response.status_code}: {response.text}")
    return response