# తెలుగు సామెతలు · Telugu Proverbs (Firefox add-on)

A Firefox extension that replaces the new tab page with a random Telugu proverb (సామెత).
Every new tab shows a different one.

Inspired by [scientific-temper](https://github.com/bhavabhuthi/scientific-temper).
The proverbs come from the Telugu Wikipedia
[సామెతల జాబితా](https://te.wikipedia.org/wiki/%E0%B0%B8%E0%B0%BE%E0%B0%AE%E0%B1%86%E0%B0%A4%E0%B0%B2_%E0%B0%9C%E0%B0%BE%E0%B0%AC%E0%B0%BF%E0%B0%A4%E0%B0%BE) page.

## Features

- A random proverb on every new tab, without repeating the last 30 you saw
- **మరొకటి** button (or <kbd>Space</kbd> / <kbd>→</kbd> / <kbd>N</kbd>) for another proverb
- The meaning of each proverb (భావం) in Telugu, with a short English meaning
- **కాపీ** button (or <kbd>C</kbd>) to copy the proverb and its meaning
- Light and dark themes (follows your system setting, toggle in the top-right corner)
- Bundled Noto Serif/Sans Telugu fonts, so it renders correctly even without Telugu fonts installed
- Works fully offline: no network requests, no permissions, no data collection

## Try it locally

1. Open `about:debugging#/runtime/this-firefox` in Firefox.
2. Click **Load Temporary Add-on…** and pick `manifest.json` from this folder.
3. Open a new tab.

Or with [web-ext](https://github.com/mozilla/web-ext):

```sh
npx web-ext run      # launches Firefox with the add-on loaded
npx web-ext lint     # validates the add-on
npx web-ext build    # creates the .zip to upload to addons.mozilla.org
```

## The proverbs

`proverbs.js` holds 441 proverbs from the Telugu Wikipedia list, cleaned up and
de-duplicated. Riddles, broken entries and crude or demeaning proverbs were left out.
Each entry has a Telugu meaning (భావం) and a short English meaning:

```js
{ text: "అందని ద్రాక్ష పుల్లన", meaning: "దొరకని దాన్ని చెడ్డదని తీసిపారేయడం.", en: "Grapes out of reach are sour." },
```

To add or correct a proverb, edit that file. The proverbs come from Wikipedia and are
licensed CC BY-SA 4.0; the new tab page credits the source.

## Project layout

| File | Purpose |
| --- | --- |
| `manifest.json` | Extension manifest (Manifest V3, overrides the new tab page) |
| `newtab.html`, `newtab.js`, `style.css` | The new tab page |
| `proverbs.js` | Proverbs with their meanings (`PROVERBS` array) |
| `fonts/` | Noto Telugu fonts (SIL Open Font License, see `fonts/OFL.txt`) |
| `icons/icon.svg` | Add-on icon |
