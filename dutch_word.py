#!/usr/bin/env python3
"""
Dutch Word of the Day — Quiz Mode
Shows an English word and asks you to type the Dutch translation.
"""

import json
import os
import random
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VOCAB_FILE = SCRIPT_DIR / "vocabulary.json"
HISTORY_FILE = SCRIPT_DIR / ".word_history.json"
TODAY_FILE = SCRIPT_DIR / ".word_today.json"


def load_vocabulary() -> list[dict]:
    if not VOCAB_FILE.exists():
        alert("Dutch Word — Error", f"Vocabulary file not found:\n{VOCAB_FILE}")
        sys.exit(1)

    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            words = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        alert("Dutch Word — Error", f"Failed to read vocabulary file:\n{exc}")
        sys.exit(1)

    if not words:
        alert("Dutch Word — Error", "Vocabulary file is empty.")
        sys.exit(1)

    return words


def load_history() -> list[str]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list[str]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
    except IOError:
        pass


def load_today() -> dict | None:
    if not TODAY_FILE.exists():
        return None
    try:
        with open(TODAY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == str(date.today()):
            return data.get("word")
    except (json.JSONDecodeError, IOError, KeyError):
        pass
    return None


def save_today(word: dict) -> None:
    try:
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            json.dump({"date": str(date.today()), "word": word}, f, ensure_ascii=False)
    except IOError:
        pass


def pick_word(words: list[dict]) -> dict:
    history = load_history()
    unseen = [w for w in words if w["dutch"] not in history]

    if not unseen:
        history.clear()
        unseen = words

    choice = random.choice(unseen)
    history.append(choice["dutch"])

    max_history = len(words)
    if len(history) > max_history:
        history = history[-max_history:]

    save_history(history)
    return choice


def get_word_of_the_day(words: list[dict]) -> tuple[dict, bool]:
    existing = load_today()
    if existing:
        return existing, True

    word = pick_word(words)
    save_today(word)
    return word, False


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


def quiz_prompt(english: str, prompt_msg: str) -> tuple[str, str]:
    """
    Show a dialog with a text field. Returns (button_clicked, text_entered).
    Buttons: 'Check' and 'I don\\'t know'.
    """
    applescript = (
        f'display dialog "{_escape(prompt_msg)}" '
        f'default answer "" '
        f'with title "🇳🇱 Dutch Quiz" '
        f'buttons {{"Later", "I don\'t know", "Check"}} '
        f'default button "Check"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        # osascript returns: "button returned:Check, text returned:stoel"
        button = ""
        text = ""
        for part in output.split(", "):
            if part.startswith("button returned:"):
                button = part.split(":", 1)[1]
            elif part.startswith("text returned:"):
                text = part.split(":", 1)[1]
        return button, text.strip().lower()
    except subprocess.CalledProcessError:
        # User closed the dialog (pressed Escape or Cmd-.)
        return "cancel", ""
    except FileNotFoundError:
        print("osascript not found", file=sys.stderr)
        sys.exit(1)


def clear_today() -> None:
    try:
        TODAY_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def run_quiz(word: dict, is_reminder: bool) -> None:
    dutch = word["dutch"].lower()
    english = word["english"]
    example = word.get("example", "")

    if is_reminder:
        label = f"⏰ Reminder! Translate to Dutch:\n\n\"{english}\""
    else:
        label = f"Translate to Dutch:\n\n\"{english}\""

    attempt = 0
    while True:
        button, answer = quiz_prompt(english, label)

        if button == "cancel":
            return

        if button == "Later":
            schedule_retry()
            return

        if button == "I don't know":
            reveal = f"The answer is:  {word['dutch']}"
            if example:
                reveal += f"\n\nExample:\n{example}"
            alert("🇳🇱 Don't worry, now you know!", reveal)
            return

        # button == "Check"
        if answer == dutch:
            msg = f"✅  {word['dutch']}  =  {english}"
            if example:
                msg += f"\n\nExample:\n{example}"
            alert("🇳🇱 Correct! Goed gedaan!", msg)
            clear_today()
            return

        attempt += 1
        if attempt >= 3:
            hint = dutch[:len(dutch) // 2] + "..."
            label = (
                f"❌ Not quite. Here is a hint:  \"{hint}\"\n\n"
                f"Translate to Dutch:\n\n\"{english}\""
            )
        else:
            label = (
                f"❌ Not quite, try again!\n\n"
                f"Translate to Dutch:\n\n\"{english}\""
            )


RETRY_DELAY_MINUTES = 30


def schedule_retry() -> None:
    """Fork a background process that waits, then re-launches the quiz."""
    script = str(SCRIPT_DIR / "dutch_word.py")
    python = sys.executable
    pid = os.fork()
    if pid == 0:
        os.setsid()
        time.sleep(RETRY_DELAY_MINUTES * 60)
        os.execvp(python, [python, script])


def main() -> None:
    words = load_vocabulary()
    word, is_reminder = get_word_of_the_day(words)
    run_quiz(word, is_reminder)


if __name__ == "__main__":
    main()
