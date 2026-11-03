#!/usr/bin/env python3
"""Audit local dictionary and Strong's-link coverage across the KJV corpus."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
KJV = BASE / "kjv"
LEXICON = BASE / "lexicon" / "lexicon.json"
WORDNET = BASE / "lexicon" / "wordnet-3.0.json"
OUT = BASE / "lexicon"
WORD_RE = re.compile(r"[\w]+(?:['’][\w]+)*", re.UNICODE)
MARKER_RE = re.compile(r'\|strong="([GH]\d+)"')


def canonical_strong(identifier: str) -> str:
    return identifier[0] + identifier[1:].lstrip("0")


def audit():
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    wordnet = json.loads(WORDNET.read_text(encoding="utf-8"))
    frequencies = Counter()
    tagged_by_form = defaultdict(Counter)
    total_tokens = marker_count = verses_with_markers = verses = books = 0
    all_ids = Counter()
    unaligned = []

    for path in sorted(KJV.glob("*.json")):
        if path.name == "manifest.json":
            continue
        book = json.loads(path.read_text(encoding="utf-8"))
        books += 1
        for chapter, verse_rows in book["chapters"].items():
            for verse in verse_rows:
                verses += 1
                raw_text = verse["t"]
                markers = list(MARKER_RE.finditer(raw_text))
                marker_count += len(markers)
                verses_with_markers += bool(markers)
                text = MARKER_RE.sub("", raw_text)
                tokens = WORD_RE.findall(text)
                forms = [token.lower().replace("’", "'") for token in tokens]
                total_tokens += len(tokens)
                marker_rows = []
                inline_by_token = defaultdict(list)
                for marker in markers:
                    prefix = MARKER_RE.sub("", raw_text[:marker.start()])
                    token_index = len(WORD_RE.findall(prefix)) - 1
                    marker_rows.append((token_index, marker.group(1)))
                    all_ids[canonical_strong(marker.group(1))] += 1
                    if token_index >= 0:
                        inline_by_token[token_index].append(marker.group(1))
                    else:
                        unaligned.append({"reference": f"{book['id']}.{chapter}.{verse['n']}",
                                          "raw_index": "inline-marker", "strong_id": marker.group(1),
                                          "detail": "inline Strong's marker has no preceding displayed word"})

                raw_to_clean = {}
                for clean_index in range(len(tokens)):
                    previous_markers = sum(1 for marker_index, _ in marker_rows if marker_index < clean_index)
                    raw_index = str(clean_index + previous_markers * 2)
                    raw_to_clean[raw_index] = clean_index
                    source_ids = list(verse.get("s", {}).get(raw_index, []))
                    source_ids.extend(inline_by_token.get(clean_index, []))
                    for identifier in source_ids:
                        canonical = canonical_strong(identifier)
                        tagged_by_form[forms[clean_index]][canonical] += 1
                        all_ids[canonical] += 1

                for raw_index, source_ids in verse.get("s", {}).items():
                    if raw_index not in raw_to_clean:
                        for identifier in source_ids:
                            unaligned.append({"reference": f"{book['id']}.{chapter}.{verse['n']}",
                                              "raw_index": raw_index, "strong_id": identifier,
                                              "detail": "source annotation key has no matching displayed English token"})
                            all_ids[canonical_strong(identifier)] += 1
                for form in forms:
                    frequencies[form] += 1

    rows = []
    curated_occurrences = wordnet_only_occurrences = 0
    for form, occurrences in frequencies.items():
        curated = form in lexicon["lexemes"]
        registered = form in lexicon["surfaceForms"]
        candidates = wordnet["surfaceForms"].get(form, [])
        if curated:
            status = "project-lexeme"
            headwords = [lexicon["lexemes"][form]["headword"]]
            curated_occurrences += occurrences
        elif registered:
            status = "registered-form"
            headwords = [lexicon["surfaceForms"][form]["lexeme"]]
            curated_occurrences += occurrences
        elif candidates:
            status = "WordNet-candidates"
            headwords = sorted({candidate["lemma"] for candidate in candidates})
            wordnet_only_occurrences += occurrences
        else:
            status = "external-lookup-fallback"
            headwords = []
        all_senses = sum(len(wordnet["entries"][headword]["senses"])
                         for headword in {candidate["lemma"] for candidate in candidates})
        local_sources = sorted(identifier for identifier in tagged_by_form[form]
                               if identifier in lexicon["sourceLexemes"])
        external_sources = sorted(identifier for identifier in tagged_by_form[form]
                                  if identifier not in lexicon["sourceLexemes"])
        rows.append({
            "surface_form": form,
            "occurrences": occurrences,
            "resolution_status": status,
            "headword_candidates": ";".join(headwords),
            "wordnet_sense_candidates": all_senses,
            "source_tag_occurrences": sum(tagged_by_form[form].values()),
            "local_source_records": ";".join(local_sources),
            "external_source_ids": ";".join(external_sources),
        })
    rows.sort(key=lambda row: (-row["occurrences"], row["surface_form"]))

    with (OUT / "coverage-audit.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (OUT / "unaligned-source-annotations.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["reference", "raw_index", "strong_id", "detail"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(unaligned)

    curated_forms = {row["surface_form"] for row in rows if row["resolution_status"] in ("project-lexeme", "registered-form")}
    wordnet_forms = {row["surface_form"] for row in rows if row["resolution_status"] == "WordNet-candidates"}
    report = {
        "edition": lexicon["edition"],
        "generated_on": "2026-11-02",
        "coverage_unit": "case-folded English surface tokens after removal of inline Strong's source markup",
        "corpus": {"books": books, "verses": verses, "word_occurrences": total_tokens,
                   "unique_surface_forms": len(frequencies), "inline_strong_markers_removed": marker_count,
                   "verses_with_inline_strong_markers": verses_with_markers},
        "english_lexicon": {
            "project_lexemes": len(lexicon["lexemes"]),
            "registered_project_forms": len(lexicon["surfaceForms"]),
            "project_resolved_occurrences": curated_occurrences,
            "project_resolved_occurrence_percent": round(100 * curated_occurrences / total_tokens, 3),
            "wordnet_edition": wordnet["edition"],
            "wordnet_headwords": wordnet["buildStats"]["distinctLinkedHeadwords"],
            "wordnet_senses": wordnet["buildStats"]["linkedSenses"],
            "wordnet_linked_unique_forms": len(wordnet_forms | (curated_forms & set(wordnet["surfaceForms"]))),
            "wordnet_only_occurrences": wordnet_only_occurrences,
            "combined_local_dictionary_occurrences": curated_occurrences + wordnet_only_occurrences,
            "combined_local_dictionary_occurrence_percent": round(100 * (curated_occurrences + wordnet_only_occurrences) / total_tokens, 3),
            "unique_forms_with_local_dictionary_data": len(curated_forms | wordnet_forms),
            "unique_forms_using_external_lookup_fallback": len(frequencies) - len(curated_forms | wordnet_forms),
        },
        "source_language": {"strong_tag_occurrences_in_source": sum(all_ids.values()),
                            "inline_tags_attached_from_verse_text": marker_count,
                            "unique_strong_ids": len(all_ids),
                            "local_source_lexeme_records": len(lexicon["sourceLexemes"]),
                            "unique_ids_without_local_records": sum(1 for identifier in all_ids
                                                                     if identifier not in lexicon["sourceLexemes"])},
        "annotation_alignment": {"source_annotation_keys_without_displayed_token": len(unaligned),
                                 "method": "Inline markers attach to their preceding displayed word; later source ordinals are shifted back by two marker fragments. Unmatched IDs remain separately listed and clickable."},
        "downloads": {"all_surface_forms": "coverage-audit.csv",
                      "unaligned_source_annotations": "unaligned-source-annotations.csv"},
        "top_external_fallback_forms": [{"surface_form": row["surface_form"], "occurrences": row["occurrences"]}
                                         for row in rows if row["resolution_status"] == "external-lookup-fallback"][:100],
    }
    (OUT / "coverage-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "top_external_fallback_forms"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    audit()
