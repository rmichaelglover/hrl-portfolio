#!/usr/bin/env python3
"""Build Maestro's Linux-only DEB, RPM, source archive, and APT metadata."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'
NAME = 'maestro-chess'
PUBLIC = 'https://rmichaelglover.github.io/hrl-portfolio/'
LAUNCHER = '''#!/usr/bin/python3 -B
"""Launch Maestro as a local, Linux desktop web application."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent.parent / 'share/maestro-chess'
sys.path.insert(0, str(root / 'server'))
from app import App
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--no-browser', action='store_true', help='Print the local URL without launching a browser')
parser.add_argument('--port', type=int, default=0, help='Local port; default selects an available port')
parser.add_argument('--db', default=str(Path.home()/'.local/share/maestro-chess/accounts.sqlite3'))
args = parser.parse_args()
server = App(('127.0.0.1', args.port), args.db)
url = 'http://127.0.0.1:' + str(server.server_port) + '/'
print(url, flush=True)
if not args.no_browser:
    subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
'''


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def payload(stage):
    data = stage / 'usr/share/maestro-chess'
    data.mkdir(parents=True)
    shutil.copy2(ROOT / 'maestro.html', data / 'maestro.html')
    for folder in ['community', 'chess-music', 'chess-lessons', 'assets/rage-comics', 'assets/day-visuals']:
        shutil.copytree(ROOT / folder, data / folder, ignore=shutil.ignore_patterns('__pycache__'))
    (data / 'whimsy-chess').mkdir()
    for name in ['worldkit.js', 'storybook.js']:
        shutil.copy2(ROOT / 'whimsy-chess' / name, data / 'whimsy-chess' / name)
    # Full site libraries stay online; the board, music kit, and accounts work locally.
    for html in [data / 'maestro.html', data / 'chess-music/index.html', data / 'community/index.html', data / 'chess-lessons/index.html']:
        text = html.read_text()
        def fix_link(match):
            href = match.group(1)
            if href.startswith(('https:', 'http:', '#', '?')):
                return match.group(0)
            target = html.parent / href.split('?')[0].split('#')[0]
            if target.exists():
                return match.group(0)
            from urllib.parse import urljoin
            relative = html.relative_to(data).as_posix()
            return 'href="' + urljoin(PUBLIC + relative, href) + '"'
        html.write_text(re.sub(r'href="([^"]+)"', fix_link, text))
    story = data / 'whimsy-chess/storybook.js'
    story.write_text(story.read_text().replace("'/hrl-portfolio/whimsy-chess/storybook/'", repr(PUBLIC+'whimsy-chess/storybook/')))
    # Linux starts with the same full native Maestro app. Online portfolio
    # links remain online; music, lecture, and local profiles are included.
    landing = (ROOT / 'index.html').read_text()
    a = landing.index('<div id="site-extras">')
    b = landing.index('</body>', a)
    landing = landing[:a] + '<footer id="site-extras" style="text-align:center;padding:30px"><a href="https://rmichaelglover.github.io/hrl-portfolio/">Explore all worlds online ↗</a><p>Local profiles stay on this computer.</p></footer>' + landing[b:]
    landing = landing.replace('href="linux/"', 'href="https://rmichaelglover.github.io/hrl-portfolio/linux/"')
    landing = landing.replace('href="chess/"','href="https://rmichaelglover.github.io/hrl-portfolio/chess/"').replace('href="hrl-lab/"','href="https://rmichaelglover.github.io/hrl-portfolio/hrl-lab/"').replace('href="play/"','href="https://rmichaelglover.github.io/hrl-portfolio/play/"').replace('href="hrlized/"','href="https://rmichaelglover.github.io/hrl-portfolio/hrlized/"')
    (data / 'index.html').write_text(landing)
    (data / 'server').mkdir()
    shutil.copy2(ROOT / 'server/app.py', data / 'server/app.py')
    for name in ['LICENSE', 'LICENSING.md', 'TERMS.md']:
        shutil.copy2(ROOT / name, data / name)
    bindir = stage / 'usr/bin'; bindir.mkdir(parents=True)
    (bindir / 'maestro-chess').write_text(LAUNCHER)
    (bindir / 'maestro-chess').chmod(0o755)
    apps = stage / 'usr/share/applications'; apps.mkdir(parents=True)
    (apps / 'maestro-chess.desktop').write_text('''[Desktop Entry]
Type=Application
Name=Maestro Chess
Comment=Play colorful musical chess and mix chess-derived music
Exec=maestro-chess
Icon=maestro-chess
Terminal=false
Categories=Game;BoardGame;Music;
StartupNotify=false
''')
    icons = stage / 'usr/share/icons/hicolor/scalable/apps'; icons.mkdir(parents=True)
    (icons / 'maestro-chess.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><rect width="128" height="128" rx="24" fill="#0a1020"/><path d="M35 99h58v-9H35zm9-16h40l-8-22H52zm9-29h22V42H53zm5-19h12V18H58z" fill="#37e6ff"/><circle cx="95" cy="42" r="10" fill="#c060ff"/><path d="M103 42V16H86" fill="none" stroke="#c060ff" stroke-width="6"/></svg>''')
    docs = stage / 'usr/share/doc/maestro-chess'; docs.mkdir(parents=True)
    (docs / 'copyright').write_text('Maestro Chess\nCopyright R. Michael Glover\nLicense: MIRL-1.0, source-available; see full terms below.\n\n'+(ROOT/'LICENSE').read_text()+'\n\nThird-party Rage Comics assets and fonts:\n'+(ROOT/'assets/rage-comics/UPSTREAM-LICENSE.txt').read_text()+'\n'+(ROOT/'assets/rage-comics/FONT-LICENSE.txt').read_text())
    shutil.copy2(ROOT / 'packaging/README.md', docs / 'README.md')
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'linux')
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='maestro-linux-') as temp:
        work=Path(temp); stage=work/'stage'; stage.mkdir(); payload(stage)
        installed_size=sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())//1024
        debian=stage/'DEBIAN'; debian.mkdir()
        (debian/'control').write_text(f'''Package: {NAME}
Version: {VERSION}-1
Section: non-free/games
Priority: optional
Architecture: all
Maintainer: Michael Emanuel Glover <glover.rmichael@gmail.com>
Depends: python3 (>= 3.10), xdg-utils
Installed-Size: {installed_size}
Homepage: {PUBLIC}
Description: Colorful musical chess and an Audacity music kit
 Play both sides on the Maestro board in your browser. Explore colorful
 pieces and musical moves, mix five chess-derived audio tracks in Audacity,
 and maintain local player profiles. Runs on Linux with a loopback server.
 This package uses the MIRL-1.0 source-available license.
''')
        (debian/'md5sums').write_text(''.join(hashlib.md5(p.read_bytes()).hexdigest()+'  '+p.relative_to(stage).as_posix()+'\n' for p in sorted(stage.rglob('*')) if p.is_file() and not p.is_relative_to(debian)))
        deb=out/f'{NAME}_{VERSION}-1_all.deb'
        run('dpkg-deb','--root-owner-group','--build',str(stage),str(deb))
        # RPM and portable source archive share the exact application payload.
        source=work/f'{NAME}-{VERSION}'; source.mkdir()
        shutil.copytree(stage/'usr',source/'usr')
        shutil.copytree(ROOT/'packaging',source/'packaging',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT/'LICENSE',source/'LICENSE')
        shutil.copy2(ROOT/'server/test_accounts.py',source/'usr/share/maestro-chess/server/test_accounts.py')
        archive=out/f'{NAME}-{VERSION}.tar.gz'
        with tarfile.open(archive,'w:gz') as tar: tar.add(source,arcname=source.name)
        if shutil.which('rpmbuild'):
            rpm=work/'rpm'
            for folder in ['BUILD','BUILDROOT','RPMS','SOURCES','SPECS','SRPMS']: (rpm/folder).mkdir(parents=True)
            shutil.copy2(archive,rpm/'SOURCES'/archive.name)
            spec=rpm/'SPECS/maestro.spec'
            spec.write_text(f'''Name: {NAME}
Version: {VERSION}
Release: 1
Summary: Colorful musical chess and an Audacity music kit
License: LicenseRef-MIRL-1.0
URL: {PUBLIC}
Source0: {archive.name}
BuildArch: noarch
Requires: python3 >= 3.10
Requires: xdg-utils
AutoReqProv: no
%description
Play colorful musical chess, mix chess-derived music, and keep local player
profiles. Linux-only. MIRL-1.0 source-available license.
%prep
%setup -q
%build
%install
mkdir -p %{{buildroot}}/usr
cp -a usr/* %{{buildroot}}/usr/
%files
/usr/bin/maestro-chess
/usr/share/maestro-chess/
/usr/share/applications/maestro-chess.desktop
/usr/share/icons/hicolor/scalable/apps/maestro-chess.svg
%doc /usr/share/doc/maestro-chess/README.md
%license /usr/share/doc/maestro-chess/copyright
''')
            run('rpmbuild','--define',f'_topdir {rpm}','-ba',str(spec),stdout=subprocess.DEVNULL)
            for file in (rpm/'RPMS').rglob('*.rpm'): shutil.copy2(file,out/file.name)
            for file in (rpm/'SRPMS').rglob('*.rpm'): shutil.copy2(file,out/file.name)
        apt=out/'apt'; pool=apt/'pool/main'; pool.mkdir(parents=True,exist_ok=True)
        shutil.copy2(deb,pool/deb.name)
        binary=apt/'dists/stable/main/binary-all'; binary.mkdir(parents=True,exist_ok=True)
        result=run('dpkg-scanpackages','--multiversion','pool',cwd=apt,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (binary/'Packages').write_bytes(result.stdout)
        with gzip.GzipFile(filename=str(binary/'Packages.gz'),mode='wb',mtime=0) as f: f.write(result.stdout)
        release=run('apt-ftparchive','-o','APT::FTPArchive::Release::Origin=Maestro Chess','-o','APT::FTPArchive::Release::Label=Maestro Chess','-o','APT::FTPArchive::Release::Suite=stable','-o','APT::FTPArchive::Release::Codename=stable','-o','APT::FTPArchive::Release::Architectures=all','-o','APT::FTPArchive::Release::Components=main','release','dists/stable',cwd=apt,stdout=subprocess.PIPE)
        (apt/'dists/stable/Release').write_bytes(release.stdout)
        public_files=sorted(p for p in out.iterdir() if p.is_file() and p.suffix in ['.deb','.rpm','.gz'])
        (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in public_files))
        print('Built:',*[p.name for p in public_files],sep='\n  ')
        print('APT metadata ready; sign Release before publishing installation instructions.')

if __name__=='__main__': main()
