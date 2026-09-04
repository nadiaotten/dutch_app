const STORAGE_KEYS = {
  history: "dutchWord.history",
  today: "dutchWord.today",
  snoozeUntil: "dutchWord.snoozeUntil",
  lastReminder: "dutchWord.lastReminder",
};

const DAILY_SNOOZE_MS = 30 * 60 * 1000;

const state = {
  words: [],
  verbs: [],
  ready: false,
  installPrompt: null,
  dailyAttempts: 0,
  dailyTimerId: null,
  practiceLevel: "All",
  practiceSession: null,
  studyLevel: "All",
  studySession: null,
  verbsLevel: "All",
  verbsForm: "Both",
  verbsSession: null,
};

const els = {
  appStatus: document.querySelector("#app-status"),
  installButton: document.querySelector("#install-button"),
  notificationsButton: document.querySelector("#notifications-button"),
  tabButtons: [...document.querySelectorAll(".tab-button")],
  panels: {
    daily: document.querySelector("#daily-panel"),
    practice: document.querySelector("#practice-panel"),
    study: document.querySelector("#study-panel"),
    verbs: document.querySelector("#verbs-panel"),
  },
  daily: {
    state: document.querySelector("#daily-state"),
    questionWrap: document.querySelector("#daily-question-wrap"),
    question: document.querySelector("#daily-question"),
    answer: document.querySelector("#daily-answer"),
    check: document.querySelector("#daily-check"),
    idk: document.querySelector("#daily-idk"),
    later: document.querySelector("#daily-later"),
    result: document.querySelector("#daily-result"),
    levelChip: document.querySelector("#daily-level-chip"),
  },
  practice: {
    levelButtons: [...document.querySelectorAll("[data-practice-level]")],
    start: document.querySelector("#practice-start"),
    card: document.querySelector("#practice-card"),
    question: document.querySelector("#practice-question"),
    answer: document.querySelector("#practice-answer"),
    check: document.querySelector("#practice-check"),
    idk: document.querySelector("#practice-idk"),
    stop: document.querySelector("#practice-stop"),
    feedback: document.querySelector("#practice-feedback"),
    progress: document.querySelector("#practice-progress"),
    score: document.querySelector("#practice-score"),
    summary: document.querySelector("#practice-summary"),
    summaryCopy: document.querySelector("#practice-summary-copy"),
    restart: document.querySelector("#practice-restart"),
  },
  study: {
    levelButtons: [...document.querySelectorAll("[data-study-level]")],
    start: document.querySelector("#study-start"),
    card: document.querySelector("#study-card"),
    progress: document.querySelector("#study-progress"),
    score: document.querySelector("#study-score"),
    front: document.querySelector("#study-front"),
    word: document.querySelector(".study-word"),
    back: document.querySelector("#study-back"),
    answer: document.querySelector("#study-answer"),
    example: document.querySelector("#study-example"),
    frontActions: document.querySelector("#study-front-actions"),
    backActions: document.querySelector("#study-back-actions"),
    flip: document.querySelector("#study-flip"),
    gotIt: document.querySelector("#study-got-it"),
    notYet: document.querySelector("#study-not-yet"),
    stopFront: document.querySelector("#study-stop-front"),
    stopBack: document.querySelector("#study-stop-back"),
    feedback: document.querySelector("#study-feedback"),
    summary: document.querySelector("#study-summary"),
    summaryCopy: document.querySelector("#study-summary-copy"),
    restart: document.querySelector("#study-restart"),
  },
  verbs: {
    levelButtons: [...document.querySelectorAll("[data-verbs-level]")],
    formRadios: [...document.querySelectorAll("input[name='verb-form']")],
    start: document.querySelector("#verbs-start"),
    card: document.querySelector("#verbs-card"),
    label: document.querySelector("#verbs-label"),
    progress: document.querySelector("#verbs-progress"),
    score: document.querySelector("#verbs-score"),
    question: document.querySelector("#verbs-question"),
    answer: document.querySelector("#verbs-answer"),
    check: document.querySelector("#verbs-check"),
    idk: document.querySelector("#verbs-idk"),
    stop: document.querySelector("#verbs-stop"),
    feedback: document.querySelector("#verbs-feedback"),
    summary: document.querySelector("#verbs-summary"),
    summaryCopy: document.querySelector("#verbs-summary-copy"),
    restart: document.querySelector("#verbs-restart"),
  },
};

function readStore(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeStore(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}

function removeStore(key) {
  window.localStorage.removeItem(key);
}

function todayIsoString() {
  return new Date().toISOString().slice(0, 10);
}

function normalizeAnswer(value) {
  return value.trim().toLowerCase().replace(/\s+/g, " ");
}

function sample(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function shuffle(array) {
  const copy = [...array];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy;
}

function setStatus(message) {
  els.appStatus.textContent = message;
}

function showMessage(element, tone, html) {
  element.classList.remove("hidden", "success", "warning", "danger");
  element.classList.add(tone);
  element.innerHTML = html;
}

function hideMessage(element) {
  element.classList.add("hidden");
  element.classList.remove("success", "warning", "danger");
  element.innerHTML = "";
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

function vocabularyForLevel(level) {
  if (level === "All") {
    return state.words;
  }
  return state.words.filter((word) => word.level === level);
}

function verbsForLevel(level) {
  if (level === "All") {
    return state.verbs;
  }
  return state.verbs.filter((verb) => verb.level === level);
}

function setSelectedLevel(buttons, key, value) {
  buttons.forEach((button) => {
    const selected = button.dataset[key] === value;
    button.classList.toggle("is-selected", selected);
  });
}

function getTodayRecord() {
  const saved = readStore(STORAGE_KEYS.today, null);
  if (saved && saved.date === todayIsoString()) {
    return saved;
  }
  return null;
}

function pickDailyWord() {
  let history = readStore(STORAGE_KEYS.history, []);
  let unseen = state.words.filter((word) => !history.includes(word.dutch));

  if (!unseen.length) {
    history = [];
    unseen = state.words;
  }

  const chosen = sample(unseen);
  history.push(chosen.dutch);

  if (history.length > state.words.length) {
    history = history.slice(-state.words.length);
  }

  writeStore(STORAGE_KEYS.history, history);
  return chosen;
}

function getDailyWord() {
  const existing = getTodayRecord();
  if (existing) {
    return { word: existing.word, isReminder: true };
  }

  const word = pickDailyWord();
  writeStore(STORAGE_KEYS.today, { date: todayIsoString(), word });
  return { word, isReminder: false };
}

function clearDailyWord() {
  removeStore(STORAGE_KEYS.today);
  removeStore(STORAGE_KEYS.snoozeUntil);
  state.dailyAttempts = 0;
}

function currentSnoozeUntil() {
  const value = readStore(STORAGE_KEYS.snoozeUntil, null);
  return typeof value === "number" ? value : null;
}

function clearDailyTimer() {
  if (state.dailyTimerId) {
    window.clearTimeout(state.dailyTimerId);
    state.dailyTimerId = null;
  }
}

function maybeNotify(message) {
  const lastReminder = readStore(STORAGE_KEYS.lastReminder, null);
  const reminderKey = `${todayIsoString()}:${message}`;
  if (Notification.permission !== "granted" || lastReminder === reminderKey) {
    return;
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistration().then((registration) => {
      if (registration) {
        registration.showNotification("Dutch Word", {
          body: message,
          icon: "./assets/icon.svg",
          badge: "./assets/icon.svg",
        });
      } else {
        new Notification("Dutch Word", { body: message, icon: "./assets/icon.svg" });
      }
      writeStore(STORAGE_KEYS.lastReminder, reminderKey);
    });
    return;
  }

  new Notification("Dutch Word", { body: message, icon: "./assets/icon.svg" });
  writeStore(STORAGE_KEYS.lastReminder, reminderKey);
}

function scheduleDailyWakeup() {
  clearDailyTimer();
  const snoozeUntil = currentSnoozeUntil();
  if (!snoozeUntil) {
    return;
  }

  const remaining = snoozeUntil - Date.now();
  if (remaining <= 0) {
    removeStore(STORAGE_KEYS.snoozeUntil);
    renderDaily();
    maybeNotify("Your daily Dutch quiz is ready again.");
    return;
  }

  state.dailyTimerId = window.setTimeout(() => {
    removeStore(STORAGE_KEYS.snoozeUntil);
    renderDaily();
    maybeNotify("Your daily Dutch quiz is ready again.");
  }, remaining);
}

function renderDaily() {
  if (!state.ready) {
    return;
  }

  const { word, isReminder } = getDailyWord();
  const snoozeUntil = currentSnoozeUntil();

  els.daily.levelChip.textContent = word.level ? `Daily ${word.level}` : "Daily";
  hideMessage(els.daily.result);

  if (snoozeUntil && snoozeUntil > Date.now()) {
    els.daily.questionWrap.classList.add("hidden");
    els.daily.state.textContent = `Snoozed until ${formatTime(snoozeUntil)}. Come back then to retry "${word.english}".`;
    showMessage(
      els.daily.result,
      "warning",
      `<strong>Later saved.</strong><br>Your word is waiting: <strong>${word.dutch}</strong>.`
    );
    scheduleDailyWakeup();
    return;
  }

  els.daily.questionWrap.classList.remove("hidden");
  els.daily.question.textContent = `"${word.english}"`;
  els.daily.state.textContent = isReminder
    ? "Reminder word. Keep trying until it sticks."
    : "New word for today. Type the Dutch translation.";
  els.daily.answer.value = "";
  els.daily.answer.focus();
  scheduleDailyWakeup();
}

function handleDailyCheck() {
  const { word } = getDailyWord();
  const answer = normalizeAnswer(els.daily.answer.value);

  if (!answer) {
    showMessage(els.daily.result, "warning", "Type an answer before checking.");
    return;
  }

  if (answer === normalizeAnswer(word.dutch)) {
    showMessage(
      els.daily.result,
      "success",
      `<strong>Correct.</strong><br>${word.dutch} = ${word.english}<br><br>${word.example || ""}`
    );
    clearDailyWord();
    window.setTimeout(() => {
      renderDaily();
    }, 900);
    return;
  }

  state.dailyAttempts += 1;
  if (state.dailyAttempts >= 3) {
    const hint = `${word.dutch.slice(0, Math.max(1, Math.floor(word.dutch.length / 2)))}...`;
    showMessage(
      els.daily.result,
      "warning",
      `<strong>Not quite.</strong><br>Hint: <strong>${hint}</strong>`
    );
  } else {
    showMessage(els.daily.result, "danger", "<strong>Not quite.</strong><br>Try again.");
  }

  els.daily.answer.focus();
  els.daily.answer.select();
}

function handleDailyReveal() {
  const { word } = getDailyWord();
  showMessage(
    els.daily.result,
    "warning",
    `<strong>The answer is ${word.dutch}${word.level ? ` [${word.level}]` : ""}.</strong><br>${word.example || ""}`
  );
}

function handleDailyLater() {
  const wakeup = Date.now() + DAILY_SNOOZE_MS;
  writeStore(STORAGE_KEYS.snoozeUntil, wakeup);
  renderDaily();
}

function buildPracticeSummary(session) {
  if (session.total === 0) {
    return "No words practiced. Tot de volgende keer!";
  }

  const score = Math.round((session.correct / session.total) * 100);
  let closing = "Keep practicing, je kunt het.";
  if (score === 100) {
    closing = "Perfect. Uitstekend!";
  } else if (score >= 70) {
    closing = "Goed gedaan. Keep it up!";
  }

  return `Words practiced: ${session.total}
Correct: ${session.correct}
Wrong: ${session.wrong}
Score: ${score}%

${closing}`;
}

function showPracticeQuestion() {
  const session = state.practiceSession;
  if (!session) {
    return;
  }

  if (!session.queue.length && session.retryQueue.length) {
    session.queue = shuffle(session.retryQueue);
    session.retryQueue = [];
    showMessage(
      els.practice.feedback,
      "warning",
      `Review round: ${session.queue.length} word${session.queue.length === 1 ? "" : "s"} left.`
    );
  }

  if (!session.queue.length) {
    finishPractice();
    return;
  }

  session.currentWord = session.queue.shift();
  session.attempt = 0;
  els.practice.card.classList.remove("hidden");
  els.practice.summary.classList.add("hidden");
  els.practice.question.textContent = `"${session.currentWord.english}"`;
  els.practice.answer.value = "";
  els.practice.answer.focus();
  els.practice.progress.textContent = `${session.level} session`;
  els.practice.score.textContent = `Correct ${session.correct}`;
}

function startPractice() {
  const words = vocabularyForLevel(state.practiceLevel);
  hideMessage(els.practice.feedback);

  if (!words.length) {
    showMessage(els.practice.feedback, "warning", `No words found for level ${state.practiceLevel}.`);
    els.practice.card.classList.remove("hidden");
    return;
  }

  state.practiceSession = {
    level: state.practiceLevel === "All" ? "All levels" : state.practiceLevel,
    queue: shuffle(words),
    retryQueue: [],
    currentWord: null,
    attempt: 0,
    total: 0,
    correct: 0,
    wrong: 0,
  };

  showPracticeQuestion();
}

function finishPractice() {
  const session = state.practiceSession;
  if (!session) {
    return;
  }

  els.practice.card.classList.add("hidden");
  els.practice.summary.classList.remove("hidden");
  els.practice.summaryCopy.textContent = buildPracticeSummary(session);
}

function handlePracticeCheck() {
  const session = state.practiceSession;
  if (!session || !session.currentWord) {
    return;
  }

  const answer = normalizeAnswer(els.practice.answer.value);
  if (!answer) {
    showMessage(els.practice.feedback, "warning", "Type an answer before checking.");
    return;
  }

  if (answer === normalizeAnswer(session.currentWord.dutch)) {
    session.total += 1;
    session.correct += 1;
    showMessage(
      els.practice.feedback,
      "success",
      `<strong>Correct.</strong><br>${session.currentWord.dutch} = ${session.currentWord.english}<br><br>${session.currentWord.example || ""}`
    );
    window.setTimeout(() => {
      hideMessage(els.practice.feedback);
      showPracticeQuestion();
    }, 2000);
    return;
  }

  session.attempt += 1;
  if (session.attempt >= 3) {
    const hint = `${session.currentWord.dutch.slice(0, Math.max(1, Math.floor(session.currentWord.dutch.length / 2)))}...`;
    showMessage(
      els.practice.feedback,
      "warning",
      `<strong>Not quite.</strong><br>Hint: <strong>${hint}</strong>`
    );
  } else {
    showMessage(els.practice.feedback, "danger", "<strong>Not quite.</strong><br>Try again.");
  }
  els.practice.answer.focus();
  els.practice.answer.select();
}

function handlePracticeReveal() {
  const session = state.practiceSession;
  if (!session || !session.currentWord) {
    return;
  }

  session.total += 1;
  session.wrong += 1;
  session.retryQueue.push(session.currentWord);
  showMessage(
    els.practice.feedback,
    "warning",
    `<strong>The answer is ${session.currentWord.dutch}.</strong><br>${session.currentWord.example || ""}`
  );
  window.setTimeout(() => {
    hideMessage(els.practice.feedback);
    showPracticeQuestion();
  }, 2500);
}

function handlePracticeStop() {
  finishPractice();
}

function buildStudySummary(session) {
  if (session.total === 0) {
    return "No cards studied. Tot de volgende keer!";
  }

  const score = Math.round((session.known / session.total) * 100);
  let closing = "Keep studying, oefening baart kunst.";
  if (score === 100) {
    closing = "Perfect recall. Geweldig!";
  } else if (score >= 70) {
    closing = "Goed bezig. You're getting there!";
  }

  return `Cards studied: ${session.total}
Known: ${session.known}
Need review: ${session.review}
Score: ${score}%

${closing}`;
}

function renderStudyCard() {
  const session = state.studySession;
  if (!session || !session.currentWord) {
    return;
  }

  els.study.card.classList.remove("hidden");
  els.study.summary.classList.add("hidden");
  els.study.word.textContent = session.currentWord.dutch;
  els.study.answer.textContent = `🇬🇧 ${session.currentWord.english}`;
  els.study.example.textContent = session.currentWord.example || "";
  els.study.back.classList.add("hidden");
  els.study.frontActions.classList.remove("hidden");
  els.study.backActions.classList.add("hidden");
  els.study.progress.textContent = `Card ${session.roundSeen + 1} / ${session.roundSize}`;
  els.study.score.textContent = `Known ${session.known}`;
}

function showNextStudyCard() {
  const session = state.studySession;
  if (!session) {
    return;
  }

  if (!session.deck.length && session.reviewPile.length) {
    session.deck = shuffle(session.reviewPile);
    session.reviewPile = [];
    session.roundSize = session.deck.length;
    session.roundSeen = 0;
    showMessage(
      els.study.feedback,
      "warning",
      `Review round: ${session.roundSize} card${session.roundSize === 1 ? "" : "s"} to revisit.`
    );
  }

  if (!session.deck.length) {
    finishStudy();
    return;
  }

  session.currentWord = session.deck.shift();
  renderStudyCard();
}

function startStudy() {
  const words = vocabularyForLevel(state.studyLevel);
  hideMessage(els.study.feedback);

  if (!words.length) {
    showMessage(els.study.feedback, "warning", `No words found for level ${state.studyLevel}.`);
    els.study.card.classList.remove("hidden");
    return;
  }

  state.studySession = {
    level: state.studyLevel === "All" ? "All levels" : state.studyLevel,
    deck: shuffle(words),
    reviewPile: [],
    currentWord: null,
    total: 0,
    known: 0,
    review: 0,
    roundSize: words.length,
    roundSeen: 0,
  };

  showNextStudyCard();
}

function finishStudy() {
  const session = state.studySession;
  if (!session) {
    return;
  }

  els.study.card.classList.add("hidden");
  els.study.summary.classList.remove("hidden");
  els.study.summaryCopy.textContent = buildStudySummary(session);
}

function flipStudyCard() {
  const session = state.studySession;
  if (!session || !session.currentWord) {
    return;
  }

  els.study.back.classList.remove("hidden");
  els.study.frontActions.classList.add("hidden");
  els.study.backActions.classList.remove("hidden");
}

function scoreStudyCard(knewIt) {
  const session = state.studySession;
  if (!session || !session.currentWord) {
    return;
  }

  session.total += 1;
  session.roundSeen += 1;

  if (knewIt) {
    session.known += 1;
    showMessage(els.study.feedback, "success", "<strong>Nice.</strong><br>On to the next card.");
  } else {
    session.review += 1;
    session.reviewPile.push(session.currentWord);
    showMessage(els.study.feedback, "warning", "<strong>Saved for review.</strong><br>This card will come back later.");
  }

  window.setTimeout(() => {
    hideMessage(els.study.feedback);
    showNextStudyCard();
  }, 2000);
}

function startVerbs() {
  const verbs = verbsForLevel(state.verbsLevel);
  hideMessage(els.verbs.feedback);

  if (!verbs.length) {
    showMessage(els.verbs.feedback, "warning", `No verbs found for level ${state.verbsLevel}.`);
    els.verbs.card.classList.remove("hidden");
    return;
  }

  state.verbsSession = {
    level: state.verbsLevel === "All" ? "All levels" : state.verbsLevel,
    queue: shuffle(verbs),
    retryQueue: [],
    currentVerb: null,
    currentForm: null,
    attempt: 0,
    total: 0,
    correct: 0,
    wrong: 0,
  };

  els.verbs.summary.classList.add("hidden");
  els.verbs.card.classList.remove("hidden");
  els.verbs.answer.value = "";
  showVerbsQuestion();
}

function showVerbsQuestion() {
  const session = state.verbsSession;
  if (!session) {
    return;
  }

  if (session.queue.length === 0 && session.retryQueue.length === 0) {
    finishVerbs();
    return;
  }

  if (session.queue.length === 0) {
    session.queue = shuffle(session.retryQueue);
    session.retryQueue = [];
  }

  session.currentVerb = session.queue.shift();
  session.attempt = 0;
  hideMessage(els.verbs.feedback);

  if (state.verbsForm === "Both") {
    session.currentForm = sample(["Past", "Participle"]);
  } else {
    session.currentForm = state.verbsForm;
  }

  updateVerbsProgress();
  renderVerbsCard();
  els.verbs.answer.focus();
  els.verbs.answer.value = "";
}

function renderVerbsCard() {
  const session = state.verbsSession;
  if (!session || !session.currentVerb) {
    return;
  }

  const verb = session.currentVerb;
  const infinitive = verb.infinitive;
  const meaning = verb.meaning;

  if (session.currentForm === "Past") {
    els.verbs.label.textContent = "What is the past tense?";
    els.verbs.question.textContent = `${infinitive} — ${meaning}`;
  } else {
    els.verbs.label.textContent = "What is the past participle?";
    els.verbs.question.textContent = `${infinitive} — ${meaning}`;
  }
}

function updateVerbsProgress() {
  const session = state.verbsSession;
  if (!session) {
    return;
  }

  const totalVerbs = session.level === "All levels" ? state.verbs.length : verbsForLevel(session.level).length;
  const current = session.total + 1;
  els.verbs.progress.textContent = `Card ${current} / ${totalVerbs}`;
  els.verbs.score.textContent = `Correct ${session.correct}`;
}

function handleVerbsCheck() {
  const session = state.verbsSession;
  if (!session || !session.currentVerb) {
    return;
  }

  const answer = normalizeAnswer(els.verbs.answer.value);
  if (!answer) {
    showMessage(els.verbs.feedback, "warning", "Type an answer before checking.");
    return;
  }

  const verb = session.currentVerb;
  const correctAnswer = session.currentForm === "Past"
    ? normalizeAnswer(verb.past_singular)
    : normalizeAnswer(verb.participle);

  if (answer === correctAnswer) {
    session.total += 1;
    session.correct += 1;
    const auxiliary = verb.auxiliary ? ` (${verb.auxiliary})` : "";
    const form = session.currentForm === "Past" ? verb.past_singular : `${verb.participle}${auxiliary}`;
    showMessage(
      els.verbs.feedback,
      "success",
      `<strong>Correct.</strong><br>${verb.infinitive} → ${form}<br><br>${verb.example || ""}`
    );
    window.setTimeout(() => {
      hideMessage(els.verbs.feedback);
      showVerbsQuestion();
    }, 2000);
    return;
  }

  session.attempt += 1;
  if (session.attempt >= 2) {
    const hint = session.currentForm === "Past"
      ? `${verb.past_singular.slice(0, Math.max(1, Math.floor(verb.past_singular.length / 2)))}...`
      : `${verb.participle.slice(0, Math.max(1, Math.floor(verb.participle.length / 2)))}...`;
    showMessage(
      els.verbs.feedback,
      "warning",
      `<strong>Not quite.</strong><br>Hint: <strong>${hint}</strong>`
    );
  } else {
    showMessage(els.verbs.feedback, "danger", "<strong>Not quite.</strong><br>Try again.");
  }
  els.verbs.answer.focus();
  els.verbs.answer.select();
}

function handleVerbsReveal() {
  const session = state.verbsSession;
  if (!session || !session.currentVerb) {
    return;
  }

  const verb = session.currentVerb;
  const auxiliary = verb.auxiliary ? ` (${verb.auxiliary})` : "";
  const form = session.currentForm === "Past" ? verb.past_singular : `${verb.participle}${auxiliary}`;
  session.total += 1;
  session.wrong += 1;
  session.retryQueue.push(verb);
  showMessage(
    els.verbs.feedback,
    "warning",
    `<strong>The answer is ${form}.</strong><br>${verb.example || ""}`
  );
  window.setTimeout(() => {
    hideMessage(els.verbs.feedback);
    showVerbsQuestion();
  }, 2500);
}

function handleVerbsStop() {
  finishVerbs();
}

function buildVerbsSummary(session) {
  if (session.total === 0) {
    return "No verbs practiced. Tot de volgende keer!";
  }

  const score = Math.round((session.correct / session.total) * 100);
  let closing = "Keep practicing, je kunt het!";
  if (score === 100) {
    closing = "Perfect! Ongelofelijk!";
  } else if (score >= 70) {
    closing = "Goed gedaan! Keep it up!";
  }

  return `Verbs practiced: ${session.total}
Correct: ${session.correct}
Wrong: ${session.wrong}
Score: ${score}%

${closing}`;
}

function finishVerbs() {
  const session = state.verbsSession;
  if (!session) {
    return;
  }

  els.verbs.card.classList.add("hidden");
  els.verbs.summary.classList.remove("hidden");
  els.verbs.summaryCopy.textContent = buildVerbsSummary(session);
}

function activateMode(mode) {
  els.tabButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.mode === mode);
  });

  Object.entries(els.panels).forEach(([panelMode, panel]) => {
    panel.classList.toggle("is-active", panelMode === mode);
  });
}

function updateReminderButton() {
  if (!("Notification" in window)) {
    els.notificationsButton.disabled = true;
    els.notificationsButton.textContent = "Reminders unavailable";
    return;
  }

  if (Notification.permission === "granted") {
    els.notificationsButton.textContent = "Reminders enabled";
  } else if (Notification.permission === "denied") {
    els.notificationsButton.textContent = "Reminders blocked";
  } else {
    els.notificationsButton.textContent = "Enable reminders";
  }
}

async function requestReminders() {
  if (!("Notification" in window)) {
    setStatus("This browser does not support notifications.");
    return;
  }

  const result = await Notification.requestPermission();
  updateReminderButton();

  if (result === "granted") {
    setStatus("Reminders enabled. Open the app daily to see your quiz on your phone.");
    maybeNotify("Notifications are ready for Dutch Word.");
  } else {
    setStatus("Notification permission was not granted.");
  }
}

function setupInstallPrompt() {
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    state.installPrompt = event;
    els.installButton.classList.remove("hidden");
  });

  els.installButton.addEventListener("click", async () => {
    if (!state.installPrompt) {
      return;
    }

    state.installPrompt.prompt();
    await state.installPrompt.userChoice;
    state.installPrompt = null;
    els.installButton.classList.add("hidden");
  });
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  try {
    const swUrl = new URL("./sw.js", window.location.href);
    const scope = new URL("./", window.location.href).pathname;
    await navigator.serviceWorker.register(swUrl, { scope });
  } catch (error) {
    console.error("Service worker registration failed.", error);
  }
}

async function loadVocabulary() {
  const response = await fetch("./vocabulary.json");
  if (!response.ok) {
    throw new Error(`Failed to load vocabulary: ${response.status}`);
  }
  return response.json();
}

async function loadVerbs() {
  const response = await fetch("./verbs.json");
  if (!response.ok) {
    throw new Error(`Failed to load verbs: ${response.status}`);
  }
  return response.json();
}

function bindEvents() {
  els.tabButtons.forEach((button) => {
    button.addEventListener("click", () => activateMode(button.dataset.mode));
  });

  els.daily.check.addEventListener("click", handleDailyCheck);
  els.daily.idk.addEventListener("click", handleDailyReveal);
  els.daily.later.addEventListener("click", handleDailyLater);
  els.daily.answer.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      handleDailyCheck();
    }
  });

  els.practice.levelButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.practiceLevel = button.dataset.practiceLevel;
      setSelectedLevel(els.practice.levelButtons, "practiceLevel", state.practiceLevel);
    });
  });
  els.practice.start.addEventListener("click", startPractice);
  els.practice.check.addEventListener("click", handlePracticeCheck);
  els.practice.idk.addEventListener("click", handlePracticeReveal);
  els.practice.stop.addEventListener("click", handlePracticeStop);
  els.practice.restart.addEventListener("click", startPractice);
  els.practice.answer.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      handlePracticeCheck();
    }
  });

  els.study.levelButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.studyLevel = button.dataset.studyLevel;
      setSelectedLevel(els.study.levelButtons, "studyLevel", state.studyLevel);
    });
  });
  els.study.start.addEventListener("click", startStudy);
  els.study.flip.addEventListener("click", flipStudyCard);
  els.study.gotIt.addEventListener("click", () => scoreStudyCard(true));
  els.study.notYet.addEventListener("click", () => scoreStudyCard(false));
  els.study.stopFront.addEventListener("click", finishStudy);
  els.study.stopBack.addEventListener("click", finishStudy);
  els.study.restart.addEventListener("click", startStudy);

  els.verbs.levelButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.verbsLevel = button.dataset.verbsLevel;
      setSelectedLevel(els.verbs.levelButtons, "verbsLevel", state.verbsLevel);
    });
  });
  els.verbs.formRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      state.verbsForm = radio.value;
    });
  });
  els.verbs.start.addEventListener("click", startVerbs);
  els.verbs.check.addEventListener("click", handleVerbsCheck);
  els.verbs.idk.addEventListener("click", handleVerbsReveal);
  els.verbs.stop.addEventListener("click", handleVerbsStop);
  els.verbs.restart.addEventListener("click", startVerbs);
  els.verbs.answer.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      handleVerbsCheck();
    }
  });

  els.notificationsButton.addEventListener("click", requestReminders);

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      scheduleDailyWakeup();
      renderDaily();
    }
  });
}

async function init() {
  bindEvents();
  setupInstallPrompt();
  updateReminderButton();
  setSelectedLevel(els.practice.levelButtons, "practiceLevel", state.practiceLevel);
  setSelectedLevel(els.study.levelButtons, "studyLevel", state.studyLevel);
  setSelectedLevel(els.verbs.levelButtons, "verbsLevel", state.verbsLevel);

  try {
    state.words = await loadVocabulary();
    state.verbs = await loadVerbs();
    state.ready = true;
    setStatus(`${state.words.length} words and ${state.verbs.length} verbs loaded. Install this app on your phone for quick practice.`);
    renderDaily();
  } catch (error) {
    setStatus("Could not load the vocabulary list.");
    showMessage(
      els.daily.result,
      "danger",
      "The app could not load <code>vocabulary.json</code>. Check the file and reload the page."
    );
    console.error(error);
  }

  await registerServiceWorker();
}

init();
