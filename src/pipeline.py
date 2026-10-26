def get_input():
    print("1. Scan a single GitHub profile")
    print("2. Scan profiles from a file")

    choice = input("Choose an option (1/2): ")

    if choice == "1":
        source = input("Enter the GitHub profile URL: ")

    elif choice == "2":
        source = input("Enter the file path: ")

    else:
        print("Invalid choice!")
        return None, []

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


get_input()
