#!/usr/bin/env python3
"""
Dutch Verb Trainer — Practice Conjugations
Drills irregular and regular verbs with past tense, participles, and auxiliaries.
"""

import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
VERBS_FILE = SCRIPT_DIR / "verbs.json"


def load_verbs() -> list[dict]:
    if not VERBS_FILE.exists():
        alert("Verb Trainer — Error", f"Verbs file not found:\n{VERBS_FILE}")
        sys.exit(1)
    try:
        with open(VERBS_FILE, "r", encoding="utf-8") as f:
            verbs = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        alert("Verb Trainer — Error", f"Failed to read verbs file:\n{exc}")
        sys.exit(1)
    if not verbs:
        alert("Verb Trainer — Error", "Verbs file is empty.")
        sys.exit(1)
    return verbs


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


def quiz_prompt(prompt_msg: str) -> Tuple[str, str]:
    applescript = (
        f'display dialog "{_escape(prompt_msg)}" '
        f'default answer "" '
        f'with title "🇳🇱 Verb Trainer" '
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
    applescript_all = (
        'display alert "🇳🇱 Verb Trainer" '
        'message "What level do you want to practice?" '
        'as informational '
        'buttons {"All levels", "Pick a level"} '
        'default button "Pick a level"'
    )
    applescript_pick = (
        'display dialog "Choose a difficulty level:" '
        'with title "🇳🇱 Verb Trainer" '
        'buttons {"A1", "A2", "B1"} '
        'default button "A2"'
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


def pick_form() -> Optional[str]:
    """Show a form picker dialog. Returns 'Past', 'Participle', 'All', or None on cancel."""
    applescript = (
        'display dialog "What do you want to practice?" '
        'with title "🇳🇱 Verb Trainer" '
        'buttons {"Past tense", "Participle", "Both"} '
        'default button "Both"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        if "Past" in output:
            return "Past"
        elif "Participle" in output:
            return "Participle"
        else:
            return "Both"
    except subprocess.CalledProcessError:
        return None


def filter_by_level(verbs: list[dict], level: str) -> list[dict]:
    if level == "All":
        return verbs
    return [v for v in verbs if v.get("level") == level]


def ask_verb(verb: dict, form_type: str, question_num: int, total: int) -> Optional[bool]:
    """
    Ask a conjugation question. Returns:
      True  = correct
      False = wrong or "I don't know"
      None  = user wants to stop
    """
    infinitive = verb["infinitive"]
    english = verb["meaning"]
    example = verb.get("example", "")
    level_tag = f"  [{verb.get('level', '')}]" if verb.get("level") else ""

    if form_type == "Past":
        correct_answer = verb["past_singular"].lower()
        prompt_text = (
            f"Question {question_num} / {total}\n\n"
            f"Past tense (ik):\n\n\"{english}\"\n\n"
            f"Infinitive: {infinitive}\n\n"
            f"What is the past singular?"
        )
    else:
        correct_answer = verb["participle"].lower()
        prompt_text = (
            f"Question {question_num} / {total}\n\n"
            f"Participle (past):\n\n\"{english}\"\n\n"
            f"Infinitive: {infinitive}\n\n"
            f"What is the past participle?"
        )

    attempt = 0
    while True:
        button, answer = quiz_prompt(prompt_text)

        if button in ("cancel", "Stop"):
            return None

        if button == "I don't know":
            if form_type == "Past":
                reveal = f"Past: {verb['past_singular']}"
            else:
                reveal = f"Participle: {verb['participle']}\nAuxiliary: {verb['auxiliary']}"
            if example:
                reveal += f"\n\nExample:\n{example}"
            alert("🇳🇱 Here's the answer!", reveal)
            return False

        if answer == correct_answer:
            if form_type == "Past":
                msg = f"✅  {verb['infinitive']} → {verb['past_singular']}"
            else:
                msg = f"✅  {verb['infinitive']} → {verb['participle']} ({verb['auxiliary']})"
            if example:
                msg += f"\n\nExample:\n{example}"
            alert("🇳🇱 Correct!", msg)
            return True

        attempt += 1
        if attempt >= 2:
            if form_type == "Past":
                hint = verb["past_singular"][:len(verb["past_singular"]) // 2] + "..."
                prompt_text = f"❌ Not quite. Hint: \"{hint}\"\n\nTry again!"
            else:
                hint = verb["participle"][:len(verb["participle"]) // 2] + "..."
                prompt_text = f"❌ Not quite. Hint: \"{hint}\"\n\nTry again!"
        else:
            prompt_text = f"❌ Not quite, try again!"


def main() -> None:
    all_verbs = load_verbs()

    level = pick_level()
    if level is None:
        return

    verbs = filter_by_level(all_verbs, level)
    if not verbs:
        alert("🇳🇱 Verb Trainer", f"No verbs found for level {level}.")
        return

    form = pick_form()
    if form is None:
        return

    level_label = level if level != "All" else "All levels"
    alert("🇳🇱 Verb Trainer", f"Level: {level_label}\nForm: {form}\nVerbs: {len(verbs)}\n\nLet's go!")

    queue = random.sample(verbs, len(verbs))
    retry_queue: list[Tuple[dict, str]] = []

    correct = 0
    wrong = 0
    total = 0

    while queue or retry_queue:
        if not queue:
            if not retry_queue:
                break
            random.shuffle(retry_queue)
            queue = [v[0] for v in retry_queue]
            retry_queue = []
            alert(
                "🇳🇱 Review Round",
                f"You have {len(queue)} verbs to review.\nLet's go again!",
            )

        verb = queue.pop(0)
        total += 1

        if form == "Both":
            form_to_ask = random.choice(["Past", "Participle"])
        else:
            form_to_ask = form

        result = ask_verb(verb, form_to_ask, total, len(verbs))

        if result is None:
            total -= 1
            break

        if result:
            correct += 1
        else:
            wrong += 1
            retry_queue.append((verb, form_to_ask))

    if total == 0:
        alert("🇳🇱 Verb Trainer", "No verbs practiced. Tot de volgende keer!")
    else:
        pct = round(correct / total * 100)
        summary = (
            f"Verbs practiced:  {total}\n"
            f"Correct:  {correct}\n"
            f"Wrong:  {wrong}\n"
            f"Score:  {pct}%"
        )
        if pct == 100:
            summary += "\n\nPerfect! Ongelofelijk! 🎉"
        elif pct >= 70:
            summary += "\n\nGoed gedaan! Keep it up!"
        else:
            summary += "\n\nKeep practicing, je kunt het! 💪"
        alert("🇳🇱 Verb Trainer — Results", summary)


if __name__ == "__main__":
    main()
