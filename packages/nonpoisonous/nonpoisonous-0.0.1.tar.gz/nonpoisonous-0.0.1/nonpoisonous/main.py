import sys


def main():
    """Main function that interprets user commands."""

    if len(sys.argv) < 2:
        print("Usage: nonpoisonous <command>")
        print("Available commands: help")
        return

    command = sys.argv[1]
    if command == "help":
        print("[HELP]")
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
