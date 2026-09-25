#!/usr/bin/env python3
"""Regenerate proverbs.js from the Telugu Wikipedia list of proverbs.

Usage:
    python3 scripts/fetch_proverbs.py              # fetch from te.wikipedia.org
    python3 scripts/fetch_proverbs.py --dry-run    # only print what was found
    python3 scripts/fetch_proverbs.py --wikitext page.txt   # parse a saved file

The script reads the wikitext of "సామెతల జాబితా" through the MediaWiki API,
follows its sub-pages (for example one page per letter), and collects every
bulleted/numbered list item that contains Telugu text. A nested list item
directly under a proverb, or text after a spaced dash ("సామెత – అర్థం"),
is kept as that proverb's meaning.

Only the Python standard library is needed.
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://te.wikipedia.org/w/api.php"
MAIN_PAGE = "సామెతల జాబితా"
PAGE_URL = "https://te.wikipedia.org/wiki/" + urllib.parse.quote(MAIN_PAGE.replace(" ", "_"))
USER_AGENT = "TeluguProverbsFirefoxAddon/0.1 (https://github.com/rajasekharponakala/telugu-provers-addon)"
OUTPUT = Path(__file__).resolve().parent.parent / "proverbs.js"

TELUGU = re.compile(r"[ఀ-౿]")
# Linked pages we treat as part of the list: sub-pages of the main page,
# or pages named like "సామెతలు - అ" / "సామెతలు (అ)".
SUBPAGE = re.compile(r"^(" + re.escape(MAIN_PAGE) + r"/|సామెతలు\s*[-–—:(/])")
MEANING_SPLIT = re.compile(r"\s+[-–—]\s+|\s*[:：]\s+")


def api_get(**params):
    params.update(format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError(f"{data['error'].get('code')}: {data['error'].get('info')}")
    return data


def fetch_page(title):
    data = api_get(action="parse", page=title, prop="wikitext|links", redirects="1")
    parse = data["parse"]
    links = [link["title"] for link in parse.get("links", []) if link.get("ns") == 0 and link.get("exists", True)]
    return parse["title"], parse["wikitext"], links


def strip_markup(text):
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # Innermost templates first, repeatedly, to handle nesting.
    while True:
        stripped = re.sub(r"\{\{[^{}]*\}\}", "", text)
        if stripped == text:
            break
        text = stripped
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip(" .,;।")


def parse_wikitext(wikitext):
    """Returns a list of {"text", "meaning"} dicts from the page's list items."""
    entries = []
    for line in wikitext.splitlines():
        match = re.match(r"^([*#]+)[:;]?\s*(.*)$", line)
        if not match:
            continue
        depth, body = len(match.group(1)), strip_markup(match.group(2))
        if not body or not TELUGU.search(body):
            continue
        if depth > 1 and entries:
            # A nested item explains the proverb above it.
            last = entries[-1]
            last["meaning"] = (last.get("meaning", "") + " " + body).strip()
            continue
        parts = MEANING_SPLIT.split(body, maxsplit=1)
        entry = {"text": parts[0].strip()}
        if len(parts) == 2 and TELUGU.search(parts[1]):
            entry["meaning"] = parts[1].strip()
        entries.append(entry)
    return [e for e in entries if 3 <= len(e["text"]) <= 200]


def dedupe(entries):
    seen, result = set(), []
    for entry in entries:
        key = re.sub(r"[\s,.!?;:'\"“”‘’-]", "", entry["text"])
        if key in seen:
            continue
        seen.add(key)
        result.append(entry)
    return result


def collect_from_wikipedia():
    title, wikitext, links = fetch_page(MAIN_PAGE)
    print(f"Fetched {title}", file=sys.stderr)
    entries = parse_wikitext(wikitext)
    for sub in [link for link in links if SUBPAGE.match(link)]:
        try:
            sub_title, sub_text, _ = fetch_page(sub)
        except Exception as error:  # noqa: BLE001 - keep going with other pages
            print(f"  skipped {sub}: {error}", file=sys.stderr)
            continue
        found = parse_wikitext(sub_text)
        print(f"  {sub_title}: {len(found)}", file=sys.stderr)
        entries.extend(found)
    return entries


def write_js(entries, path):
    items = []
    for entry in entries:
        if entry.get("meaning"):
            items.append("  " + json.dumps({"text": entry["text"], "meaning": entry["meaning"]}, ensure_ascii=False) + ",")
        else:
            items.append("  " + json.dumps(entry["text"], ensure_ascii=False) + ",")
    source = {"name": "te.wikipedia.org – " + MAIN_PAGE, "url": PAGE_URL, "license": "CC BY-SA 4.0"}
    path.write_text(
        "// Generated by scripts/fetch_proverbs.py from Telugu Wikipedia – do not edit by hand.\n"
        f"// Source: {PAGE_URL}\n"
        "// Text is available under the Creative Commons Attribution-ShareAlike License 4.0.\n\n"
        f"const PROVERBS_SOURCE = {json.dumps(source, ensure_ascii=False, indent=2)};\n\n"
        "const PROVERBS = [\n" + "\n".join(items) + "\n];\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wikitext", type=Path, help="parse this saved wikitext file instead of fetching")
    parser.add_argument("--output", type=Path, default=OUTPUT, help=f"output file (default: {OUTPUT})")
    parser.add_argument("--dry-run", action="store_true", help="print the proverbs instead of writing them")
    args = parser.parse_args()

    if args.wikitext:
        entries = parse_wikitext(args.wikitext.read_text(encoding="utf-8"))
    else:
        entries = collect_from_wikipedia()
    entries = dedupe(entries)

    if not entries:
        sys.exit("No proverbs found – the page layout may have changed.")
    if args.dry_run:
        for entry in entries:
            print(entry["text"] + (f"  ⟶  {entry['meaning']}" if entry.get("meaning") else ""))
    else:
        write_js(entries, args.output)
    print(f"{len(entries)} proverbs" + ("" if args.dry_run else f" written to {args.output}"), file=sys.stderr)


if __name__ == "__main__":
    main()
