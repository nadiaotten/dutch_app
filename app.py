#!/usr/bin/env python3
"""
Dutch Learning App — Main Menu
Central launcher for all learning modes: Daily, Study, Practice, Test, and Verb Training.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent


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


def choose_mode() -> Optional[str]:
    """Show mode picker dialog. Returns mode name or None on cancel."""
    applescript = (
        'display dialog "Choose a learning mode:" '
        'with title "🇳🇱 Dutch Trainer" '
        'buttons {"Daily", "Study", "Practice", "Test", "Verbs"} '
        'default button "Practice"'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            check=True, capture_output=True, text=True,
        )
        output = result.stdout.strip()
        if "Daily" in output:
            return "daily"
        elif "Study" in output:
            return "study"
        elif "Practice" in output:
            return "practice"
        elif "Test" in output:
            return "test"
        elif "Verbs" in output:
            return "verb"
    except subprocess.CalledProcessError:
        pass
    return None


def run_script(script_name: str) -> None:
    """Run a Python script in the same directory."""
    script_path = SCRIPT_DIR / f"{script_name}.py"
    if not script_path.exists():
        alert("Error", f"Script not found: {script_path}")
        return
    try:
        subprocess.run([sys.executable, str(script_path)], check=False)
    except Exception as exc:
        alert("Error", f"Failed to run {script_name}:\n{exc}")


def main() -> None:
    mode = choose_mode()
    if mode is None:
        return

    script_map = {
        "daily": "dutch_word",
        "study": "study",
        "practice": "practice",
        "test": "test",
        "verb": "verb",
    }

    script = script_map.get(mode)
    if script:
        run_script(script)


if __name__ == "__main__":
    main()
