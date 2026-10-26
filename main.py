import subprocess
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def generate_commit_message(diff: str) -> str:
    client = Anthropic()
    model = os.getenv("CODEPILOT_MODEL", "claude-haiku-5-5")

    prompt = (
        "Write a git commit message for the diff below.\n"
        "Use the format: type(scope): subject\n"
        "Reply with only the commit message, nothing else.\n\n"
        f"{diff}"
    )
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    return "".join(text_parts).strip()


def commit(message: str) -> None:                                   
    subprocess.run(["git", "commit", "-m", message], check=True)


def main():
    diff = get_staged_diff()
    if not diff.strip():
        print("Nothing is staged")
        return

    message = generate_commit_message(diff)
    print("Suggested commit message:\n")
    print(message)

    answer = input("\nCommit with this message? [y/n]: ").strip().lower()   
    if answer == "y":                                                      
        commit(message)                                                  
    else:                                                                  
        print("Cancelled. Nothing was committed.")                          


if __name__ == "__main__":
    main()