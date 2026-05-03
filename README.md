# Dutch Word of the Day

A macOS app to learn Dutch vocabulary through daily quizzes, flashcards, and free practice sessions.

---

## Files

| File | Purpose |
|---|---|
| `dutch_word.py` | Daily quiz — runs automatically 3x/day via launchd |
| `practice.py` | Free practice — type Dutch translations, on demand |
| `study.py` | Flashcards — see English, think of Dutch, flip to check |
| `vocabulary.json` | 206 Dutch words with translations, examples, and difficulty levels (A1/A2/B1) |
| `com.nadia.dutchword.plist` | launchd config for automatic scheduling |
| `install.sh` | One-command installer |
| `.word_history.json` | Auto-generated — tracks shown words to avoid repeats |
| `.word_today.json` | Auto-generated — stores today's quiz word |

---

## Three Modes

### 1. Daily Quiz (`dutch_word.py`) — automatic

Runs automatically at **9:00 AM**, **3:00 PM**, and **5:00 PM**. Shows an English word and asks you to type the Dutch translation.

- **Correct answer** → next run gives a new word
- **Wrong / I don't know** → same word comes back at the next scheduled time
- **Later** → dismisses the quiz and retries in 30 minutes
- The word's difficulty level (A1/A2/B1) is shown in the prompt

```bash
python3 "/Users/notte1/Documents/NADIA/DUTCH APP/dutch_word.py"
```

### 2. Practice (`practice.py`) — on demand

Continuous quiz session. Words you get wrong come back until you get them right. Starts with a level picker: A1, A2, B1, or All.

```bash
python3 "/Users/notte1/Documents/NADIA/DUTCH APP/practice.py"
```

### 3. Study (`study.py`) — on demand

Flashcard mode. See the English word, think of the Dutch translation, press Flip to check. Cards you don't know cycle back. Starts with a level picker.

```bash
python3 "/Users/notte1/Documents/NADIA/DUTCH APP/study.py"
```

---

## Quick Start

### 1. Test it right now

```bash
python3 "/Users/notte1/Documents/NADIA/DUTCH APP/dutch_word.py"
```

### 2. Install the daily schedule

**Option A — one command:**

```bash
bash "/Users/notte1/Documents/NADIA/DUTCH APP/install.sh"
```

**Option B — manual steps:**

```bash
cp "/Users/notte1/Documents/NADIA/DUTCH APP/com.nadia.dutchword.plist" \
   ~/Library/LaunchAgents/com.nadia.dutchword.plist

launchctl load ~/Library/LaunchAgents/com.nadia.dutchword.plist
```

### 3. Change the notification times

Edit the plist (or the copy in `~/Library/LaunchAgents/`). The `StartCalendarInterval` array contains one entry per scheduled time (Hour is 0-23):

After editing, reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.nadia.dutchword.plist
launchctl load   ~/Library/LaunchAgents/com.nadia.dutchword.plist
```

---

## Difficulty Levels

Every word in `vocabulary.json` has a `"level"` field:

| Level | Count | Description |
|---|---|---|
| **A1** | 49 | Basics — huis, boek, goed, eten, dank je wel... |
| **A2** | 93 | Everyday — fietsen, beginnen, winkel, samen... |
| **B1** | 64 | Advanced — voorbereiden, uitzoeken, vertrouwen, gezellig... |

In **practice** and **study** mode, you choose your level before starting. The **daily quiz** picks from all levels and shows the level tag in the prompt.

---

## Managing the Schedule

| Action | Command |
|---|---|
| **Enable** | `launchctl load ~/Library/LaunchAgents/com.nadia.dutchword.plist` |
| **Disable** | `launchctl unload ~/Library/LaunchAgents/com.nadia.dutchword.plist` |
| **Run now** | `launchctl start com.nadia.dutchword` |
| **Check status** | `launchctl list \| grep dutchword` |
| **View logs** | `cat /tmp/dutchword.log` |
| **View errors** | `cat /tmp/dutchword.err` |

---

## Adding Your Own Words

Edit `vocabulary.json`. Each entry has four fields:

```json
{"dutch": "huis", "english": "house", "example": "Ik woon in een groot huis.", "level": "A1"}
```

The script will automatically cycle through all words before repeating any.

---

## Dependencies

**None.** Uses only the Python standard library and macOS's built-in `osascript`. No `pip install` required.

---

## Troubleshooting

- **No dialog appears?** Open System Settings → Notifications → Script Editor and make sure notifications are allowed.
- **Wrong Python path?** Run `which python3` and update the path in the plist if it differs from `/usr/bin/python3`.
- **Missed quiz?** If your Mac was asleep at the scheduled time, launchd fires the quiz shortly after waking.
