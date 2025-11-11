# foundrydb/cli.py
"""
Simple REPL for FoundryDB
"""


def main():
    print("FoundryDB CLI starting…")
    print("Type '.exit' to quit.")

    while True:
        cmd = input("foundrydb> ").strip()
        if cmd in (".exit", "exit", "quit"):
            print("Goodbye!")
            break
        elif cmd:
            print(f"(pretending to execute): {cmd}")
