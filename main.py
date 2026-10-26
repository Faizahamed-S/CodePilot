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


def generate_commit_message(diff: str) -> tuple[str, str]:
    client = Anthropic()
    model = os.getenv("CODEPILOT_MODEL", "claude-haiku-5-5")

    prompt = (
        "Write a git commit message for the diff below.\n"
        "First line: a summary in the format type(scope): subject\n"
        "Then a blank line, then a 1-3 sentence description of what changed and why.\n"
        "Reply with only the commit message, nothing else.\n\n"
        f"{diff}"
    )
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    message = "".join(text_parts).strip()

    subject, _, description = message.partition("\n\n")
    return subject.strip(), description.strip()


def commit(subject: str, description: str) -> None:
    args = ["git", "commit", "-m", subject]
    if description:
        args += ["-m", description]
    subprocess.run(args, check=True)


def main():
    diff = get_staged_diff()
    if not diff.strip():
        print("Nothing is staged")
        return

    subject, description = generate_commit_message(diff)
    print("Suggested commit message:\n")
    print(subject)
    if description:
        print()
        print(description)

    answer = input("\nCommit with this message? [y/n]: ").strip().lower()
    if answer == "y":
        commit(subject, description)
    else:
        print("Cancelled. Nothing was committed.")


if __name__ == "__main__":
    main()