"""Integrity checks for the complete, non-apocryphal Easy Bible Reader dataset."""

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
DATA_FILE = ROOT / "easy-bible-reader" / "data" / "web-canon.js"
EXPECTED_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation",
]


def load_canon():
    raw = DATA_FILE.read_text(encoding="utf-8")
    return json.loads(raw.removeprefix("window.BIBLE_DATA={web:").removesuffix("};\n"))


def test_complete_protestant_canon_in_canonical_order():
    canon = load_canon()
    assert list(canon) == EXPECTED_BOOKS
    assert len(list(canon)[:39]) == 39
    assert len(list(canon)[39:]) == 27
    assert sum(len(chapters) for chapters in canon.values()) == 1189


def test_canon_has_all_source_verse_records_and_boundary_passages():
    canon = load_canon()
    assert sum(len(verses) for chapters in canon.values() for verses in chapters.values()) == 31103
    assert canon["Genesis"]["1"][0] == "In the beginning, God created the heavens and the earth."
    assert "God so loved the world" in canon["John"]["3"][15]
    assert canon["Revelation"]["22"][-1].startswith("The grace of the Lord Jesus Christ")


def test_read_aloud_controls_and_browser_speech_are_wired():
    page = (ROOT / "easy-bible-reader" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "easy-bible-reader" / "app.js").read_text(encoding="utf-8")
    assert all(control in page for control in ('id="readBtn"', 'id="speechToggle"', 'id="speechStop"', 'id="speechRate"', 'id="speechVoice"'))
    assert "SpeechSynthesisUtterance" in app
    assert "speechSynthesis.pause()" in app
    assert "speechSynthesis.resume()" in app
    assert "speechSynthesis.cancel()" in app
    assert "speech.utterance=new SpeechSynthesisUtterance" in app
    assert "speech.nextTimer=setTimeout(()=>speakCurrent(token),160)" in app
    assert "startReading(nearestVerse())" in app
