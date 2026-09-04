#!/usr/bin/env python3
"""
Dutch Practice Mode — Continuous Quiz
Run this when you have a few minutes and want to drill vocabulary.
Words you get wrong come back later in the same session.
Press 'Stop' anytime to see your score.
"""

import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
VOCAB_FILE = SCRIPT_DIR / "vocabulary.json"


def load_vocabulary() -> list[dict]:
    if not VOCAB_FILE.exists():
        alert("Practice — Error", f"Vocabulary file not found:\n{VOCAB_FILE}")
        sys.exit(1)
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            words = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        alert("Practice — Error", f"Failed to read vocabulary file:\n{exc}")
        sys.exit(1)
    if not words:
        alert("Practice — Error", "Vocabulary file is empty.")
        sys.exit(1)
    return words


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def alert(title: str, message: str) -> None:
    applescript = (
        f'display alert "{_escape(title)}" '
        f'message "{_escape(message)}" '
        f'as informational '
        f'buttons {{"OK"}} default button "OK"'
    )
    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"[{title}] {message}", file=sys.stderr)


def quiz_prompt(prompt_msg: str) -> tuple[str, str]:
    applescript = (
        f'display dialog "{_escape(prompt_msg)}" '
        f'default answer "" '
        f'with title "🇳🇱 Dutch Practice" '
        f'buttons {{"Stop", "I don\'t know", "Check"}} '
        f'default button "Check"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        button = ""
        text = ""
        for part in output.split(", "):
            if part.startswith("button returned:"):
                button = part.split(":", 1)[1]
            elif part.startswith("text returned:"):
                text = part.split(":", 1)[1]
        return button, text.strip().lower()
    except subprocess.CalledProcessError:
        return "cancel", ""
    except FileNotFoundError:
        print("osascript not found", file=sys.stderr)
        sys.exit(1)


def pick_level() -> Optional[str]:
    """Show a level picker dialog. Returns 'A1', 'A2', 'B1', 'All', or None on cancel."""
    applescript = (
        'display dialog "Choose a difficulty level:" '
        'with title "🇳🇱 Dutch Practice" '
        'buttons {"A1", "A2", "B1"} '
        'default button "B1" '
        'giving up after 0'
    )
    # osascript only supports 3 buttons max, so we use two dialogs
    applescript_all = (
        'display alert "🇳🇱 Dutch Practice" '
        'message "What level do you want to practice?" '
        'as informational '
        'buttons {"All levels", "Pick a level"} '
        'default button "Pick a level"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript_all],
            check=True, capture_output=True, text=True,
        )
        if "All levels" in result.stdout:
            return "All"

        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        for lvl in ("A1", "A2", "B1"):
            if lvl in output:
                return lvl
        return "All"
    except subprocess.CalledProcessError:
        return None


def filter_by_level(words: list[dict], level: str) -> list[dict]:
    if level == "All":
        return words
    return [w for w in words if w.get("level") == level]


def ask_word(word: dict) -> Optional[bool]:
    """
    Quiz a single word. Returns:
      True  = correct
      False = wrong or "I don't know"
      None  = user wants to stop
    """
    dutch = word["dutch"].lower()
    english = word["english"]
    example = word.get("example", "")

    label = f"Translate to Dutch:\n\n\"{english}\""
    attempt = 0

    while True:
        button, answer = quiz_prompt(label)

        if button in ("cancel", "Stop"):
            return None

        if button == "I don't know":
            reveal = f"The answer is:  {word['dutch']}"
            if example:
                reveal += f"\n\nExample:\n{example}"
            alert("🇳🇱 Now you know!", reveal)
            return False

        if answer == dutch:
            msg = f"✅  {word['dutch']}  =  {english}"
            if example:
                msg += f"\n\nExample:\n{example}"
            alert("🇳🇱 Correct!", msg)
            return True

        attempt += 1
        if attempt >= 3:
            hint = dutch[:len(dutch) // 2] + "..."
            label = (
                f"❌ Not quite. Hint:  \"{hint}\"\n\n"
                f"Translate to Dutch:\n\n\"{english}\""
            )
        else:
            label = (
                f"❌ Not quite, try again!\n\n"
                f"Translate to Dutch:\n\n\"{english}\""
            )


def main() -> None:
    all_words = load_vocabulary()

    level = pick_level()
    if level is None:
        return

    words = filter_by_level(all_words, level)
    if not words:
        alert("🇳🇱 Practice", f"No words found for level {level}.")
        return

    level_label = level if level != "All" else "All levels"
    alert("🇳🇱 Practice", f"Level: {level_label}\nWords: {len(words)}\n\nLet's go!")

    queue = random.sample(words, len(words))
    retry_queue: list[dict] = []

    correct = 0
    wrong = 0
    total = 0

    while queue or retry_queue:
        if not queue:
            random.shuffle(retry_queue)
            queue = retry_queue
            retry_queue = []

        word = queue.pop(0)
        total += 1
        result = ask_word(word)

        if result is None:
            total -= 1
            break

        if result:
            correct += 1
        else:
            wrong += 1
            retry_queue.append(word)

    if total == 0:
        alert("🇳🇱 Practice", "No words practiced. Tot de volgende keer!")
    else:
        pct = round(correct / total * 100)
        summary = (
            f"Words practiced:  {total}\n"
            f"Correct:  {correct}\n"
            f"Wrong:  {wrong}\n"
            f"Score:  {pct}%"
        )
        if pct == 100:
            summary += "\n\nPerfect! Uitstekend! 🎉"
        elif pct >= 70:
            summary += "\n\nGoed gedaan! Keep it up!"
        else:
            summary += "\n\nKeep practicing, je kunt het! 💪"
        alert("🇳🇱 Practice — Results", summary)


if __name__ == "__main__":
    main()
