# Ubuntu packaging audit — October 26, 2026

The current Ubuntu distribution entrypoint is https://rmichaelglover.github.io/hrl-portfolio/linux/ . These are independent project packages, not packages accepted into Ubuntu's official archive.

## Results

| Product / attempt | What was found | Verified result / action |
|---|---|---|
| Maestro Chess | Existing 0.1.0-1 and 0.1.1-1 DEBs, build script, source archives, signed APT repository | Live signed APT update succeeded; candidate 0.1.1-1 downloaded through APT and matched the local published DEB checksum. Extracted launcher served the board, music, lessons, and community pages on loopback. Existing release retained. |
| Portfolio HRL engine (`hrl/`) | Existing `pyproject.toml`, package version 0.1.0, NumPy-only imports, optional lazy NLI/LLM integrations; no DEB | Built `python3-hrl_0.1.0-1_all.deb`, terminal `hrl-demo`, docs/tests, and a rebuildable source archive. Preserved MIRL-1.0 terms. |
| Canonical classic RL core (`Code/oss/relaxation-labeling`) | Clean public AGPL-3.0 source, setuptools configuration, version 0.1.0; no DEB | Built `python3-relaxation-labeling_0.1.0-1_all.deb`, terminal `relaxation-labeling-demo`, docs/tests, and a rebuildable source archive. Preserved AGPL-3.0 and commercial-license notice. |
| Grok fork (`Code/grok-relaxation-labeling`) | Conflicting setuptools/pyproject configuration; advertised `grok-relax` CLI; experimental hierarchical/GRRLE modules | Actual wheel build emitted `relaxation_labeling-0.1.0`, containing `relax.py` but omitting `grok_relax/cli.py` and the advertised entry point. A successful wheel build is therefore not a working distribution of the advertised product. No DEB offered for this fork. |
| Generic HRL / recursive GRRLE research (`Code/relaxation-labeling/python`) | `hrl_generic`, `grrle`, `nlp_hrl` and many subsidiary experiments; no Debian packaging found | Generic HRL self-tests and synthetic GRRLE self-test pass. Broader source is a historical mixed research archive with a documented data/provenance boundary. Not swept into a package. Full recursive GRRLE is not installed by `python3-hrl`. |
| `Code/hrl2026` | Python/C++ research prototypes; no Debian build or DEB found | Not a reviewed Ubuntu release. Its Python tree also contains unrelated personal documents, so directory-wide packaging is unsuitable. |
| `Code/relaxation-labeling-2026` | Maestro application variants | No independent Debian packaging found. Existing maintained Maestro package remains the Ubuntu route. |
| `DataAnnotation.tech/hrl-portfolio` and older portfolio copies | Earlier `hrl` Python packaging metadata and engine snapshots | Historical duplicate attempt, not a separate Ubuntu release. Current tracked portfolio engine was used for the new HRL DEB. |
| RelaxFish polished archive and Ellipse Lab | Runnable Python prototypes with requirements; no DEB found | Remain source/notebook downloads. Neither is silently included in these core packages. |

The scan covered the current user's home tree for DEB files and Debian control files, and inspected HRL/GRRLE-related repositories and known portfolio copies for build/install metadata. Unrelated dependency build trees, caches, environments, and other users were excluded. Local wheel probes are diagnostic artifacts, not claims of a PyPI publication.

## Ubuntu verification

Host: Ubuntu 22.04.5 LTS, Python 3.10. The Ubuntu-distributed NumPy is 1.21.5; a newer NumPy 1.26.4 is also available in the developer environment, so distro-NumPy checks explicitly selected `/usr/lib/python3/dist-packages`.

- Portfolio engine: 81 existing tests passed with both developer NumPy and Ubuntu NumPy 1.21.5.
- Extracted HRL DEB: its 71 shipped module tests passed with distro NumPy, and its packaged `hrl-demo` ran.
- Classic core: all eight upstream tests passed; all eight also passed with Ubuntu NumPy 1.21.5 and from the extracted package. Its packaged demo recovered the expected two clusters.
- Both published source archives rebuilt DEBs from their own extracted contents.
- APT verified repository signatures with the established key. Isolated APT configuration, lists, cache, and downloads lived under `/tmp/hrl-ubuntu-audit`; system APT sources and installed packages were not modified.
- New packages were resolved by APT installation simulation against the Ubuntu host's package database. This is not a system-wide installation test or a clean-container test.
- Signatures, package-index hashes, source checksums, and new package pool copies were checked before publication.

Only Ubuntu 22.04 was exercised. `Architecture: all` means the Python payload contains no architecture-specific compiled binary; it is not a claim that every Ubuntu release or CPU has been tested. Other Ubuntu releases require Python >=3.10 and appropriate distribution NumPy packages. Optional model integrations require additional dependencies and model/service access; nothing downloads models automatically.

The classic core's upstream Python metadata specifies NumPy >=1.23. Its Debian dependency floor is deliberately 1.21.5 after running all eight upstream tests with Ubuntu 22.04's NumPy. No upstream algorithm code was changed.

## Repository maintenance correction

The old builder could regenerate `Release` while stale `Release`/signature files were present and could leave old signatures after replacing metadata. `packaging/update_apt.py` now scans every DEB in the existing pool, generates Release from a clean metadata tree, and refreshes InRelease, Release.gpg, and signed checksums together using the existing key. The Maestro builder uses that helper and refuses to modify an existing signed repository without an explicit signing home. Existing Maestro downloads remain unchanged.

The repository retains its established Origin/Label and signing identity, “Maestro Chess,” to avoid an unexpected release-information change for existing users. It now carries both HRL packages alongside Maestro. No private signing material is included in downloads or Git.

## Usage after repository setup

```sh
sudo apt update
sudo apt install python3-hrl
hrl-demo
/usr/bin/python3 -c 'from hrl import RelaxationLabeler; print(RelaxationLabeler)'

# Optional classic RL engine and desktop application:
sudo apt install python3-relaxation-labeling maestro-chess
relaxation-labeling-demo
maestro-chess
```

Alternatively, download either DEB and use `sudo apt install ./filename.deb`. Use `/usr/bin/python3` for Ubuntu-packaged Python modules; isolated virtual environments do not automatically see system packages.

Repository format and Ubuntu installation references:

- https://ubuntu.com/server/docs/how-to/software/package-management/
- https://manpages.ubuntu.com/manpages/noble/man5/sources.list.5.html
- https://wiki.debian.org/DebianRepository/Format
