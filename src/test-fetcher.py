import sys
from pprint import pprint
from fetcher import GitHubError, fetch_profile

for name in sys.argv[1:]:
    try:
        pprint(fetch_profile(name))
    except GitHubError as error:
        print(f"{name}: {type(error).__name__}: {error}")
    except ValueError as error:
        print(f"{name}: {error}")