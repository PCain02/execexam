import argparse
import os
import subprocess


def confirm_action(action_description):
    """Prompts the user to confirm the action."""
    confirmation = input(
        f"Are you sure you want to {action_description}? (y/n): "
    ).lower()
    if confirmation in ["yes", "y"]:
        return True
    print("Action canceled.")
    return False


def reset_file(file_name):
    """Resets the specified file to its last commit state."""
    if confirm_action(f"reset the file: {file_name}"):
        try:
            subprocess.run(["git", "checkout", "--", file_name], check=True)
            print(f"File {file_name} has been reset.")
        except subprocess.CalledProcessError:
            print(f"Failed to reset the file: {file_name}. Does it exist?")
    else:
        print("No changes made to the file.")


def hard_reset():
    """Resets the entire repository to the last commit state."""
    if confirm_action("hard reset the entire repository"):
        try:
            subprocess.run(["git", "reset", "--hard"], check=True)
            print("Repository has been hard reset.")
        except subprocess.CalledProcessError:
            print("Failed to hard reset the repository.")
    else:
        print("No changes made to the repository.")


def main():
    parser = argparse.ArgumentParser(
        description="Reset the repo or a specific file."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--hard-reset",
        action="store_true",
        help="Reset the entire repository to the last commit.",
    )
    group.add_argument(
        "--reset", type=str, help="Reset a specific file to the last commit."
    )

    args = parser.parse_args()

    if args.hard_reset:
        hard_reset()
    elif args.reset:
        reset_file(args.reset)


if __name__ == "__main__":
    main()
