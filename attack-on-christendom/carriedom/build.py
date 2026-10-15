"""Render the standalone nonfiction Carriedom essay."""
from pathlib import Path
from html import escape
import markdown

ROOT = Path(__file__).resolve().parent
TITLE = "We’re All Just People: An Attack on Carriedom"
DESCRIPTION = "Humiliation never grants a right to kill: an appeal to people tempted by mass violence, extremist recruitment, or revenge against bullies."
BASE = "https://rmichaelglover.github.io/hrl-portfolio/attack-on-christendom/carriedom/"

def main():
    source = (ROOT / "essay.md").read_text()
    renderer = markdown.Markdown(extensions=["toc", "smarty"])
    body = renderer.convert(source.split("\n", 1)[1])
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Attack on Christendom</title><meta name="description" content="{escape(DESCRIPTION, quote=True)}">
<link rel="canonical" href="{BASE}"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESCRIPTION, quote=True)}"><meta property="og:type" content="article"><meta property="og:url" content="{BASE}"><meta name="twitter:card" content="summary">
<link rel="stylesheet" href="../journal.css"><link rel="stylesheet" href="../carrie-and-lilith/reading.css"></head>
<body><a class="skip" href="#reading">Skip to reading</a><main class="reader"><nav aria-label="Journal"><a href="../">Attack on Christendom</a><a href="../../">Portfolio</a><a href="essay.md">Text edition</a></nav>
<header><p class="eyebrow">Nonfiction · ethics &amp; ordinary life</p><h1>{escape(TITLE)}</h1><p class="standfirst">{escape(DESCRIPTION)}</p></header>
<aside class="contents" aria-label="Contents"><p>In this essay</p>{renderer.toc}</aside><article id="reading">{body}</article>
<footer><p>Michael Emanuel Glover &amp; Cypher · <time datetime="2026-10-15">October 15, 2026</time></p><p><a href="../#carriedom">Back to the journal</a> · <a href="../carrie-and-lilith/essay.html">Separate literary essay: Carrie, Emaline, and the Shared Conscience</a></p></footer></main></body></html>'''
    (ROOT / "index.html").write_text(page)
    print(f"Built Carriedom nonfiction essay ({len(source.split())} words).")

if __name__ == "__main__":
    main()
