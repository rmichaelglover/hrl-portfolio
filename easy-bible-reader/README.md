# Easy Bible Reader

A tiny, free, ad-free, reading-first Bible reader.

**Design order:** reading → navigation → browsing.

The interface aims to feel closer to a clean text file opened in a good editor than to a content portal. It has comfortable proportional typography by default, while retaining fast keyboard-driven navigation for users who want it.

## MVP

- Clean reading view with minimal chrome
- Reference jump (`John 3:16`, `Psalm 23`)
- Full-text search over installed translation data
- Book/chapter browser
- Previous/next chapter
- Local bookmarks and resume position
- Adjustable size, measure, line spacing, serif/sans, verse numbers, dark mode
- Optional Vim-inspired keys: `j`, `k`, `gg`, `G`, `/`, `:`, `[`, `]`, `Ctrl-f`, `Ctrl-b`
- PWA/offline shell
- No account, ads, analytics, feed, or tracking

## Run

Because the service worker requires HTTP rather than `file://`:

```bash
cd easy-bible-reader
python3 -m http.server 8080
```

Open `http://localhost:8080`.

## Bible text

The repository includes the complete 66-book Protestant canon of the public-domain **World English Bible**: 39 Old Testament books and 27 New Testament books. Deuterocanonical/apocryphal books are intentionally excluded. The source is eBible.org's canon-only `engwebp` VPL distribution; `tools/build_web_bible.py` reproducibly converts that source while enforcing an explicit 66-book allowlist and 1,189-chapter count.

The translation registry is ready for ten English editions. Before a full text is committed, its redistribution status should be verified for the project's distribution jurisdictions. Editions currently listed in the UI but not installed are visibly disabled.

Other translations remain visibly disabled until complete text and redistribution status are verified for the project's distribution jurisdictions.

## Portfolio placement

Suggested location:

```text
hrl-portfolio/
  extras/
    easy-bible-reader/
```

Suggested main README line:

> **Easy Bible Reader** — a small, independent, ad-free Bible reader focused on typography, offline reading, and unobtrusive navigation.

This is intentionally an independent software side-project, not an HRL application.
