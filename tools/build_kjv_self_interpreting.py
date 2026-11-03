#!/usr/bin/env python3
"""Compile eBible's KJV USFM into verse-addressable, word-linked JSON."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


SOURCE_URL = "https://ebible.org/Scriptures/eng-kjv2006_usfm.zip"
BOOK_ORDER = [
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA",
    "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO",
    "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO",
    "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL", "MAT",
    "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHP",
    "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE",
    "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]
BOOK_NAMES = {
    "GEN":"Genesis", "EXO":"Exodus", "LEV":"Leviticus", "NUM":"Numbers", "DEU":"Deuteronomy",
    "JOS":"Joshua", "JDG":"Judges", "RUT":"Ruth", "1SA":"1 Samuel", "2SA":"2 Samuel",
    "1KI":"1 Kings", "2KI":"2 Kings", "1CH":"1 Chronicles", "2CH":"2 Chronicles", "EZR":"Ezra",
    "NEH":"Nehemiah", "EST":"Esther", "JOB":"Job", "PSA":"Psalms", "PRO":"Proverbs",
    "ECC":"Ecclesiastes", "SNG":"Song of Solomon", "ISA":"Isaiah", "JER":"Jeremiah",
    "LAM":"Lamentations", "EZK":"Ezekiel", "DAN":"Daniel", "HOS":"Hosea", "JOL":"Joel",
    "AMO":"Amos", "OBA":"Obadiah", "JON":"Jonah", "MIC":"Micah", "NAM":"Nahum", "HAB":"Habakkuk",
    "ZEP":"Zephaniah", "HAG":"Haggai", "ZEC":"Zechariah", "MAL":"Malachi", "MAT":"Matthew",
    "MRK":"Mark", "LUK":"Luke", "JHN":"John", "ACT":"Acts", "ROM":"Romans",
    "1CO":"1 Corinthians", "2CO":"2 Corinthians", "GAL":"Galatians", "EPH":"Ephesians",
    "PHP":"Philippians", "COL":"Colossians", "1TH":"1 Thessalonians", "2TH":"2 Thessalonians",
    "1TI":"1 Timothy", "2TI":"2 Timothy", "TIT":"Titus", "PHM":"Philemon", "HEB":"Hebrews",
    "JAS":"James", "1PE":"1 Peter", "2PE":"2 Peter", "1JN":"1 John", "2JN":"2 John",
    "3JN":"3 John", "JUD":"Jude", "REV":"Revelation",
}
OT = set(BOOK_ORDER[:39])
VERSE_RE = re.compile(r"^\\v\s+([0-9]+[a-z]?(?:-[0-9]+[a-z]?)?)\s+(.*)$")
WORD_RE = re.compile(r'\\w\s+([^|\\]+)\|([^\\]*)\\w\*')
TOKEN_RE = re.compile(r"\x01([^\x02]*)\x02(.*?)\x03|\x04|\x05|\s+|[^\W_]+(?:[’'][^\W_]+)*|[^\w\s]", re.UNICODE | re.DOTALL)


def verse_segments(raw: str) -> list[dict[str, object]]:
    # Footnotes and cross-reference apparatus are not part of the verse text.
    raw = re.sub(r"\\[fx]\s+.*?\\[fx]\*", "", raw, flags=re.DOTALL)

    def mark_word(match: re.Match[str]) -> str:
        word, attrs = match.group(1), match.group(2)
        strong = re.search(r'\bstrong="([^"]+)"', attrs)
        return f"\x01{strong.group(1) if strong else ''}\x02{word}\x03"

    marked = WORD_RE.sub(mark_word, raw)
    marked = marked.replace(r"\add*", "\x05").replace(r"\add", "\x04")
    marked = re.sub(r"\\[A-Za-z0-9+]+\*?", "", marked)
    marked = marked.replace("~", " ").replace("\u00a0", " ")

    result: list[dict[str, object]] = []
    added = False
    for match in TOKEN_RE.finditer(marked):
        token = match.group(0)
        if token == "\x04":
            added = True
        elif token == "\x05":
            added = False
        elif token.startswith("\x01"):
            strong, text = token[1:-1].split("\x02", 1)
            segment: dict[str, object] = {"t": text, "kind": "word"}
            if strong:
                segment["strong"] = strong.split()
            if added:
                segment["added"] = True
            result.append(segment)
        elif token.isspace():
            result.append({"t": token, "kind": "space"})
        elif re.match(r"[^\W_]", token, re.UNICODE):
            segment = {"t": token, "kind": "word"}
            if added:
                segment["added"] = True
            result.append(segment)
        else:
            result.append({"t": token, "kind": "punct"})

    # Merge adjacent spaces to keep the generated corpus compact.
    merged: list[dict[str, object]] = []
    for segment in result:
        if segment["kind"] == "space" and merged and merged[-1]["kind"] == "space":
            merged[-1]["t"] = str(merged[-1]["t"]) + str(segment["t"])
        else:
            merged.append(segment)
    return merged


def compile_book(name: str, source: str) -> dict[str, object]:
    book_id = re.search(r"^\\id\s+(\S+)", source, re.MULTILINE).group(1)  # type: ignore[union-attr]
    chapters: dict[str, list[dict[str, object]]] = {}
    current_chapter: str | None = None
    for line in source.splitlines():
        chapter_match = re.match(r"^\\c\s+(\d+)", line)
        if chapter_match:
            current_chapter = chapter_match.group(1)
            chapters.setdefault(current_chapter, [])
            continue
        verse_match = VERSE_RE.match(line)
        if verse_match and current_chapter is not None:
            verse, raw = verse_match.groups()
            segments = verse_segments(raw)
            text = "".join(str(segment["t"]) for segment in segments).rstrip()
            strong: dict[str, list[str]] = {}
            added: list[int] = []
            word_index = 0
            for segment in segments:
                if segment["kind"] != "word":
                    continue
                if "strong" in segment:
                    strong[str(word_index)] = segment["strong"]  # type: ignore[assignment]
                if segment.get("added"):
                    added.append(word_index)
                word_index += 1
            compact_verse: dict[str, object] = {"n": verse, "t": text}
            if strong:
                compact_verse["s"] = strong
            if added:
                compact_verse["a"] = added
            chapters[current_chapter].append(compact_verse)

    return {
        "id": book_id,
        "name": BOOK_NAMES[book_id],
        "testament": "OT" if book_id in OT else "NT",
        "chapters": chapters,
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: build_kjv_self_interpreting.py SOURCE.zip OUTPUT_DIR", file=sys.stderr)
        return 2
    archive_path = Path(sys.argv[1])
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    manifest: dict[str, object] = {
        "translation": "King James Version (1769 standardized text; eBible eng-kjv2006 USFM)",
        "source": SOURCE_URL,
        "archive_sha256": archive_hash,
        "source_license": "Public domain text; source package courtesy of CrossWire Bible Society and eBible.org",
        "book_order": BOOK_ORDER,
        "books": [],
    }
    with zipfile.ZipFile(archive_path) as archive:
        files = {Path(item.filename).name.split("eng-kjv2006")[0][-3:]: item for item in archive.infolist() if item.filename.endswith(".usfm")}
        for book_id in BOOK_ORDER:
            item = files.get(book_id)
            if item is None:
                raise ValueError(f"Missing USFM source for {book_id}")
            book = compile_book(item.filename, archive.read(item).decode("utf-8-sig"))
            filename = f"{book_id}.json"
            (output / filename).write_text(json.dumps(book, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            book_info = {
                "id": book_id,
                "name": BOOK_NAMES[book_id],
                "testament": book["testament"],
                "chapters": len(book["chapters"]),
                "verses": sum(len(v) for v in book["chapters"].values()),
                "file": filename,
            }
            manifest["books"].append(book_info)  # type: ignore[union-attr]
            verse_count = sum(len(v) for v in book["chapters"].values())  # type: ignore[union-attr]
            print(f"{book_id}: {len(book['chapters'])} chapters, {verse_count} verses")
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
