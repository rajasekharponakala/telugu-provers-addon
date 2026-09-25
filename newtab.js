"use strict";

// How many recently shown proverbs to avoid repeating.
const HISTORY_SIZE = 30;
const HISTORY_KEY = "recentProverbs";
const THEME_KEY = "theme";

const proverbEl = document.getElementById("proverb");
const explainEl = document.getElementById("explain");
const meaningEl = document.getElementById("meaning");
const englishEl = document.getElementById("english");
const counterEl = document.getElementById("counter");
const nextButton = document.getElementById("nextButton");
const copyButton = document.getElementById("copyButton");
const copyLabel = document.getElementById("copyLabel");
const themeToggle = document.getElementById("themeToggle");
const sourceNote = document.getElementById("sourceNote");

// localStorage can throw (e.g. with site data blocked), so every access is guarded.
function load(key, fallback) {
  try {
    const value = localStorage.getItem(key);
    return value === null ? fallback : JSON.parse(value);
  } catch {
    return fallback;
  }
}

function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Not fatal: we just lose the preference.
  }
}

function normalize(entry) {
  return typeof entry === "string" ? { text: entry } : entry;
}

// Picks a random index, skipping the ones shown recently.
function pickIndex() {
  const total = PROVERBS.length;
  const recent = load(HISTORY_KEY, []).filter((i) => Number.isInteger(i) && i < total);
  const avoid = new Set(recent.slice(-Math.min(HISTORY_SIZE, total - 1)));

  let index;
  do {
    index = Math.floor(Math.random() * total);
  } while (avoid.has(index));

  recent.push(index);
  save(HISTORY_KEY, recent.slice(-HISTORY_SIZE));
  return index;
}

let current = null;

function showProverb() {
  if (!PROVERBS.length) {
    proverbEl.textContent = "సామెతలు దొరకలేదు.";
    return;
  }
  const index = pickIndex();
  current = normalize(PROVERBS[index]);

  for (const el of [proverbEl, explainEl]) {
    el.classList.remove("fade-in");
    // Force a reflow so the animation restarts on every change.
    void el.offsetWidth;
    el.classList.add("fade-in");
  }

  proverbEl.textContent = current.text;
  meaningEl.textContent = current.meaning || "";
  meaningEl.hidden = !current.meaning;
  englishEl.textContent = current.en || "";
  englishEl.hidden = !current.en;
  explainEl.hidden = !current.meaning && !current.en;
  counterEl.textContent = `${index + 1} / ${PROVERBS.length}`;
}

async function copyProverb() {
  if (!current) return;
  try {
    const lines = [current.text];
    if (current.meaning) lines.push(`భావం: ${current.meaning}`);
    if (current.en) lines.push(current.en);
    await navigator.clipboard.writeText(lines.join("\n"));
    copyLabel.textContent = "కాపీ అయింది ✓";
  } catch {
    copyLabel.textContent = "కాపీ కాలేదు";
  }
  setTimeout(() => (copyLabel.textContent = "కాపీ"), 1500);
}

function applyTheme(theme) {
  if (theme === "light" || theme === "dark") {
    document.documentElement.dataset.theme = theme;
  } else {
    delete document.documentElement.dataset.theme;
  }
}

function toggleTheme() {
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const active = document.documentElement.dataset.theme || (prefersDark ? "dark" : "light");
  const next = active === "dark" ? "light" : "dark";
  applyTheme(next);
  save(THEME_KEY, next);
}

if (typeof PROVERBS_SOURCE !== "undefined" && PROVERBS_SOURCE.license) {
  sourceNote.textContent = `(${PROVERBS_SOURCE.license})`;
}

applyTheme(load(THEME_KEY, null));
showProverb();

nextButton.addEventListener("click", showProverb);
copyButton.addEventListener("click", copyProverb);
themeToggle.addEventListener("click", toggleTheme);

document.addEventListener("keydown", (event) => {
  if (event.ctrlKey || event.metaKey || event.altKey) return;
  // Let a focused button or link handle Space itself.
  if (event.key === " " && event.target.closest("button, a")) return;
  if (event.key === " " || event.key === "ArrowRight" || event.key === "n") {
    event.preventDefault();
    showProverb();
  } else if (event.key === "c") {
    copyProverb();
  }
});
