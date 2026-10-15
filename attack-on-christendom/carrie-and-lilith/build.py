"""Render the standalone Carrie/Lilith reading room from its two manuscripts."""
from html import escape
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent
BASE = "https://rmichaelglover.github.io/hrl-portfolio/attack-on-christendom/carrie-and-lilith/"
NAV = '<nav aria-label="Reading room"><a href="../">The journal</a><a href="./">Carrie &amp; Lilith</a><a href="essay.html">The essay</a><a href="story.html">The story</a><a href="../../">Portfolio</a></nav>'
FOOT = '<footer><p>Michael Emanuel Glover &amp; Cypher · <time datetime="2026-10-15">October 15, 2026</time> · Independent literary criticism and unofficial fanfiction.</p><p><a href="../mary-comes-to-roost/">Earlier Carrie fiction: Mary Comes to Roost</a> · <a href="../#carrie-and-lilith">Back to the journal</a></p></footer>'


def shell(title, description, filename, body, kind="article", layout="reader"):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | Attack on Christendom</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{BASE}{filename}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:type" content="{kind}"><meta property="og:url" content="{BASE}{filename}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}">
<link rel="stylesheet" href="../journal.css"><link rel="stylesheet" href="reading.css"></head>
<body><a class="skip" href="#reading">Skip to reading</a><main class="{layout}">{NAV}{body}{FOOT}</main></body></html>
'''


def manuscript(source, destination, description, label, companion, companion_label):
    text = (ROOT / source).read_text()
    title_line, body = text.split("\n", 1)
    title = title_line.removeprefix("# ").strip()
    renderer = markdown.Markdown(extensions=["toc", "smarty"], output_format="html")
    rendered = renderer.convert(body)
    word_count = len(text.split())
    minutes = max(1, round(word_count / 220))
    content = f'''<header><p class="eyebrow">{label}</p><h1>{escape(title)}</h1><p class="standfirst">{escape(description)}</p><p class="meta">About {minutes} minutes · <a href="{source}">Text edition</a> · <a href="{companion}">{companion_label}</a></p></header>
<aside class="contents" aria-label="Contents"><p>In this reading</p>{renderer.toc}</aside>
<article id="reading">{rendered}</article>
<section class="related" aria-label="Continue reading"><p><a class="read" href="{companion}">{companion_label} →</a> · <a href="./">Reading room</a></p></section>'''
    (ROOT / destination).write_text(shell(title, description, destination, content))
    return word_count


def main():
    essay_count = manuscript("essay.md", "essay.html",
        "Shared agency, wrath, forgiveness, and the friend through whom Carrie sometimes hears her own conscience.",
        "Literary criticism · personal theology · finale spoilers", "story.html", "Read the standalone fiction")
    story_count = manuscript("story.md", "story.html",
        "Carrie and Emaline arrive in a flooded town with an unwanted letter, a borrowed car, and unfinished business with their own hands.",
        "Standalone fanfiction · six chapters · first edition", "essay.html", "Read the companion essay")
    body = '''<header id="reading"><p class="eyebrow">Attack on Christendom · a new reading room</p>
<h1>Carrie &amp; Lilith</h1><p class="standfirst">Conscience, wrath, forgiveness, and the road beyond the fire.</p>
<p class="byline">Michael Emanuel Glover &amp; Cypher · October 15, 2026</p>
<svg class="road" viewBox="0 0 140 30" role="img" aria-label="Two paths joining an open road"><path d="M2 3 Q35 3 55 15 T138 15 M2 27 Q35 27 55 15" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="108" cy="15" r="9" fill="none" stroke="currentColor"/></svg>
<p>Our discussion began with Lilith and became a question about friendship: what happens when another person gives a voice to the part of yourself you can scarcely hear?</p></header>
<div class="pair"><article aria-labelledby="essay-title"><p class="eyebrow">Nonfiction · criticism &amp; interpretation</p><h2 id="essay-title"><a href="essay.html">Carrie, Emaline, and the Shared Conscience</a></h2>
<p>Carrie remains the greater moral authority in our reading. Emaline can still help her find courage, speak with her anger, or confront something she cannot govern. Their shared actions leave questions that neither can answer alone.</p><p>Includes source notes, the limits of the adaptation evidence, and a personal comparison with Jewish, Christian, and Muslim themes.</p><p><a class="read" href="essay.html">Read the essay →</a> · <a href="essay.md">Text</a></p></article>
<article aria-labelledby="story-title"><p class="eyebrow">Fiction · an independent alternate universe</p><h2 id="story-title"><a href="story.html">The Road Beyond the Fire</a></h2>
<p>Six chapters: a flood rescue, a visitor with an inherited claim, a game that really ends in stalemate, and the work waiting in the morning. Emaline is Lilith in this telling. Carrie must still answer for how she uses her earthly divinity.</p><p>A complete first journey, inspired by the ordinary tenderness and unease of our earlier Carrie material.</p><p><a class="read" href="story.html">Read the six chapters →</a> · <a href="story.md">Text</a></p></article></div>
<aside class="notice"><p><strong>Two kinds of writing.</strong> The essay is nonfiction criticism and explicitly identified personal theology. The story is unofficial fanfiction, separate from <em>Mary Comes to Roost</em> and official continuity. Emaline’s Lilith identity and supernatural ancestry are inventions for this version.</p><p>Finale spoilers; grief, conflict, and supernatural danger. No graphic injury.</p></aside>'''
    (ROOT / "index.html").write_text(shell("Carrie & Lilith — Conscience and the Open Road",
        "A sourced essay and a standalone six-chapter Carrie and Emaline story about shared conscience, Lilith, wrath, and forgiveness.",
        "", body, kind="website", layout="shelf"))
    print(f"Built reading room, essay ({essay_count} words), and six-chapter story ({story_count} words).")


if __name__ == "__main__":
    main()
