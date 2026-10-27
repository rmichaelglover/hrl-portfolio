#!/usr/bin/env python3
"""Verify the signed Ubuntu repository, package checksums, and direct downloads."""
from pathlib import Path
import gzip,hashlib,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'linux';DIST=OUT/'apt/dists/stable'
def main():
 key=OUT/'maestro-archive-keyring.gpg'
 with tempfile.TemporaryDirectory(prefix='ubuntu-signature-') as temp:
  verified=Path(temp)/'Release'
  subprocess.run(['gpgv','--keyring',str(key),'--output',str(verified),str(DIST/'InRelease')],check=True)
  assert verified.read_bytes()==(DIST/'Release').read_bytes(),'InRelease differs from Release'
 subprocess.run(['gpgv','--keyring',str(key),str(DIST/'Release.gpg'),str(DIST/'Release')],check=True)
 subprocess.run(['gpgv','--keyring',str(key),str(OUT/'SHA256SUMS.asc'),str(OUT/'SHA256SUMS')],check=True)
 for line in (OUT/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name
 sha=False
 for line in (DIST/'Release').read_text().splitlines():
  if line=='SHA256:':sha=True;continue
  if sha and not line.startswith(' '):break
  if sha:
   digest,size,name=line.split();p=DIST/name;assert p.stat().st_size==int(size);assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
 binary=DIST/'main/binary-all';packages=(binary/'Packages').read_bytes();assert gzip.decompress((binary/'Packages.gz').read_bytes())==packages
 found=set()
 for stanza in packages.decode().strip().split('\n\n'):
  fields=dict(line.split(': ',1) for line in stanza.splitlines() if ': ' in line and not line.startswith(' '))
  file=OUT/'apt'/fields['Filename'];assert hashlib.sha256(file.read_bytes()).hexdigest()==fields['SHA256'];assert file.stat().st_size==int(fields['Size']);found.add(fields['Package'])
  assert file.read_bytes()==(OUT/file.name).read_bytes(),'Pool differs from direct download'
 assert {'python3-hrl','python3-relaxation-labeling','maestro-chess'}<=found
 print('PASS: three signatures, Release hashes, signed download checksums, compressed index, and all package pool copies.')
if __name__=='__main__':main()
