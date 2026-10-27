#!/usr/bin/env python3
"""Refresh the existing repository and sign it explicitly with its established key."""
import argparse,gzip,hashlib,shutil,subprocess,tempfile
from pathlib import Path
KEY='FD6550680E9B0A04151D42DE99D81725B3A631F0'
def run(*args,**kw):return subprocess.run(args,check=True,**kw)
def update(out,signing_home=None):
 out=Path(out).resolve();apt=out/'apt';pool=apt/'pool/main';pool.mkdir(parents=True,exist_ok=True)
 if (apt/'dists/stable/InRelease').exists() and signing_home is None:
  raise RuntimeError('This repository is signed. Supply --signing-home to regenerate metadata and signatures together.')
 for deb in out.glob('*.deb'):shutil.copy2(deb,pool/deb.name)
 result=run('dpkg-scanpackages','--multiversion','pool',cwd=apt,capture_output=True)
 binary=apt/'dists/stable/main/binary-all';binary.mkdir(parents=True,exist_ok=True)
 (binary/'Packages').write_bytes(result.stdout)
 (binary/'Packages.gz').write_bytes(gzip.compress(result.stdout,mtime=0))
 # Generate Release in a clean tree so it never hashes itself or stale signatures.
 with tempfile.TemporaryDirectory(prefix='hrl-release-') as tmp:
  work=Path(tmp);shutil.copytree(binary,work/'dists/stable/main/binary-all')
  release=run('apt-ftparchive','-o','APT::FTPArchive::Release::Origin=Maestro Chess','-o','APT::FTPArchive::Release::Label=Maestro Chess','-o','APT::FTPArchive::Release::Suite=stable','-o','APT::FTPArchive::Release::Codename=stable','-o','APT::FTPArchive::Release::Architectures=all','-o','APT::FTPArchive::Release::Components=main','release','dists/stable',cwd=work,capture_output=True).stdout
 (apt/'dists/stable/Release').write_bytes(release)
 public=sorted(p for p in out.iterdir() if p.is_file() and p.suffix in {'.deb','.rpm','.gz'})
 sums=out/'SHA256SUMS';sums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in public))
 if signing_home:
  gpg=['gpg','--homedir',str(Path(signing_home).resolve()),'--batch','--yes','--local-user',KEY]
  release_path=apt/'dists/stable/Release'
  run(*gpg,'--digest-algo','SHA256','--clearsign','--output',str(release_path.with_name('InRelease')),str(release_path))
  run(*gpg,'--digest-algo','SHA256','--detach-sign','--output',str(release_path.with_name('Release.gpg')),str(release_path))
  run(*gpg,'--armor','--digest-algo','SHA256','--detach-sign','--output',str(out/'SHA256SUMS.asc'),str(sums))
  run('gpgv','--keyring',str(out/'maestro-archive-keyring.gpg'),str(release_path.with_name('InRelease')))
 print('Repository metadata updated'+(' and signed.' if signing_home else '; unsigned staging only.'))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'linux');p.add_argument('--signing-home',type=Path);a=p.parse_args();update(a.output,a.signing_home)
