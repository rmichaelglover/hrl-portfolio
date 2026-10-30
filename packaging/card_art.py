"""Give every homepage destination card a local, subject-specific visual.

Existing illustrations stay in place. Destination artwork is preferred to the
small generated SVG scenes. No remote image requests or runtime HTML rewriting.
"""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/card-art'
OVERRIDES = {
    'chess/recent/2026-10-30/eastern-bullet/': 'chess/recent/2026-10-30/eastern-bullet/cover.svg',
    'capture-tutor/': 'assets/social/capture-tutor--index.png',
    'calabi-yau-vane/': 'assets/thumbs/calabi-yau-vane.jpg',
    'promaster-grrle/': 'promaster-grrle/assets/promaster-1500-front-left.jpg',
    'whimsy-chess/': 'whimsy-chess/media/maestro_kadas.gif',
    'body-pos/': 'assets/body_pos.png',
    'genesis/sdss/': 'assets/thumbs/sdss.png',
    'genesis/sparc/': 'assets/thumbs/sparc.png',
    'genesis/rar/': 'assets/thumbs/rar.png',
    'genesis/brain/': 'assets/thumbs/brain.png',
    'genesis/cord/': 'assets/thumbs/cord.png',
    'genesis/forecast/': 'assets/thumbs/forecast.png',
    'genesis/planck/': 'assets/thumbs/planck.png',
    'genesis/ontology/': 'assets/thumbs/ontology.png',
}


def motif_for(route, title):
    specific = {
        'fair-oaks/world/': 'oak', 'fair-oaks/': 'oak',
        'lion-and-the-lamb/world/': 'coexist', 'lion-and-the-lamb/': 'coexist',
        'rolling-chess-ros/': 'rolling', 'data-worlds/': 'voxels',
        'play/': 'cells-grid',
    }
    if route in specific:
        return specific[route]
    text = (route + ' ' + title).lower()
    rules = [
        ('cell', ('virtual-cell', 'virtual-body', 'cancer', 'biology', 'morphogenesis')),
        ('river', ('riverbank', 'last ferry')),
        ('fox-chess', ('tiny-creek-chess', 'woodland', 'storybook', 'whimsy-chess/novella')),
        ('atlas-chess', ('worlds-of-kings', 'geographic chess')),
        ('puzzle', ('no-choice', 'capture-tutor', 'missed-mate', 'puzzle', 'premove')),
        ('knight', ('stalemate', 'chess', 'maestro', 'relaxfish', 'ultrabullet', 'stockfish')),
        ('reef', ('reef', 'ocean', 'waterize', 'water cycle')),
        ('islands', ('isles', 'floating', 'terraform')),
        ('forest', ('tiny-creek-world', 'fair-oaks', 'garden', 'st-james', 'elbie', 'gooblet', 'critter', 'world/', 'worlds/')),
        ('earth', ('earth', 'atlas', 'humanity', 'lion-and-the-lamb', 'atlanta', 'malaria')),
        ('space', ('oort', 'halo', 'galaxy', 'cosmic', 'sparc', 'sdss', 'planck', 'gravity', 'genesis/light')),
        ('waves', ('wave', 'sound', 'hyperobject')),
        ('music', ('music', 'songs', 'hrlized', 'follows', 'kernel')),
        ('books', ('reader', 'bible', 'gospel', 'james', 'faith', 'shrine', 'ecc-', 'gospel')),
        ('theatre', ('authors', 'thursday', 'quorum', 'christendom', 'novella', 'panzer', 'perfect-union', 'cuento', 'red-thread', 'narrative')),
        ('community', ('community', 'people', 'gay-georgia', 'cv/', 'chronology', 'education')),
        ('train', ('beena', 'train', 'brake')),
        ('vision', ('vision', 'ellipse', 'promaster', 'body-pos', 'mocap')),
        ('language', ('wiki', 'language', 'numerological', 'words', 'grounding')),
        ('economics', ('econom', 'spreadsheet', 'finance', 'business', 'forecast', 'biz-viz')),
        ('shield', ('cyber', 'white-hat', 'hacker', 'licens', 'terms', 'trust')),
        ('code', ('github', 'cpp', 'python', 'linux', 'terminal', 'engine', 'source', 'code')),
        ('geometry', ('quant', 'penrose', 'projective', 'simplic', 'calabi', 'geometry', 'hyperspace', 'formula')),
        ('cells-grid', ('cellular', 'emoji-life', 'conway')),
        ('network', ('renormal', 'label', 'consensus', 'relax', 'finalization', 'tensor', 'compatibility', 'graph', 'neural')),
        ('books', ('paper', 'dissertation', 'report', 'essay', 'manuscript', 'opus', 'wall', 'mother-god', 'all-in-a-day')),
    ]
    return next((name for name, words in rules if any(word in text for word in words)), 'network')


DESCRIPTIONS = {
    'oak': 'A broad oak canopy, a little schoolhouse and a winding garden path',
    'coexist': 'A lion and lamb sharing a green landscape beside a blue globe',
    'rolling': 'A tilted wooden chess maze with pieces, metal marbles and curved paths',
    'voxels': 'Colorful stacks of small cubes forming an explorable voxel landscape',
    'cell': 'A luminous cell with folded organelles and two colored DNA compartments',
    'river': 'Chess pieces finding stepping stones across a winding blue river',
    'fox-chess': 'A woodland fox beside a colorful chessboard and knight',
    'atlas-chess': 'Chess towers and routes across an illustrated globe',
    'puzzle': 'A chessboard with a highlighted move and a curious knight',
    'knight': 'An ivory chess knight overlooking a colorful patterned board',
    'reef': 'Coral, kelp and tiny fish in a glowing underwater world',
    'islands': 'Floating green islands with trees and lanterns under a glowing moon',
    'forest': 'A welcoming little forest with a garden path and a fox',
    'earth': 'A blue globe with land, orbiting routes and a bright sunrise',
    'space': 'Orbiting worlds, stars and a spiral of galactic light',
    'waves': 'Colorful wave fronts traveling across a luminous sound field',
    'music': 'A bright melody, flowing notes and a miniature piano keyboard',
    'books': 'Open books, warm lamplight and a constellation of ideas',
    'theatre': 'An open stage, illustrated book and warm pools of theatrical light',
    'community': 'A circle of colorful people gathered around a shared table',
    'train': 'A small train on a curved rail with visible wheels and brake mechanism',
    'vision': 'A camera lens, tracking points and a colorful geometric object',
    'language': 'Speech bubbles and letter tiles linked by a web of connections',
    'economics': 'A rising chart, a table of values and stacks of golden coins',
    'shield': 'A glowing shield protecting a network of connected points',
    'code': 'A luminous terminal window with code brackets and connected modules',
    'geometry': 'Intersecting polyhedra, orbital curves and a bright geometric center',
    'cells-grid': 'A colorful cellular grid with neighboring patterns and a growing cluster',
    'network': 'Colored nodes and paths forming a layered web of connected ideas',
}


def scene(motif, seed):
    palettes = [('#122a3c','#72dfc2','#f3c98b','#a59ae1'),
                ('#24304c','#83c9eb','#f2b6be','#b0df9b'),
                ('#193d3b','#9cdeb4','#efbd86','#9ebbdc'),
                ('#352b48','#c9a3e4','#f5d79b','#84d3cb')]
    bg, mint, gold, lilac = palettes[seed % len(palettes)]
    a = []
    def add(s): a.append(s)
    def circle(x,y,r,fill,extra=''): add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {extra}/>')
    def path(d,stroke=mint,width=3,fill='none',extra=''): add(f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')
    def tree(x,y,scale=1):
        add(f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 0v-65" stroke="#b6926d" stroke-width="7"/><path d="M-32-25L0-91l32 66h-16l21 26h-74l21-26z" fill="{mint}"/><path d="M0-75v65" stroke="#234945" stroke-width="2" opacity=".35"/></g>')
    def fox(x,y,scale=1):
        add(f'<g transform="translate({x} {y}) scale({scale})"><path d="M-43-20l8-48 25 23Q3-51 16-44l26-25 6 50L8 20z" fill="#e4a46f"/><path d="M-43-20L0 4l48-23L8 20z" fill="#fff0ce"/><circle cx="-17" cy="-18" r="3" fill="#18332f"/><circle cx="23" cy="-18" r="3" fill="#18332f"/><path d="M-3 3h13L5 12z" fill="#18332f"/></g>')
    def board(x=210,y=174,w=260,h=140):
        add(f'<g transform="translate({x} {y}) skewX(-22)">')
        for r in range(6):
            for c in range(6):
                fill=gold if (r+c)%2==0 else '#4c786f'
                add(f'<rect x="{c*w/6:.1f}" y="{r*h/6:.1f}" width="{w/6+.5:.1f}" height="{h/6+.5:.1f}" fill="{fill}"/>')
        add('</g>')
    def knight(x,y,scale=1):
        add(f'<g transform="translate({x} {y}) scale({scale})"><path d="M-52 43h103l-8-13H-44z" fill="#e8d6b1"/><path d="M-39 22q5-44 40-65l-32 9-15-20 25-30 2-24 20 14 17-5q30 19 25 58l-11 63z" fill="#fff1cf" stroke="#9f9e89" stroke-width="2"/><path d="M-21-75l18 4M-27-42l22-11" stroke="#526366" stroke-width="4" stroke-linecap="round"/><path d="M15-70q22 42-7 83" fill="none" stroke="#d5c19b" stroke-width="4"/></g>')
    def globe(x=330,y=170,r=110):
        circle(x,y,r,'#3c7b94')
        add(f'<g clip-path="url(#globe-clip)"><path d="M{x-r} {y-60}l65-25 45 27-28 34 24 35-56 19-28-33-27 7zM{x+20} {y-75}l62-12 32 48-18 32-29-6-20 38-33-29zM{x-5} {y+5}l49 20-3 38-28 38-26-31z" fill="{mint}"/></g>')
        for dx in [-r*.55,0,r*.55]:
            add(f'<ellipse cx="{x}" cy="{y}" rx="{r*.42 if dx==0 else r*.8}" ry="{r}" fill="none" stroke="#b8e8de" opacity=".2"/>')
            if dx==0:break
        path(f'M{x-r} {y}h{2*r}', '#b8e8de',1,extra='opacity=".3"')
        add(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*.4}" fill="none" stroke="#b8e8de" opacity=".3"/>')
    def book(x,y,scale=1):
        add(f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 3q-60-35-116-16v-111Q-57-142 0-102q57-40 116-22v111Q60-32 0 3z" fill="#f0ddb4" stroke="#bbac94" stroke-width="2"/><path d="M0-102V3" stroke="#a48b75" stroke-width="3"/><path d="M-91-96q37-6 66 12m-66 14q37-5 66 11m-66 14q37-4 66 11M25-85q29-15 66-12M25-59q29-14 66-12M25-34q29-13 66-12" fill="none" stroke="#a18c72" stroke-width="4" stroke-linecap="round"/></g>')
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360"><defs><radialGradient id="bg"><stop stop-color="{bg}"/><stop offset="1" stop-color="#0c1b2a"/></radialGradient><linearGradient id="floor" x2="0" y2="1"><stop stop-color="{mint}" stop-opacity=".2"/><stop offset="1" stop-color="{mint}" stop-opacity="0"/></linearGradient><clipPath id="globe-clip"><circle cx="330" cy="170" r="110"/></clipPath></defs><rect width="640" height="360" fill="url(#bg)"/>')
    for i in range(19):
        x=(i*97+seed*17)%620+10;y=(i*53+seed*7)%330+10
        circle(x,y,1+(i%3)*.5,'#d4efe8',f'opacity="{.12+(i%4)*.06}"')
    add(f'<ellipse cx="320" cy="345" rx="280" ry="100" fill="url(#floor)"/>')
    if motif=='oak':
        path('M0 291q140-57 320-4t320-21v94H0z','#3f6b62',0,'#3f6b62')
        path('M325 360q-46-49 3-80',gold,18)
        for x,y,sc in [(155,256,1.2),(491,249,.9)]:
            path(f'M{x} {y}v-100','#aa8a63',11)
            for dx,dy,r in [(-30,-83,39),(25,-88,44),(0,-122,45)]:circle(x+dx*sc,y+dy*sc,r*sc,mint)
            path(f'M{x} {y-55}l-20-30m20 16 20-27','#aa8a63',5)
        add(f'<rect x="270" y="212" width="118" height="75" rx="4" fill="#d6aa7e"/><path d="M256 214l73-57 73 57z" fill="{lilac}"/><rect x="317" y="249" width="25" height="38" rx="11" fill="#284b4a"/><rect x="281" y="232" width="19" height="20" fill="{gold}"/><rect x="359" y="232" width="19" height="20" fill="{gold}"/>')
    elif motif=='coexist':
        globe();path('M0 303q160-70 320-20t320-13v90H0z','#436c57',0,'#436c57')
        # Animal silhouettes are illustrative, not a species-range map.
        add(f'<ellipse cx="204" cy="279" rx="45" ry="22" fill="#d9b27e"/><path d="M176 282v35m43-34v34" stroke="#d9b27e" stroke-width="11" stroke-linecap="round"/>')
        circle(168,248,33,'#a98158');circle(168,248,21,gold);circle(161,244,2,'#24413d');circle(175,244,2,'#24413d');path('M163 254l5 4 5-4','#614a37',2)
        add('<ellipse cx="439" cy="288" rx="35" ry="22" fill="#ecebd6"/><path d="M417 295v22m38-22v22" stroke="#c9cdb9" stroke-width="7" stroke-linecap="round"/><ellipse cx="468" cy="278" rx="14" ry="19" fill="#d9d4bf"/>');circle(473,274,2,'#24413d')
    elif motif=='voxels':
        for r in range(4):
            for c in range(6):
                h=(r*3+c*2+seed)%4+1;x=160+c*51+r*24;y=265-r*26
                for level in range(h):
                    yy=y-level*27
                    add(f'<path d="M{x} {yy}l25-13 25 13-25 13z" fill="{mint}"/><path d="M{x} {yy}v26l25 13v-26z" fill="#487a72"/><path d="M{x+25} {yy+13}l25-13v26l-25 13z" fill="{lilac}"/>')
    elif motif=='rolling':
        board(200,139,300,165)
        path('M203 193l98 0 0 28 105 0m-176 56h140l0-26 78 0','#845f45',8)
        for x,y in [(254,225),(390,183),(414,271)]:circle(x,y,10,'#163734',f'stroke="{gold}" stroke-width="3"')
        knight(356,134,.65)
        for x,y in [(226,175),(376,258)]:circle(x,y,13,'#a3b7b8',f'stroke="#dfe9db" stroke-width="2"');circle(x-4,y-5,4,'#f4fff7')
        path('M128 292q-30-94 32-142m-20 12 20-12 2 24',mint,3)
    elif motif in ('knight','puzzle','fox-chess'):
        board(185,210,310,110)
        if motif=='fox-chess':
            tree(110,245,1.3);tree(548,240,1.6);fox(240,187,.95);knight(405,190,.85)
        else:
            knight(330,185,1.15)
            if motif=='puzzle':
                path('M180 270h80l32-35',gold,5);circle(292,235,8,gold)
                add(f'<path d="M476 90q33-31 52-5t-17 35v18" fill="none" stroke="{gold}" stroke-width="9" stroke-linecap="round"/>');circle(509,156,5,gold)
            else:
                circle(460,92,38,'none',f'stroke="{mint}" stroke-width="2" opacity=".3"');path('M450 92l9 9 18-23',mint,4)
    elif motif=='atlas-chess':
        globe();add(f'<ellipse cx="330" cy="188" rx="183" ry="53" transform="rotate(-22 330 188)" fill="none" stroke="{gold}" stroke-width="3" stroke-dasharray="7 9"/>')
        for x,y,sc in [(177,245,1),(467,142,.8)]:
            add(f'<g transform="translate({x} {y}) scale({sc})"><path d="M-35 10h70v-12H24V-52l12-12v-21H18v13H7v-13H-7v13h-11v-13h-18v21l12 12v50h-11z" fill="{gold}" stroke="#927a63" stroke-width="2"/></g>')
    elif motif=='cell':
        for x,y,r in [(357,177,118),(163,226,42)]:
            circle(x,y,r+10,'none',f'stroke="#efa9b7" stroke-width="12" opacity=".2"');circle(x,y,r,'#6c536d',f'stroke="#efa9b7" stroke-width="3"')
        for x,y in [(310,129),(398,206),(330,253)]:
            add(f'<ellipse cx="{x}" cy="{y}" rx="22" ry="11" transform="rotate(-25 {x} {y})" fill="{mint}"/>');path(f'M{x-13} {y}l7-5 6 9 7-8 6 5','#3b746d',2)
        path('M297 157q-35 13-16 47t21 15M305 169q-26 12-11 35',lilac,7)
        circle(341,181,31,'#f7c68533',f'stroke="{gold}" stroke-width="2"');circle(402,164,27,'#a6e9d122',f'stroke="{mint}" stroke-width="2"')
        path('M329 176q24-14 9 12t16 4',gold,4);path('M389 157q23-12 10 10t13 6',mint,4)
        path('M477 178q36-28 65-2t63-9',mint,5)
    elif motif in ('forest','islands'):
        if motif=='forest':
            path('M0 268Q130 180 280 241t360-22v141H0z','#406b64',0,'#406b64');path('M0 313q200-100 640-23v70H0z','#284e48',0,'#284e48')
            path('M316 360q-103-44-19-104t-2-30',gold,17,extra='opacity=".65"')
            for x,y,sc in [(86,262,1.2),(170,253,1.8),(470,262,1.8),(555,280,1.1)]:tree(x,y,sc)
            fox(350,285,.6)
        else:
            circle(500,77,30,gold)
            for x,y,sc in [(245,217,1.3),(465,157,.8),(117,116,.55)]:
                add(f'<g transform="translate({x} {y}) scale({sc})"><path d="M-100 0l44 65 54 22L92 0z" fill="#4d646e"/><ellipse rx="100" ry="23" fill="{mint}"/></g>');tree(x-12,y-7,sc*.8)
            path('M342 215q47-95 68-61',gold,2,extra='stroke-dasharray="4 7"')
    elif motif=='reef':
        for i in range(5):path(f'M{40+i*130} 0q-50 150 25 360',mint,22,extra='opacity=".035"')
        path('M0 320q140-38 300 0t340-10v50H0z','#224c5b',0,'#224c5b')
        for x,y in [(110,310),(190,330),(470,330),(560,310)]:
            path(f'M{x} {y}q-30-70 0-133m0 80q-50-15-40-52m40 32q46-14 41-48',lilac if x%3 else gold,9)
        for x,y in [(287,118),(382,193),(300,245)]:
            add(f'<ellipse cx="{x}" cy="{y}" rx="29" ry="13" fill="{gold}"/><path d="M{x+22} {y}l23-17v34z" fill="{gold}"/>');circle(x-15,y-3,2,'#183140')
        for i in range(6):circle(65+i*87,60+(i*31)%170,4,'none',f'stroke="{mint}" opacity=".5"')
    elif motif=='river':
        path('M-30 118Q177 55 300 180T670 235', '#4b9fc2',105)
        for x,y in [(190,142),(320,195),(445,217)]:
            add(f'<ellipse cx="{x}" cy="{y+6}" rx="44" ry="19" fill="#274955"/><ellipse cx="{x}" cy="{y}" rx="44" ry="16" fill="#b6c8b7"/>')
        knight(180,124,.47);path('M218 119q34-60 88 43m30 13q41-56 85 9',gold,3,extra='stroke-dasharray="5 7"')
        tree(67,300,.7);tree(563,124,.7)
    elif motif in ('earth','space'):
        if motif=='earth':globe();circle(507,90,31,gold)
        else:
            circle(320,180,24,gold)
            for r in [67,109,153]:add(f'<ellipse cx="320" cy="180" rx="{r*1.4}" ry="{r*.55}" transform="rotate(-22 320 180)" fill="none" stroke="{mint}" opacity=".4" stroke-width="2"/>')
            for x,y,r,c in [(192,178,19,mint),(439,136,24,lilac),(481,227,12,gold)]:circle(x,y,r,c)
            for n in range(60):
                angle=n*.52;radius=10+n*2.3
                circle(round(320+math.cos(angle)*radius*1.8,1),round(180+math.sin(angle)*radius*.55,1),1.8,lilac,'opacity=".5"')
    elif motif in ('music','waves'):
        for i in range(5):
            y=92+i*35;path(f'M65 {y}q65-70 130 0t130 0 130 0 130 0',[mint,gold,lilac][i%3],3,extra=f'opacity="{.9-i*.12}"')
        if motif=='music':
            for i in range(13):
                x=177+i*23;add(f'<rect x="{x}" y="252" width="21" height="63" rx="3" fill="#f3e4c7"/>')
                if i%7 not in [2,6]:add(f'<rect x="{x+16}" y="252" width="11" height="36" rx="2" fill="#1b3540"/>')
            for x,y in [(226,112),(396,170)]:
                path(f'M{x} {y}v-59l37-9v55',gold,6);add(f'<ellipse cx="{x-10}" cy="{y}" rx="15" ry="10" transform="rotate(-20 {x-10} {y})" fill="{gold}"/><ellipse cx="{x+27}" cy="{y-13}" rx="15" ry="10" fill="{gold}"/>')
    elif motif in ('books','theatre'):
        if motif=='theatre':
            path('M0 0h148q-5 140-85 228H0z','#86546e',0,'#86546e');path('M640 0H492q5 140 85 228h63z','#86546e',0,'#86546e')
            path('M140 0L320 290 500 0','#f3cf8b',0,'#f3cf8b',extra='opacity=".07"')
            path('M45 325h550',gold,7)
        else:
            path('M140 271l-21 24h409l-22-24',gold,3)
            circle(486,105,28,gold,'opacity=".8"');path('M486 135v105m-29 0h58',gold,5)
        book(321,283,1.15)
    elif motif=='community':
        add(f'<ellipse cx="320" cy="248" rx="165" ry="58" fill="#466c72" stroke="{mint}" stroke-width="2"/>')
        for x,y,c in [(210,153,mint),(320,111,gold),(431,153,lilac),(320,284,'#edb3b8')]:
            circle(x,y,23,c);path(f'M{x-30} {y+55}q-1-34 30-34t30 34',c,0,c)
        path('M266 240h107',gold,3);circle(320,237,12,gold)
    elif motif=='train':
        path('M0 312q250-59 640 0','#b8b6a0',7);path('M0 326q250-59 640 0','#b8b6a0',4)
        add(f'<rect x="178" y="148" width="254" height="109" rx="16" fill="{mint}"/><rect x="351" y="100" width="77" height="120" rx="8" fill="{lilac}"/><rect x="364" y="114" width="48" height="53" rx="4" fill="#244752"/><path d="M172 257h303l-35-48h-27" fill="{gold}"/><path d="M217 151v-51h36v51" fill="{gold}"/>')
        for x in [221,299,385]:circle(x,263,26,'#17323a',f'stroke="{gold}" stroke-width="5"')
        path('M220 263h165',gold,7)
        for x,y,r in [(236,71,13),(266,49,19),(310,29,26)]:circle(x,y,r,'#a8d0c7','opacity=".25"')
    elif motif=='vision':
        add(f'<rect x="145" y="99" width="350" height="195" rx="25" fill="#294c58" stroke="{mint}" stroke-width="2"/><path d="M181 99l27-34h96l28 34" fill="#466570"/>')
        circle(331,196,73,'#152b3a',f'stroke="{lilac}" stroke-width="10"');circle(331,196,43,'#4b7894',f'stroke="{mint}" stroke-width="2"');circle(313,177,15,'#d7fff0','opacity=".4"')
        for x,y in [(144,98),(494,98),(144,293),(494,293)]:circle(x,y,6,gold)
        path('M112 131v-49h50m365 49V82h-50M112 263v49h50m365-49v49h-50',gold,3)
    elif motif=='language':
        for x,y,w,c in [(134,98,170,mint),(321,167,180,lilac)]:
            add(f'<path d="M{x} {y}h{w}v81h-42l-28 27v-27h-{w-70}z" fill="{c}"/>')
        add('<text x="160" y="151" fill="#19323b" font-family="Georgia,serif" font-size="39">A B C</text><text x="352" y="219" fill="#24304b" font-family="Georgia,serif" font-size="38">a ↔ b</text>')
        path('M187 227q-12 80 118 55m197-154q45-51-30-75',gold,3,extra='stroke-dasharray="5 8"')
    elif motif=='economics':
        add(f'<rect x="116" y="71" width="327" height="220" rx="13" fill="#1c3944" stroke="{mint}" stroke-width="2"/>')
        for i,h in enumerate([41,83,66,121,160]):add(f'<rect x="{150+i*50}" y="{262-h}" width="25" height="{h}" rx="4" fill="{mint if i%2 else lilac}" opacity=".8"/>')
        path('M145 226l56-53 48 20 56-74 59-27',gold,4)
        for x,n in [(465,4),(511,6)]:
            for j in range(n):add(f'<ellipse cx="{x}" cy="{286-j*13}" rx="27" ry="10" fill="{gold}" stroke="#aa845a" stroke-width="2"/>')
    elif motif=='shield':
        for x,y in [(134,107),(500,103),(114,256),(526,263)]:path(f'M{x} {y}L320 181',mint,2,extra='opacity=".5"');circle(x,y,11,lilac)
        path('M320 61l107 37v75q-5 80-107 132-102-52-107-132V98z',mint,3,'#31595b')
        path('M267 181l35 35 71-82',gold,12)
    elif motif=='code':
        add(f'<rect x="117" y="64" width="406" height="231" rx="16" fill="#112938" stroke="{mint}" stroke-width="2"/><path d="M118 106h404" stroke="{mint}" opacity=".3"/>')
        for x,c in [(142,'#e9b3b9'),(161,gold),(180,mint)]:circle(x,84,5,c)
        path('M236 150l-49 36 49 37m170-73 49 36-49 37m-55-87-38 102',mint,7)
        path('M245 273h151',lilac,4)
    elif motif=='cells-grid':
        for r in range(6):
            for c in range(10):
                active=(r*c+c+seed)%7<3
                fill=[mint,lilac,gold][(r+c)%3] if active else '#2c4753'
                add(f'<rect x="{117+c*41}" y="{59+r*41}" width="35" height="35" rx="6" fill="{fill}" opacity="{.9 if active else .5}"/>')
    elif motif=='geometry':
        points=[(320,52),(476,149),(417,295),(223,295),(164,149)]
        for i,(x,y) in enumerate(points):
            for xx,yy in points[i+1:]:path(f'M{x} {y}L{xx} {yy}',mint,2,extra='opacity=".65"')
            circle(x,y,7,gold)
        add(f'<ellipse cx="320" cy="180" rx="209" ry="78" transform="rotate(-20 320 180)" fill="none" stroke="{lilac}" stroke-width="3" opacity=".5"/>');circle(320,180,23,gold)
    else:
        points=[(128,173),(222,91),(249,253),(338,163),(414,76),(498,228),(533,125),(377,295)]
        for i,(x,y) in enumerate(points):
            for j,(xx,yy) in enumerate(points):
                if i<j and (i+j+seed)%3==0:path(f'M{x} {y}Q320 180 {xx} {yy}',mint,2,extra='opacity=".4"')
        for i,(x,y) in enumerate(points):
            circle(x,y,21 if i==3 else 12,[mint,lilac,gold][(i+seed)%3]);circle(x,y,29 if i==3 else 18,'none',f'stroke="{mint}" opacity=".2"')
    add('<rect x=".5" y=".5" width="639" height="359" rx="1" fill="none" stroke="#e3fff0" opacity=".08"/></svg>')
    return ''.join(a)


class AnchorRanges(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source=source; self.lines=[0];self.stack=[];self.cards=[]
        self.lines.extend(m.end() for m in re.finditer('\n',source))
        self.feed(source)
    def source_offset(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);classes=set(attrs.get('class','').split())
        selected=tag=='a' and ('href' in attrs) and (bool(classes & {'card','discovery','variant-door','world-feature'}) or any(s['classes'] & {'world-links','more'} for s in self.stack))
        item={'tag':tag,'attrs':attrs,'classes':classes,'start':self.source_offset(),'open_end':self.source_offset()+len(self.get_starttag_text()),'selected':selected}
        if tag not in self.VOID:self.stack.append(item)
    def handle_startendtag(self,tag,attrs):pass
    def handle_endtag(self,tag):
        index=next((n for n in range(len(self.stack)-1,-1,-1) if self.stack[n]['tag']==tag),None)
        if index is None:return
        item=self.stack[index]
        if item['selected']:
            item['close_start']=self.source_offset();item['end']=self.source.find('>',self.source_offset())+1;self.cards.append(item)
        del self.stack[index:]


def title_of(body):
    match=re.search(r'<(?:strong|h[23])\b[^>]*>(.*?)</(?:strong|h[23])>',body,re.S)
    text=match[1] if match else body.split('<span')[0]
    return ' '.join(unescape(re.sub('<[^>]+>',' ',text)).split()) or 'Explore this project'


class CardIllustrator:
    def __init__(self):
        ART.mkdir(exist_ok=True)
        self.manifest={};self.added=0;self.existing=0
    def image_for(self,href,title):
        parsed=urlsplit(unescape(href));route=unquote(parsed.path).removeprefix('/hrl-portfolio/').lstrip('/')
        motif=motif_for(route,title)
        if route in self.manifest:return self.manifest[route]
        image=OVERRIDES.get(route)
        # Prefer destination illustrations, never incidental UI icons or generated social covers.
        candidate=ROOT/route
        if candidate.is_dir():candidate=candidate/'index.html'
        if not image and candidate.is_file() and candidate.suffix=='.html':
            page=candidate.read_text(errors='replace')
            for src in re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)',page,re.I):
                if src.startswith(('data:','http','/')):continue
                asset=(candidate.parent/unquote(src.split('?')[0])).resolve()
                if ROOT not in asset.parents or not asset.is_file():continue
                if asset.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):continue
                if any(word in str(asset.relative_to(ROOT)).lower() for word in ('icon','flag','social/','sprite','logo','tracking')):continue
                if asset.stat().st_size<18000:continue
                image=asset.relative_to(ROOT).as_posix();break
        if image and not (ROOT/image).is_file():image=None
        if image:
            alt=f'Artwork from {title}'
            kind='existing destination artwork'
        else:
            key=hashlib.sha256(route.encode()).hexdigest()
            slug=re.sub('[^a-z0-9]+','-',route.lower()).strip('-')[:72] or 'project'
            image=f'assets/card-art/{slug}-{key[:7]}.svg'
            (ROOT/image).write_text(scene(motif,int(key[:8],16)))
            alt=DESCRIPTIONS[motif];kind='original SVG illustration'
        entry={'route':route,'title':title,'image':image,'alt':alt,'motif':motif,'kind':kind}
        self.manifest[route]=entry
        return entry
    def decorate(self,source):
        ranges=AnchorRanges(source).cards
        for card in sorted(ranges,key=lambda c:c['start'],reverse=True):
            body=source[card['open_end']:card['close_start']]
            if re.search(r'<(?:img|svg)\b',body,re.I):
                self.existing+=1;continue
            href=card['attrs']['href'];title=title_of(body)
            entry=self.image_for(href,title)
            img=f'<img class="card-art" src="{escape(entry["image"],quote=True)}" alt="{escape(entry["alt"],quote=True)}" width="640" height="360" loading="lazy" decoding="async">'
            classes=card['classes']
            # Replace old emoji placeholders rather than making the card repeat itself.
            body=re.sub(r'<span class="(?:variant-icon|study-art|world-art)[^"]*"[^>]*>.*?</span>','',body,flags=re.S)
            body=re.sub(r'<div class="icon"[^>]*>.*?</div>','',body,flags=re.S)
            if classes & {'world-feature','discovery','card'}:
                new_body=img+body
            else:
                new_body=img+'<span class="card-caption">'+body+'</span>'
            opening=source[card['start']:card['open_end']]
            if 'class' in card['attrs']:
                opening=re.sub(r'\bclass="([^"]*)"',lambda m:'class="'+m[1]+' has-card-image"',opening,count=1)
            else:opening=opening[:-1]+' class="has-card-image">'
            source=source[:card['start']]+opening+new_body+'</a>'+source[card['end']:]
            self.added+=1
        return source
    def save(self):
        (ART/'manifest.json').write_text(json.dumps(sorted(self.manifest.values(),key=lambda e:e['route']),ensure_ascii=False,indent=2)+'\n')
        print(f'Card images: {self.added} illustrated cards; {self.existing} existing image/diagram cards retained; {len(self.manifest)} destination artworks.')
