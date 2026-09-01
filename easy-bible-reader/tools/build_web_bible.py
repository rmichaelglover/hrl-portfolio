#!/usr/bin/env python3
"""Convert eBible.org engwebp VPL text to the reader's compact JavaScript data."""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

BOOKS = OrderedDict([
    ("GEN", "Genesis"), ("EXO", "Exodus"), ("LEV", "Leviticus"),
    ("NUM", "Numbers"), ("DEU", "Deuteronomy"), ("JOS", "Joshua"),
    ("JDG", "Judges"), ("RUT", "Ruth"), ("1SA", "1 Samuel"),
    ("2SA", "2 Samuel"), ("1KI", "1 Kings"), ("2KI", "2 Kings"),
    ("1CH", "1 Chronicles"), ("2CH", "2 Chronicles"), ("EZR", "Ezra"),
    ("NEH", "Nehemiah"), ("EST", "Esther"), ("JOB", "Job"),
    ("PSA", "Psalms"), ("PRO", "Proverbs"), ("ECC", "Ecclesiastes"),
    ("SOL", "Song of Solomon"), ("ISA", "Isaiah"), ("JER", "Jeremiah"),
    ("LAM", "Lamentations"), ("EZE", "Ezekiel"), ("DAN", "Daniel"),
    ("HOS", "Hosea"), ("JOE", "Joel"), ("AMO", "Amos"),
    ("OBA", "Obadiah"), ("JON", "Jonah"), ("MIC", "Micah"),
    ("NAH", "Nahum"), ("HAB", "Habakkuk"), ("ZEP", "Zephaniah"),
    ("HAG", "Haggai"), ("ZEC", "Zechariah"), ("MAL", "Malachi"),
    ("MAT", "Matthew"), ("MAR", "Mark"), ("LUK", "Luke"),
    ("JOH", "John"), ("ACT", "Acts"), ("ROM", "Romans"),
    ("1CO", "1 Corinthians"), ("2CO", "2 Corinthians"), ("GAL", "Galatians"),
    ("EPH", "Ephesians"), ("PHI", "Philippians"), ("COL", "Colossians"),
    ("1TH", "1 Thessalonians"), ("2TH", "2 Thessalonians"),
    ("1TI", "1 Timothy"), ("2TI", "2 Timothy"), ("TIT", "Titus"),
    ("PHM", "Philemon"), ("HEB", "Hebrews"), ("JAM", "James"),
    ("1PE", "1 Peter"), ("2PE", "2 Peter"), ("1JO", "1 John"),
    ("2JO", "2 John"), ("3JO", "3 John"), ("JUD", "Jude"),
    ("REV", "Revelation"),
])
LINE = re.compile(r"^([1-3]?[A-Z]+) (\d+):(\d+) (.*)$")


def convert(source: Path, destination: Path) -> tuple[int, int]:
    data = OrderedDict((name, OrderedDict()) for name in BOOKS.values())
    verses = 0
    seen_codes = set()
    for number, raw in enumerate(source.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = LINE.match(raw)
        if not match:
            raise ValueError(f"Malformed VPL record at line {number}")
        code, chapter_text, verse_text, text = match.groups()
        if code not in BOOKS:
            raise ValueError(f"Noncanonical or unknown book code: {code}")
        seen_codes.add(code)
        chapter, verse = int(chapter_text), int(verse_text)
        chapter_verses = data[BOOKS[code]].setdefault(str(chapter), [])
        if verse != len(chapter_verses) + 1:
            raise ValueError(f"Noncontiguous verse at {code} {chapter}:{verse}")
        chapter_verses.append(text)
        verses += 1
    missing = set(BOOKS) - seen_codes
    if missing:
        raise ValueError(f"Missing canonical books: {sorted(missing)}")
    chapters = sum(len(book) for book in data.values())
    if chapters != 1189:
        raise ValueError(f"Expected 1,189 chapters, found {chapters}")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    destination.write_text(f"window.BIBLE_DATA={{web:{encoded}}};\n", encoding="utf-8")
    return chapters, verses


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_web_bible.py SOURCE.vpl DESTINATION.js")
    chapter_count, verse_count = convert(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Wrote 66 books, {chapter_count} chapters, {verse_count} verses")
