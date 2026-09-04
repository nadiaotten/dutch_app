#!/usr/bin/env python3
"""
Dutch Flashcards — Study Mode
See the Dutch word, try to recall the English meaning, then flip the card to check.
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
        alert("Study — Error", f"Vocabulary file not found:\n{VOCAB_FILE}")
        sys.exit(1)
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            words = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        alert("Study — Error", f"Failed to read vocabulary file:\n{exc}")
        sys.exit(1)
    if not words:
        alert("Study — Error", "Vocabulary file is empty.")
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


def pick_level() -> Optional[str]:
    """Show a level picker dialog. Returns 'A1', 'A2', 'B1', 'All', or None on cancel."""
    applescript_all = (
        'display alert "🇳🇱 Dutch Study" '
        'message "What level do you want to study?" '
        'as informational '
        'buttons {"All levels", "Pick a level"} '
        'default button "Pick a level"'
    )
    applescript_pick = (
        'display dialog "Choose a difficulty level:" '
        'with title "🇳🇱 Dutch Study" '
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


def show_front(word: dict, card_num: int, total: int) -> str:
    """Show the Dutch word. Returns button clicked: 'Flip', 'Stop', or 'cancel'."""
    prompt = (
        f"Card {card_num} / {total}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🇳🇱  {word['dutch']}\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        f"What does this mean?\n\n"
        f"Think about it, then press Flip."
    )
    applescript = (
        f'display alert "🇳🇱 Flashcard" '
        f'message "{_escape(prompt)}" '
        f'as informational '
        f'buttons {{"Stop", "Flip"}} '
        f'default button "Flip"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        if "Flip" in output:
            return "Flip"
        return "Stop"
    except subprocess.CalledProcessError:
        return "cancel"


def show_back(word: dict) -> str:
    """Show the answer. Returns 'Got it', 'Not yet', or 'cancel'."""
    answer = (
        f"━━━━━━━━━━━━━━━━━\n"
        f"🇳🇱 {word['dutch']}\n"
        f"🇬🇧 {word['english']}\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Example:\n{word.get('example', '')}\n\n"
        f"Did you know it?"
    )
    applescript = (
        f'display alert "🇳🇱 Answer" '
        f'message "{_escape(answer)}" '
        f'as informational '
        f'buttons {{"Not yet", "Got it"}} '
        f'default button "Got it"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        if "Got it" in output:
            return "Got it"
        return "Not yet"
    except subprocess.CalledProcessError:
        return "cancel"


def main() -> None:
    all_words = load_vocabulary()

    level = pick_level()
    if level is None:
        return

    words = filter_by_level(all_words, level)
    if not words:
        alert("🇳🇱 Study", f"No words found for level {level}.")
        return

    level_label = level if level != "All" else "All levels"
    alert("🇳🇱 Study", f"Level: {level_label}\nCards: {len(words)}\n\nLet's go!")

    deck = random.sample(words, len(words))
    review_pile: list[dict] = []

    known = 0
    review = 0
    total = 0
    deck_size = len(deck)

    while deck or review_pile:
        if not deck:
            random.shuffle(review_pile)
            deck = review_pile
            review_pile = []
            deck_size = len(deck)
            alert(
                "🇳🇱 Review Round",
                f"You have {deck_size} cards to review.\nLet's go again!",
            )

        word = deck.pop(0)
        total += 1

        front = show_front(word, total, deck_size)
        if front in ("Stop", "cancel"):
            total -= 1
            break

        back = show_back(word)
        if back == "cancel":
            total -= 1
            break

        if back == "Got it":
            known += 1
        else:
            review += 1
            review_pile.append(word)

    if total == 0:
        alert("🇳🇱 Study", "No cards studied. Tot de volgende keer!")
    else:
        pct = round(known / total * 100)
        summary = (
            f"Cards studied:  {total}\n"
            f"Known:  {known}\n"
            f"Need review:  {review}\n"
            f"Score:  {pct}%"
        )
        if pct == 100:
            summary += "\n\nPerfect recall! Geweldig! 🎉"
        elif pct >= 70:
            summary += "\n\nGoed bezig! You're getting there!"
        else:
            summary += "\n\nKeep studying, oefening baart kunst! 💪"
        alert("🇳🇱 Study — Results", summary)


if __name__ == "__main__":
    main()
