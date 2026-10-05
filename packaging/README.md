# Maestro for Linux

Maestro Chess packages the actual colorful, musical board, the Van’t Kruijsing Audacity kit, and local accounts/profiles. The desktop launcher serves the app only on 127.0.0.1 and opens the default browser. It selects a free port automatically. Local profiles are not published to the website; data is stored in `~/.local/share/maestro-chess/accounts.sqlite3`.

## Build

From the website repository root:

```sh
python3 packaging/build_linux.py
```

Requires Python 3.10+, dpkg-deb, dpkg-scanpackages, apt-ftparchive, and optionally rpmbuild. It builds a `.deb`, a source tarball, RPM and source RPM when rpmbuild exists, and APT repository metadata under `linux/`. It does not install packages, configure system repositories, or upload to Debian/Ubuntu maintainers. Audacity is optional and installed separately.

## Install a downloaded package

Debian/Ubuntu:

```sh
sudo apt install ./maestro-chess_0.1.0-1_all.deb
```

Fedora/RHEL-family systems with Python 3.10 or newer:

```sh
sudo dnf install ./maestro-chess-0.1.0-1.noarch.rpm
```

Launch **Maestro Chess** from the applications menu, or run `maestro-chess`. For a terminal-only preview, use `maestro-chess --no-browser`. The web application runs until its launcher process is stopped. Closing the browser tab does not stop that process. Start another session by launching again; existing local data remains available.

For an extracted source distribution, run `python3 usr/bin/maestro-chess --no-browser`. Its installed payload is under `usr/share/maestro-chess`. The original website source is https://github.com/rmichaelglover/hrl-portfolio. Build instructions require the full repository.

## Repository signing

`linux/apt/dists/stable/Release` must be signed with a dedicated repository key to create `InRelease` and `Release.gpg`. Publish only the public key. Keep the private key outside the website and repository. Never use `trusted=yes` or disable signature checking.

The package is MIRL-1.0 source-available. The current commercial-use restrictions do not satisfy Debian's free-software requirements for its main archive. Publishing our own repository does not imply acceptance by Debian, Ubuntu, Fedora, or any other distribution. A PPA requires an account and signed Debian source-package uploads; official archive inclusion requires the distribution's review process. No license has been changed.
