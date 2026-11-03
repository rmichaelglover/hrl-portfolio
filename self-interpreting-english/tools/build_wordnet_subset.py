#!/usr/bin/env python3
"""Build a WordNet 3.0 lookup subset for the KJV surface forms.

The source directory is the unpacked Princeton WordNet 3.0 database. The output
contains only headwords and senses reachable from the checked-in KJV corpus.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
KJV = BASE / "kjv"
OUTPUT = BASE / "lexicon" / "wordnet-3.0.json"
WORD_RE = re.compile(r"[\w]+(?:['’][\w]+)*", re.UNICODE)
MARKER_RE = re.compile(r'\|strong="[GH]\d+"')
POS_FILES = {"n": "noun", "v": "verb", "a": "adj", "s": "adj", "r": "adv"}
MORPHY_RULES = {
    "n": (("s", ""), ("ses", "s"), ("ves", "f"), ("xes", "x"),
          ("zes", "z"), ("ches", "ch"), ("shes", "sh"), ("men", "man"),
          ("ies", "y")),
    "v": (("s", ""), ("ies", "y"), ("es", "e"), ("es", ""),
          ("ed", "e"), ("ed", ""), ("ing", "e"), ("ing", "")),
    "a": (("er", ""), ("est", ""), ("er", "e"), ("est", "e")),
    "r": (),
}


def surface_forms():
    found = set()
    for path in KJV.glob("*.json"):
        if path.name == "manifest.json":
            continue
        book = json.loads(path.read_text(encoding="utf-8"))
        for verses in book["chapters"].values():
            for verse in verses:
                text = MARKER_RE.sub("", verse["t"])
                found.update(word.lower().replace("’", "'") for word in WORD_RE.findall(text))
    return found


def index_records(directory: Path):
    lemmas = defaultdict(set)
    sense_order = {}
    for pos, filename in POS_FILES.items():
        path = directory / f"index.{filename}"
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line[0].isspace():
                continue
            fields = line.split()
            if len(fields) < 6:
                continue
            lemma = fields[0].replace("_", " ").lower()
            actual_pos = "a" if pos == "s" else pos
            pointer_count = int(fields[3])
            offsets = fields[6 + pointer_count:]
            lemmas[lemma].add(actual_pos)
            sense_order[(lemma, actual_pos)] = offsets
    return lemmas, sense_order


def exception_records(directory: Path):
    result = defaultdict(lambda: defaultdict(list))
    for pos, filename in (("n", "noun.exc"), ("v", "verb.exc"), ("a", "adj.exc"), ("r", "adv.exc")):
        path = directory / filename
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            fields = line.split()
            if len(fields) > 1:
                result[fields[0].lower()][pos].extend(x.lower() for x in fields[1:])
    return result


def resolve_form(form, lemmas, exceptions):
    links = []
    for pos in ("n", "v", "a", "r"):
        if pos in lemmas.get(form, set()):
            links.append({"lemma": form, "partOfSpeech": pos, "relation": "exact-form"})
    for pos, candidates in exceptions.get(form, {}).items():
        for candidate in candidates:
            if pos in lemmas.get(candidate, set()):
                links.append({"lemma": candidate, "partOfSpeech": pos,
                              "relation": "WordNet-irregular-form"})
    for pos, rules in MORPHY_RULES.items():
        for suffix, replacement in rules:
            if not suffix or not form.endswith(suffix):
                continue
            candidate = form[:-len(suffix)] + replacement
            if pos in lemmas.get(candidate, set()):
                links.append({"lemma": candidate, "partOfSpeech": pos,
                              "relation": "WordNet-morphology"})
    unique = {}
    for link in links:
        unique[(link["lemma"], link["partOfSpeech"])] = link
    return list(unique.values())


def parse_synset(line):
    record, gloss = line.rstrip().split(" | ", 1)
    fields = record.split()
    offset, lexfile, raw_pos = fields[:3]
    word_count = int(fields[3], 16)
    words = [fields[4 + 2 * i].replace("_", " ").lower() for i in range(word_count)]
    definitions = gloss.split('; "', 1)
    definition = definitions[0].strip()
    examples = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', gloss)
    pos = "a" if raw_pos == "s" else raw_pos
    return offset, raw_pos, pos, lexfile, words, definition, examples


def build(directory: Path, output: Path):
    forms = surface_forms()
    lemmas, sense_order = index_records(directory)
    exceptions = exception_records(directory)
    form_links = {form: resolve_form(form, lemmas, exceptions) for form in sorted(forms)}
    # Function words often appear as multiword lemmas rather than standalone
    # entries in WordNet. The tokenizer has already separated the phrase, so
    # preserve a precise compound-lemma route for these common lexical forms.
    compounds = {"into", "onto", "upon", "within", "without", "thereby",
                 "herein", "whereby", "wherein", "therein", "thereof"}
    for form in sorted(forms & compounds):
        for lemma, positions in lemmas.items():
            if " " in lemma and form in lemma.split():
                for pos in sorted(positions):
                    form_links[form].append({"lemma": lemma, "partOfSpeech": pos,
                                             "relation": "WordNet-compound-component"})
        unique = {(link["lemma"], link["partOfSpeech"]): link for link in form_links[form]}
        form_links[form] = list(unique.values())
    needed = {link["lemma"] for links in form_links.values() for link in links}
    records = defaultdict(list)
    lexnames_path = directory / "lexnames"
    lexnames = {}
    if lexnames_path.exists():
        for line in lexnames_path.read_text(encoding="utf-8", errors="replace").splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[0].isdigit():
                lexnames[fields[0]] = fields[1]
    for filename in ("data.noun", "data.verb", "data.adj", "data.adv"):
        for line in (directory / filename).read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line[0].isspace() or " | " not in line:
                continue
            offset, raw_pos, pos, lexfile, words, definition, examples = parse_synset(line)
            for lemma in words:
                if lemma not in needed:
                    continue
                order = sense_order.get((lemma, pos), [])
                try:
                    rank = order.index(offset) + 1
                except ValueError:
                    rank = order.index(offset) + 1 if offset in order else len(records[lemma]) + 1
                records[lemma].append({
                    "id": f"wn30:{offset}-{raw_pos}",
                    "label": f"{lemma} · {pos} · sense {rank}",
                    "partOfSpeech": pos,
                    "rank": rank,
                    "lexicographerFile": lexnames.get(lexfile, lexfile),
                    "definition": definition,
                    "examples": examples,
                    "provenance": ["wordnet-3.0"],
                })
    entries = {}
    for lemma in sorted(needed):
        senses = records.get(lemma, [])
        senses.sort(key=lambda sense: (sense["partOfSpeech"], sense["rank"], sense["id"]))
        if senses:
            entries[lemma] = {"id": f"wn30:lemma:{lemma}", "headword": lemma, "senses": senses}
    form_links = {form: [dict(link, provenance=["wordnet-3.0"])
                         for link in links if link["lemma"] in entries]
                  for form, links in form_links.items()}
    form_links = {form: links for form, links in form_links.items() if links}
    payload = {
        "schema": "hrl.wordnet-kjv-subset/v1",
        "edition": "Princeton WordNet 3.0",
        "description": "Local dictionary senses and morphology links for forms found in the checked-in KJV corpus.",
        "provenance": {
            "wordnet-3.0": {
                "label": "Princeton WordNet 3.0",
                "type": "lexical-database",
                "author": "Cognitive Science Laboratory, Princeton University",
                "copyright": "WordNet 3.0 Copyright 2006 by Princeton University.",
                "license": "WordNet 3.0 license; see WORDNET-LICENSE.txt.",
                "url": "https://wordnet.princeton.edu/",
                "description": "Word senses, glosses, examples, part-of-speech labels, and morphological candidate links are transcribed from WordNet 3.0. Candidate senses are not automatically disambiguated by this reader.",
            }
        },
        "entries": entries,
        "surfaceForms": form_links,
        "buildStats": {
            "corpusUniqueForms": len(forms),
            "formsWithWordNetLinks": len(form_links),
            "distinctLinkedHeadwords": len(entries),
            "linkedSenses": sum(len(entry["senses"]) for entry in entries.values()),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload["buildStats"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wordnet_dir", type=Path, help="Path to Princeton WordNet 3.0 data files")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(build(args.wordnet_dir, args.output), indent=2))


if __name__ == "__main__":
    main()
