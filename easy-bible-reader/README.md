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

The repository currently includes a **small WEB demo dataset** sufficient to exercise the reader. It intentionally does **not** pretend that placeholder/demo text constitutes ten installed translations.

The translation registry is ready for ten English editions. Before a full text is committed, its redistribution status should be verified for the project's distribution jurisdictions. Editions currently listed in the UI but not installed are visibly disabled.

The World English Bible is public domain and is a good default full bundled edition. eBible.org also publishes machine-readable/downloadable formats suitable for a later import step.

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
