# Dutch Word of the Day

A simple macOS app that sends you a native notification with a random Dutch vocabulary word every day at 9:00 AM.

---

## Files

| File | Purpose |
|---|---|
| `dutch_word.py` | Main script — picks a word and sends the notification |
| `vocabulary.json` | 100 Dutch words with English translations and example sentences |
| `com.nadia.dutchword.plist` | launchd config for daily scheduling |
| `install.sh` | One-command installer — sets up everything automatically |
| `.word_history.json` | Auto-generated — tracks shown words to avoid repeats |

---

## Quick Start

### 1. Test it right now

```bash
cd "/Users/notte1/Documents/NADIA/DUTCH APP"
python3 dutch_word.py
```

You should see a macOS notification pop up with a Dutch word.

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

That's it — you'll get a notification every day at **9:00 AM**.

### 3. Change the notification time

Edit the plist (or the copy in `~/Library/LaunchAgents/`). Find the `StartCalendarInterval` section and change the `Hour` and `Minute` values:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>    <!-- 0-23, 24-hour format -->
    <key>Minute</key>
    <integer>0</integer>    <!-- 0-59 -->
</dict>
```

After editing, reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.nadia.dutchword.plist
launchctl load   ~/Library/LaunchAgents/com.nadia.dutchword.plist
```

---

## Managing the Schedule

| Action | Command |
|---|---|
| **Enable** | `launchctl load ~/Library/LaunchAgents/com.nadia.dutchword.plist` |
| **Disable** | `launchctl unload ~/Library/LaunchAgents/com.nadia.dutchword.plist` |
| **Run now** | `launchctl start com.nadia.dutchword` |
| **Check status** | `launchctl list | grep dutchword` |
| **View logs** | `cat /tmp/dutchword.log` |
| **View errors** | `cat /tmp/dutchword.err` |

---

## Adding Your Own Words

Edit `vocabulary.json`. Each entry has three fields:

```json
{"dutch": "huis", "english": "house", "example": "Ik woon in een groot huis."}
```

The script will automatically cycle through all words before repeating any.

---

## Dependencies

**None.** The script uses only the Python standard library and macOS's built-in `osascript`. No `pip install` required.

---

## Troubleshooting

- **No notification appears?** Open System Settings → Notifications → Script Editor and make sure notifications are allowed.
- **Wrong Python path?** If you use a different Python (e.g. Homebrew), update the path in the plist: run `which python3` and replace `/usr/bin/python3` in the plist.
- **Missed notification?** If your Mac was asleep at 9 AM, launchd will fire the notification shortly after waking.
