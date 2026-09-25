# తెలుగు సామెతలు · Telugu Proverbs (Firefox add-on)

A Firefox extension that replaces the new tab page with a random Telugu proverb (సామెత).
Every new tab shows a different one.

Inspired by [scientific-temper](https://github.com/bhavabhuthi/scientific-temper).
The proverbs come from the Telugu Wikipedia
[సామెతల జాబితా](https://te.wikipedia.org/wiki/%E0%B0%B8%E0%B0%BE%E0%B0%AE%E0%B1%86%E0%B0%A4%E0%B0%B2_%E0%B0%9C%E0%B0%BE%E0%B0%AC%E0%B0%BF%E0%B0%A4%E0%B0%BE) page.

## Features

- A random proverb on every new tab, without repeating the last 30 you saw
- **మరొకటి** button (or <kbd>Space</kbd> / <kbd>→</kbd> / <kbd>N</kbd>) for another proverb
- **కాపీ** button (or <kbd>C</kbd>) to copy the proverb
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

## Updating the proverb list

`proverbs.js` currently holds a starter set of well-known proverbs. To import the
full list from Telugu Wikipedia, run (Python 3, no extra packages needed):

```sh
python3 scripts/fetch_proverbs.py --dry-run   # preview what will be imported
python3 scripts/fetch_proverbs.py             # regenerate proverbs.js
```

The script reads the page through the MediaWiki API, follows its sub-pages, and
keeps every list item written in Telugu. A nested list item under a proverb, or text
after a spaced dash (`సామెత – అర్థం`), is shown as the proverb's meaning.
Wikipedia text is licensed CC BY-SA 4.0; the new tab page shows the attribution
automatically once the list is imported.

## Project layout

| File | Purpose |
| --- | --- |
| `manifest.json` | Extension manifest (Manifest V3, overrides the new tab page) |
| `newtab.html`, `newtab.js`, `style.css` | The new tab page |
| `proverbs.js` | Proverb data (`PROVERBS` array) |
| `fonts/` | Noto Telugu fonts (SIL Open Font License, see `fonts/OFL.txt`) |
| `icons/icon.svg` | Add-on icon |
| `scripts/fetch_proverbs.py` | Imports proverbs from Telugu Wikipedia |
