#!/usr/bin/env python3
"""
Dutch Vocabulary Test — 10 Questions
Pick a level, answer 10 words, each word appears only once.
At the end you see your score and which ones you got wrong.
"""

import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
VOCAB_FILE = SCRIPT_DIR / "vocabulary.json"
TEST_SIZE = 10


def load_vocabulary() -> list[dict]:
    if not VOCAB_FILE.exists():
        alert("Test — Error", f"Vocabulary file not found:\n{VOCAB_FILE}")
        sys.exit(1)
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            words = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        alert("Test — Error", f"Failed to read vocabulary file:\n{exc}")
        sys.exit(1)
    if not words:
        alert("Test — Error", "Vocabulary file is empty.")
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


def test_prompt(prompt_msg: str) -> tuple[str, str]:
    applescript = (
        f'display dialog "{_escape(prompt_msg)}" '
        f'default answer "" '
        f'with title "🇳🇱 Dutch Test" '
        f'buttons {{"Quit", "I don\'t know", "Submit"}} '
        f'default button "Submit"'
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
    applescript_all = (
        'display alert "🇳🇱 Dutch Test" '
        'message "What level do you want to be tested on?" '
        'as informational '
        'buttons {"All levels", "Pick a level"} '
        'default button "Pick a level"'
    )
    applescript_pick = (
        'display dialog "Choose a difficulty level:" '
        'with title "🇳🇱 Dutch Test" '
        'buttons {"A1", "A2", "B1"} '
        'default button "B1"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript_all],
            check=True, capture_output=True, text=True,
        )
        if "All levels" in result.stdout:
            return "All"

        result = subprocess.run(
            ["osascript", "-e", applescript_pick],
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


def ask_word(word: dict, question_num: int) -> Optional[bool]:
    """
    Ask a single test question. Returns:
      True  = correct
      False = wrong or "I don't know"
      None  = user wants to quit
    """
    dutch = word["dutch"].lower()
    english = word["english"]

    label = f"Question {question_num} / {TEST_SIZE}\n\nTranslate to Dutch:\n\n\"{english}\""

    button, answer = test_prompt(label)

    if button in ("cancel", "Quit"):
        return None

    if button == "I don't know":
        alert(
            f"❌  Question {question_num}",
            f"The answer was:  {word['dutch']}\n\nExample:\n{word.get('example', '')}",
        )
        return False

    if answer == dutch:
        alert(f"✅  Question {question_num}", f"Correct!  {word['dutch']}  =  {english}")
        return True

    alert(
        f"❌  Question {question_num}",
        f"Wrong!\n\nYour answer:  {answer}\nCorrect answer:  {word['dutch']}\n\nExample:\n{word.get('example', '')}",
    )
    return False


def main() -> None:
    all_words = load_vocabulary()

    level = pick_level()
    if level is None:
        return

    words = filter_by_level(all_words, level)
    if not words:
        alert("🇳🇱 Test", f"No words found for level {level}.")
        return

    if len(words) < TEST_SIZE:
        alert(
            "🇳🇱 Test",
            f"Only {len(words)} words available for level {level}.\nNeed at least {TEST_SIZE}.",
        )
        return

    level_label = level if level != "All" else "All levels"
    alert("🇳🇱 Test", f"Level: {level_label}\nQuestions: {TEST_SIZE}\n\nGood luck! 🍀")

    test_words = random.sample(words, TEST_SIZE)

    correct = 0
    wrong = 0
    mistakes: list[dict] = []

    for i, word in enumerate(test_words, start=1):
        result = ask_word(word, i)

        if result is None:
            break

        if result:
            correct += 1
        else:
            wrong += 1
            mistakes.append(word)

    answered = correct + wrong
    if answered == 0:
        alert("🇳🇱 Test", "No questions answered. Tot de volgende keer!")
        return

    pct = round(correct / answered * 100)
    summary = (
        f"Score:  {correct} / {answered}  ({pct}%)\n"
        f"Correct:  {correct}\n"
        f"Wrong:  {wrong}"
    )

    if mistakes:
        summary += "\n\n— Mistakes —\n"
        for w in mistakes:
            summary += f"  {w['english']}  →  {w['dutch']}\n"

    if pct == 100:
        summary += "\nPerfect score! Uitstekend! 🎉"
    elif pct >= 70:
        summary += "\nGoed gedaan! Keep it up!"
    elif pct >= 50:
        summary += "\nNiet slecht, maar blijf oefenen! 💪"
    else:
        summary += "\nKeep studying, je kunt het! 💪"

    alert("🇳🇱 Test — Results", summary)


if __name__ == "__main__":
    main()
