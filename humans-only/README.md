# HumansOnly · HRL Portfolio

A working, text-first forum and reusable in-game chat backend. Public interface:
`https://rmichaelglover.github.io/hrl-portfolio/humans-only/`.

Python 3.10+ and SQLite; no third-party runtime packages. The static HTML/CSS/JS
interface lives inside HRL Portfolio. A loopback-only Python service on Michael's
laptop owns accounts, messages, topics, age declarations, reports, appeals, and
moderation. Tailscale Funnel provides its public HTTPS address.

The name *HumansOnly.ai* does not assert registration or ownership of that domain.
Posting is free; there is no subscription or payment integration. Human
participation is a community rule, not a claim of verified identity. Age
declarations are self-reported, not verified. No private messages or uploads.

## Run

```sh
python3 humans-only/backend/server.py owner --username CypherKeeper
python3 humans-only/backend/server.py serve --port 8787 \
  --origin https://rmichaelglover-ideapad-5-15ial7.tailc30ce9.ts.net
```

The first command creates an owner once, saves a random temporary passphrase to
`~/.local/share/humansonly/owner-access.txt` with mode 0600, and requires changing
that passphrase before posting or moderating. No first-visitor owner claim exists.
Read that file locally; do not commit it or paste it into a public message.

The database defaults to `~/.local/share/humansonly/forum.sqlite3`, outside the
portfolio. Passwords use salted scrypt; only SHA-256 hashes of random session tokens
are persisted. No email addresses or full birth dates are requested. Public
all-ages messages are public; restricted room content requires an authorized
session. Administrators can read the database and reported content.

Readiness: `GET http://127.0.0.1:8787/api/v1/health`.

```sh
tailscale funnel --bg --https=443 http://127.0.0.1:8787
```

Inspect existing Funnel settings before configuring it; do not replace another
application's mapping. The deployed `config.js` points only to this service.
If Tailscale reports `serve config denied`, run that command with `sudo` in your
own terminal. Do not send an administrator password through the forum or chat.
The user service file is `backend/humansonly.service`; substitute the checkout
path before installing it under `~/.config/systemd/user/`.

```sh
systemctl --user enable --now humansonly.service
systemctl --user status humansonly.service
journalctl --user -u humansonly.service
```

This runs while the user service manager is active. Laptop sleep, network loss,
session shutdown without user lingering, or Tailscale key expiry can interrupt
availability. It is not a high-availability hosting claim.

## Moderation

Sign in as owner, change the temporary password, then use **Account → Open
moderation desk**. Reports offer message removal, a seven-day commenting timeout,
or dismissal. Appeals offer early release. A reason is required for every action.
The server prevents non-moderators from using these endpoints, and applies
timeouts across forum and game rooms. Repeated reports do not auto-punish a
person, and repeated timeout actions cannot stack an active timer. Nobody is
permanently banned by this implementation. Posts still need human moderation;
there is no claim of automatic abuse recognition.

## Verify and back up

```sh
python3 -m unittest discover -s humans-only/tests -v
python3 humans-only/backend/server.py backup --output /private/path/forum-backup.sqlite3
```

Backups contain private account hashes and moderation information. Keep them
outside the public checkout. The service logs request methods and paths, not
visitor IPs, tokens, passwords, or message bodies. Authentication throttling uses
an IP-derived bucket; through a local reverse proxy, public visitors may share
that bucket. This is an intentionally conservative small-community limit.

See [API and embedding](docs/api.md) and [serve / dictionary-graph research](docs/serve.md).
ECC+ does not yet execute the proposed generic `serve` grammar, and no graph
neural network training is claimed.
