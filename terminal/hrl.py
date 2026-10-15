#!/usr/bin/env python3
"""Offline portfolio CLI and animated curses explorer; Python standard library only."""
import argparse
import curses
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
import textwrap
import time
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://rmichaelglover.github.io/hrl-portfolio/'


def catalog(query=''):
    entries = json.loads((ROOT / 'world-directory.json').read_text())
    words = query.casefold().split()
    return [e for e in entries if all(w in ' '.join(str(v) for v in e.values()).casefold() for w in words)]


def page_path(entry):
    path = (ROOT / entry['href']).resolve()
    if ROOT not in path.parents:
        raise ValueError('Page lies outside portfolio')
    return path / 'index.html' if path.is_dir() else path


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if not self.hidden and tag in ('p', 'div', 'h1', 'h2', 'h3', 'li', 'br', 'section'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
        if not self.hidden and tag in ('p', 'div', 'h1', 'h2', 'h3', 'li', 'section'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def read_page(entry):
    path = page_path(entry)
    if not path.is_file():
        return 'No local HTML page. Open the web version with o.\n' + BASE + entry['href']
    parser = PageText()
    parser.feed(path.read_text(errors='replace'))
    lines = [re.sub(r'\s+', ' ', line).strip() for line in ''.join(parser.parts).splitlines()]
    return '\n'.join(line for line in lines if line)


def knot(width, height, angle):
    """Perspective projection of a tubular trefoil with a depth buffer."""
    pixels = [[' '] * width for _ in range(height)]
    depth = [[-math.inf] * width for _ in range(height)]
    if width < 2 or height < 2:
        return [''.join(row) for row in pixels]
    ca, sa = math.cos(angle), math.sin(angle)
    scale = min(width / 8, height / 4)
    for i in range(220):
        t = i * math.tau / 220
        for j in range(12):
            v = j * math.tau / 12
            r = 2 + math.cos(3 * t) + .22 * math.cos(v)
            x, y, z = r * math.cos(2 * t), r * math.sin(2 * t), math.sin(3 * t) + .22 * math.sin(v)
            x, z = x * ca + z * sa, z * ca - x * sa
            y, z = y * .85 - z * .53, y * .53 + z * .85
            perspective = 5 / (7 - z)
            px = int(width / 2 + x * scale * perspective * 2)
            py = int(height / 2 - y * scale * perspective)
            if 0 <= px < width and 0 <= py < height and z > depth[py][px]:
                depth[py][px] = z
                pixels[py][px] = '.:-=+*#%@'[min(8, max(0, int((z + 3.5) * 1.4)))]
    return [''.join(row) for row in pixels]


def put(screen, y, x, text, attr=0):
    h, w = screen.getmaxyx()
    if 0 <= y < h and 0 <= x < w - 1:
        # HTML/control bytes must never become terminal commands.
        text = ''.join(c if c.isprintable() else ' ' for c in text)
        try:
            screen.addnstr(y, x, text, w - x - 1, attr)
        except curses.error:
            pass


def tui(screen):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.timeout(50)
    screen.keypad(True)
    query, selected, offset = '', 0, 0
    searching, reading, paused = False, False, False
    content, angle = '', 0.0
    while True:
        entries = catalog(query)
        selected = min(selected, max(0, len(entries) - 1))
        h, w = screen.getmaxyx()
        screen.erase()
        put(screen, 0, 0, 'HRL / terminal worlds', curses.A_BOLD)
        put(screen, 1, 0, 'q quit | / search | arrows select/scroll | Enter read | o browser | space pause')
        put(screen, 2, 0, ('SEARCH: ' if searching else 'Filter: ') + query)
        if h < 12 or w < 60:
            put(screen, 4, 0, 'Resize to at least 60 columns by 12 rows.')
        elif reading:
            wrapped = [part for line in content.splitlines() for part in (textwrap.wrap(line, w - 3) or [''])]
            offset = max(0, min(offset, max(0, len(wrapped) - (h - 5))))
            for row, line in enumerate(wrapped[offset:offset + h - 5], 4):
                put(screen, row, 1, line)
            put(screen, h - 1, 0, 'Esc back | arrows scroll | o open full interactive page')
        else:
            left = max(28, w // 2)
            count = h - 7
            start = max(0, selected - count + 1)
            for row, entry in enumerate(entries[start:start + count], 4):
                active = start + row - 4 == selected
                put(screen, row, 0, ('> ' if active else '  ') + entry['title'][:left - 3], curses.A_REVERSE if active else 0)
            for row, line in enumerate(knot(w - left - 1, h - 8, angle), 4):
                put(screen, row, left, line)
            if entries:
                put(screen, h - 3, 0, entries[selected]['category'])
                put(screen, h - 2, 0, entries[selected]['description'])
            put(screen, h - 1, 0, f'{len(entries)} directory entries | trefoil preview | browser scenes require adapters')
        screen.refresh()
        if not paused:
            angle += .035
        key = screen.getch()
        if key == -1:
            continue
        if searching:
            if key in (10, 13, 27):
                searching = False
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                query = query[:-1]
            elif 32 <= key <= 126:
                query += chr(key)
            selected = 0
        elif key == ord('q'):
            return
        elif key == 27:
            reading = False
        elif key == ord('/'):
            searching, reading = True, False
        elif key == ord(' '):
            paused = not paused
        elif key == curses.KEY_DOWN:
            if reading:
                offset += 1
            else:
                selected = min(selected + 1, len(entries) - 1)
        elif key == curses.KEY_UP:
            if reading:
                offset = max(0, offset - 1)
            else:
                selected = max(0, selected - 1)
        elif key in (10, 13) and entries:
            content, offset, reading = read_page(entries[selected]), 0, True
        elif key == ord('o') and entries:
            webbrowser.open(BASE + entries[selected]['href'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command')
    for name in ('list', 'read', 'open'):
        p = sub.add_parser(name)
        p.add_argument('query', nargs='*')
        if name == 'list':
            p.add_argument('--json', action='store_true')
    sub.add_parser('tui')
    p = sub.add_parser('render')
    p.add_argument('--frames', type=int, default=1)
    args = parser.parse_args()
    if args.command in (None, 'tui'):
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            parser.error('TUI needs an interactive terminal. Try list or render.')
        curses.wrapper(tui)
    elif args.command == 'render':
        if args.frames < 1:
            parser.error('--frames must be positive')
        try:
            for frame in range(args.frames):
                if sys.stdout.isatty() and args.frames > 1:
                    print('\033[H\033[2J', end='')
                print('\n'.join(knot(76, 24, frame * .08)))
                if args.frames > 1:
                    time.sleep(.05)
        except KeyboardInterrupt:
            pass
    else:
        entries = catalog(' '.join(args.query))
        if args.command == 'list':
            if args.json:
                print(json.dumps(entries, indent=2, ensure_ascii=False))
            else:
                for e in entries:
                    print(f"{e['title']}\n  {e['href']} — {e['description']}")
        elif len(entries) != 1:
            parser.error(f'{len(entries)} matches; use list to find a more specific query')
        elif args.command == 'read':
            print(read_page(entries[0]))
        else:
            webbrowser.open(BASE + entries[0]['href'])


if __name__ == '__main__':
    main()
