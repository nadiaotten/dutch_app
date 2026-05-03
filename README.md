# Dutch Word

A Dutch vocabulary trainer with three modes:

- `Daily` for one persistent word per day
- `Practice` for typed translation drills
- `Study` for flashcards and review rounds

This repo now includes:

- a static web app / PWA you can deploy from GitHub and use on your phone
- the original macOS Python scripts, kept for the desktop workflow

## Web App

The new web version is a static app built from:

| File | Purpose |
|---|---|
| `index.html` | App shell and mobile-friendly layout |
| `styles.css` | Responsive styling |
| `app.js` | Daily, practice, and study logic in the browser |
| `manifest.webmanifest` | Installable PWA metadata |
| `sw.js` | Service worker for offline caching |
| `assets/` | App icons |
| `.github/workflows/deploy-pages.yml` | GitHub Pages deployment workflow |
| `vocabulary.json` | Shared vocabulary source for both web and Python versions |

### What the web app keeps

- **Daily mode** keeps one active word until you answer it correctly
- **Practice mode** repeats missed words until you get them right
- **Study mode** sends "Not yet" cards into a review round
- **Progress is saved locally** in your browser using `localStorage`
- **The app can be installed** to your phone home screen

### Web app limitation

The original Mac version used `launchd` to force scheduled popups. The GitHub Pages version cannot guarantee background alerts while the app is closed.

In the web version:

- the daily word is still persistent
- the `Later` action still snoozes the quiz
- reminders work best when the app is installed and opened regularly

If you later want true scheduled push notifications while the app is closed, that will require a backend service.

## Deploy To GitHub Pages

### 1. Push the repo to GitHub

Commit your changes and push this repository to GitHub.

### 2. Enable Pages

In your GitHub repository:

1. Open `Settings`
2. Open `Pages`
3. Under `Build and deployment`, use **GitHub Actions**

The workflow in `.github/workflows/deploy-pages.yml` will publish the static app when you push to `main` or `master`.

### 3. Open the deployed app

After the workflow succeeds, your app will be available at:

`https://<your-github-username>.github.io/<your-repo-name>/`

## Use It On Your Phone

### iPhone / iPad

1. Open the GitHub Pages URL in Safari
2. Tap `Share`
3. Tap `Add to Home Screen`

### Android

1. Open the GitHub Pages URL in Chrome
2. Open the browser menu
3. Tap `Install app` or `Add to Home Screen`

Once installed, it behaves more like a normal app and can store your daily state locally on that device.

## Local Preview

Because the app loads `vocabulary.json` and uses a service worker, preview it from a local web server instead of opening `index.html` directly from Finder.

Example:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Learning Modes

### 1. Daily

Shows one English word and asks for the Dutch translation.

- **Correct**: clears today's word and picks a new one next time
- **Wrong**: lets you retry, then shows a hint after repeated misses
- **I don't know**: reveals the answer and example
- **Later**: snoozes the quiz for 30 minutes in the browser

### 2. Practice

Continuous typing practice with a level picker: `A1`, `A2`, `B1`, or `All`.

- wrong answers come back later in the same session
- the session ends with a score summary

### 3. Study

Flashcards with the same level picker.

- press `Flip` to reveal the answer
- choose `Got it` or `Not yet`
- cards marked `Not yet` come back in a review round

## Difficulty Levels

Every word in `vocabulary.json` has a `level` field:

| Level | Count | Description |
|---|---|---|
| **A1** | 49 | Basics |
| **A2** | 93 | Everyday vocabulary |
| **B1** | 64 | More advanced vocabulary |

## Add Your Own Words

Edit `vocabulary.json`. Each item looks like this:

```json
{"dutch": "huis", "english": "house", "example": "Ik woon in een groot huis.", "level": "A1"}
```

Required fields:

- `dutch`
- `english`
- `example`
- `level`

## Legacy macOS Version

The original desktop scripts are still in the repo:

| File | Purpose |
|---|---|
| `dutch_word.py` | Daily quiz with macOS dialogs |
| `practice.py` | On-demand typing drills |
| `study.py` | On-demand flashcards |
| `com.nadia.dutchword.plist` | `launchd` schedule |
| `install.sh` | Installs the Mac schedule |
| `.word_history.json` | Auto-generated rotation history |
| `.word_today.json` | Auto-generated daily word state |

### Run the macOS scripts manually

```bash
python3 dutch_word.py
python3 practice.py
python3 study.py
```

### Install the macOS daily schedule

```bash
bash install.sh
```

## Dependencies

### Web app

No build step is required for deployment. It is a plain static site.

### macOS scripts

No external Python packages are required. The scripts use the Python standard library and macOS `osascript`.
