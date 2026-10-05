# Maestro accounts and profiles

The homepage and existing chess tools remain static. Real signup, login, and public profiles use the same-origin Python service in this directory with persistent SQLite storage. No accounts or passwords are simulated in localStorage.

## Run locally

From the repository root:

```sh
python3 server/app.py --port 8788
```

Open http://127.0.0.1:8788/ and select **Players & profiles**. The server serves the existing website and `/api/` routes. Python 3.10+ is sufficient; no third-party dependencies are required. The database defaults to `~/.local/share/maestro/accounts.sqlite3`, outside the public website. Use `--db` to specify another private, persistent location.

```sh
cd server
python3 -m unittest -v test_accounts.py
```

## Production hosting

GitHub Pages cannot execute this service. Deploy the repository on a persistent Python host, or put the static site and this service behind one HTTPS origin. Route `/api/` to the Python process and serve the static files at the same origin. Start the process bound to loopback, with the exact public origin:

```sh
python3 server/app.py --host 127.0.0.1 --port 8788 --origin https://chess.example.org --db /var/lib/maestro/accounts.sqlite3
```

Use a reverse proxy for TLS, request limits, and static files; the built-in HTTP server is intended for local previews and the proxied API, not direct public exposure. The persistent directory must be writable by the service user. Back up the SQLite database using SQLite's backup API. Do not place it inside the static document root or commit it. Do not publicly expose `server/`, dotfiles, or repository metadata. Sessions use HttpOnly, SameSite=Lax cookies and use Secure cookies when `--origin` is HTTPS. The service checks the exact Origin and CSRF token for profile changes and logout. Passwords use salted scrypt hashes; session tokens are stored as hashes and expire after seven days.

The current release supports username/password signup, login, logout, public profile links, profile editing, and a directory of the 100 most recent members. It has no email collection or password recovery, friends, messaging, matchmaking, ratings, or synchronized saved games. External chess account links are self-reported, not verified identities. Authentication attempts are rate limited per connection IP; a proxy should add public-client rate limits because proxied connections share an IP. Profile fields are rendered as text and external profile links use fixed destinations.

No production account service has been provisioned by these changes. On GitHub Pages the profile page explains that the service is not yet connected and links directly to Maestro.
