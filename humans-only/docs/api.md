# Shared forum and game-chat API

The frontend endpoint is configured in `../config.js`. Local development serves
the same interface from `http://127.0.0.1:8787/`. No database or credential lives
under the website's static document root.

API prefix: `/api/v1`. JSON requests and responses. Authenticated calls send
`Authorization: Bearer <session token>`. Never put a token in a URL or game save.
Sessions expire after thirty days. The supplied client keeps its session in
tab-scoped `sessionStorage`. Sign-out revokes that session on the server; changing
a password revokes every previous session.

| Method | Path | Use |
| --- | --- | --- |
| GET | `/health` | Service status and server clock |
| GET | `/rooms` | Room metadata and account-specific availability |
| POST | `/auth/register` | `{username,password,age_group,human:true,accepted_rules:true}` |
| POST | `/auth/login` | `{username,password}` → session token and account |
| POST | `/auth/logout` | Revoke current session |
| GET | `/me` | Current account, role, timeout, age declaration |
| POST | `/me/password` | `{current,password}` → replacement session |
| POST | `/me/age` | Renew `{age_group}`; at most three changes per thirty days |
| GET | `/topics?room=commons` | Latest 100 topics in an authorized room |
| POST | `/topics` | `{room,title,body}` → topic ID and opening-message ID |
| GET | `/messages?room=commons&topic=...` | Latest 100 messages; omit `topic` for room chat |
| GET | `/messages?room=commons&after=123` | Up to 100 newer messages, ascending |
| POST | `/messages` | `{room,body,topic?}` |
| POST | `/reports` | `{message_id,reason}`; requests human review |
| POST | `/appeals` | `{body}` while timed out |
| GET | `/moderation` | Moderator-only open reports and appeals |
| POST | `/moderation` | Moderator-only `{action,reason,...}` |

Moderation actions: `hide` with `message_id`, `timeout` or `release` with `user_id`,
and `dismiss` with `report_id`. Every action requires a reason and creates an audit
record. There is no permanent ban action. An active timeout cannot be extended by
repeating it. Its expiry is checked for every forum/chat write, inside the same
SQLite write transaction as the proposed action. Appeals and reading remain open.

Age groups: `under18`, `18-20`, `21`, `22plus`. Age declarations are self-reported,
not verified, and expire for restricted-room access after thirty days. The 18–21
room includes twenty-one-year-olds; the 21+ room also includes them. Reading,
topics, posting, and reports all check room access on the server. Restricted message
bodies are not downloaded and then hidden in CSS. Hidden messages return a
tombstone rather than the removed body. Moderators can review reported content
across rooms.

The public list has no search, arbitrary user enumeration, uploads, private
messages, or cross-user profile lookup. Room conversations display the most recent
100 messages; this is not a complete-history interface. Client polling refreshes
the visible history, including moderation removals, every eight seconds.

## In a game

The easiest integration shares both UI and authentication within the portfolio:

```html
<iframe
  src="/hrl-portfolio/humans-only/index.html?widget=1&room=tiny-creek-chess"
  title="Tiny Creek Chess community chat"
  referrerpolicy="no-referrer"
  style="width:100%;height:560px;border:0">
</iframe>
```

Available game rooms: `game-lobby`, `tiny-creek-chess`, `whimsy-chess`. All are
all-ages. Try `../game-chat.html` for the working widget.

For a custom game UI, load `chat-client.js` and create
`new HumansOnlyClient(endpoint, token)`. Use `messages(room)` and `send(room, body)`.
The server remains authoritative. Do not trust a client's timeout flag, age label,
or moderator controls. Do not embed a moderator credential or a shared account.

## Origins and availability

CORS accepts the portfolio origin plus explicitly configured server origins.
Foreign browser origins are rejected. CORS is not bot detection or an
authentication system. Public API callers must still obey the human-posting rule;
the service cannot prove that every visitor is human. Registration and login are
rate limited, as are posts, topics, reports, appeals, and age-declaration changes.

The founder's laptop must remain on, awake, online, and running its user service
and Tailscale. Public access uses an HTTPS Funnel to the single loopback listener;
the tunnel does not expose arbitrary laptop files or ports. Tunnel bandwidth and
laptop resources limit capacity. A larger deployment would require further
operational work rather than claims of unlimited free hosting.
