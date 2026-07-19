# FileStoreBot

A Telegram file-store bot. Admins send or forward a file to the bot; it copies the file into a private Telegram database channel and returns a shareable `/start` link. Users opening the link receive a copy of the stored file.

This fork is ready for a **Render free Web Service**, Docker, and external uptime monitoring. It includes a lightweight health endpoint at `/healthz`.

> **Keep secrets private.** Never commit `setup.json`, your bot token, API hash, or MongoDB URI. `setup.json` is ignored by Git and `setup.example.json` contains safe placeholders only.

## What you need

1. A Telegram account.
2. A Telegram bot token from **[@BotFather](https://t.me/BotFather)**.
3. Telegram API credentials from **[my.telegram.org/apps](https://my.telegram.org/apps)**.
4. A free MongoDB Atlas database (or any reachable MongoDB deployment).
5. A **private Telegram channel** that will hold the files. Add your bot to it as an **administrator** with permission to post and delete messages.
6. Your numeric Telegram user ID. Send `/start` to [@userinfobot](https://t.me/userinfobot), for example, to find it.

## Configure it

Choose **one** configuration method:

- **Easy / one bot:** copy the fully commented environment template. This is ideal for Render's Environment page.

  ```bash
  cp .env.example .env
  # Edit .env, then export it locally before running:
  set -a; . ./.env; set +a
  ```

  The application reads these individual variables directly; no extra dotenv package is needed. `.env` is ignored by Git.

- **Advanced / multiple bots:** copy the JSON template, then replace every example value:

  ```bash
  cp setup.example.json setup.json
  ```

  `setup.json` is a JSON **array**, so it can contain more than one bot configuration. Most deployments need one object only. On Render, its complete content can instead be stored as the secret `SETUP_JSON`.

**Priority:** `SETUP_JSON` → individual environment variables (when `BOT_TOKEN` is set) → local `setup.json`.

| Field | Required | What it is / where to get it |
| --- | --- | --- |
| `session` | Yes | A local unique name such as `filestore_bot`. Letters, digits, `_`, and `-` are safest. |
| `token` | Yes | BotFather → `/newbot` → copy the HTTP API token. |
| `api_id` | Yes | Numeric **App api_id** at [my.telegram.org/apps](https://my.telegram.org/apps). It is not your user ID. |
| `api_hash` | Yes | **App api_hash** from the same Telegram API page. |
| `owner_id` | Yes | Your numeric Telegram user ID. The owner cannot be removed from admins. |
| `admins` | Yes | Array of numeric Telegram user IDs allowed to upload, make links, broadcast, and administer the bot. Include your `owner_id`. |
| `db_uri` | Yes | MongoDB connection string. Atlas: **Database → Connect → Drivers → Python**, then replace username and password. URL-encode special password characters. |
| `db_name` | Yes | MongoDB database name to create/use, e.g. `filestorebot`. |
| `db` | Yes | Numeric ID of the private file database channel, usually starts `-100`. Forward a channel post to [@userinfobot](https://t.me/userinfobot) to find it. |
| `workers` | No | Telegram worker count; default `8`. |
| `fsubs` | No | Force-subscription channels; use `[]` to disable. Format: `[channel_id, join_request, expiry_minutes]`. See below. |
| `auto_del` | No | Seconds before delivered files are deleted; `0` disables deletion. |
| `protect` | No | `true` prevents forwarding/saving delivered content where Telegram supports it. |
| `disable_btn` | No | `true` removes share buttons from copied database posts. |
| `messages` | No | Text/image/caption customisation. `{first}`, `{last}`, `{username}`, `{mention}`, and `{id}` work in `START`; `{owner_id}` and `{bot_username}` also work in `ABOUT`. |

### Database channel ID

Create a channel, send any test post, add the bot as an admin, then forward that post to [@userinfobot](https://t.me/userinfobot). Use the reported channel ID exactly (including the minus sign). The bot performs a send/delete startup check; if it fails, verify the ID and bot permissions.

### MongoDB Atlas quick setup

1. Create a free **M0** cluster at [MongoDB Atlas](https://www.mongodb.com/atlas/database).
2. In **Database Access**, create a database user and save its username/password.
3. In **Network Access**, add `0.0.0.0/0` for Render (or restrict it if you use a fixed egress IP elsewhere).
4. Select **Connect → Drivers → Python**, copy the URI, replace `<password>`, and put it in `db_uri`.

### Optional force subscription

Each `fsubs` entry is `[channel_id, join_request, expiry_minutes]`:

```json
"fsubs": [[-1001234567890, false, 0]]
```

The bot must be an admin in every force-subscription channel, with invite-link permission. `join_request: true` makes invite links request-to-join links. Set `expiry_minutes` above `0` to generate temporary links.

## Run locally

Requires Python 3.10+ (3.11 recommended) and a configured `setup.json`:

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open `http://localhost:10000/healthz`; it should return `{"status": "ok"}`. Set `PORT=8080` to use another local port.

## Deploy on Render (free Web Service)

1. Push this repository to GitHub, then in Render choose **New → Blueprint** and select the repository. Render reads [`render.yaml`](render.yaml), creates a free Docker Web Service, and uses `/healthz` as its health check. Alternatively choose **New → Web Service**, connect the repo, and explicitly choose **Docker** as the runtime.
2. Do **not** use Render's default Python start command (`gunicorn your_application.wsgi`); this is not a Django/Gunicorn application. Docker runs the included `Dockerfile`, which starts `python main.py`.
3. In **Environment**, choose one option:
   - **Recommended for one bot:** open [`.env.example`](.env.example) and add each uncommented variable to Render one at a time. Mark `BOT_TOKEN`, `API_HASH`, and `MONGODB_URI` as **Secret**. Do not add `PORT`; Render supplies it.
   - **For multiple bots:** add one Secret named `SETUP_JSON`, with the complete JSON from your configured `setup.json` (including the outer `[` and `]`). Do not add it as a build variable.
4. Deploy. Render provides `PORT` automatically; do not hard-code a port.
5. When deployment is live, open `https://YOUR-SERVICE.onrender.com/healthz`. It must return `{"status":"ok"}` before configuring the monitor.

Render free services can spin down after inactivity. This bot has a web listener so Render accepts it as a Web Service, but a monitor is useful for periodic liveness requests. Do not rely on a free service for critical workloads; free-plan behavior and limits can change.

## UptimeRobot health check

1. In UptimeRobot select **Add New Monitor** → **HTTP(s)**.
2. Enter `https://YOUR-SERVICE.onrender.com/healthz`.
3. Use a 5-minute interval (or your plan's available interval) and expect HTTP `200`.
4. Save it. The endpoint returns no secrets and is designed only as a liveness check.

## Docker elsewhere

```bash
docker build -t filestorebot .
docker run --rm -p 10000:10000 \
  -e SETUP_JSON="$(cat setup.json)" \
  filestorebot
```

For production, supply `SETUP_JSON` through your platform's secret manager, not shell history. If you require durable Pyrogram session files, mount persistent storage; the bot token itself is sufficient for normal bot startup.

## Bot commands

- `/start` — show the home screen or retrieve a file from a link.
- `/genlink` — create a link for one database-channel message (admin).
- `/batch` — create one link for a message range (admin).
- Send a file/message privately to the bot — store it and get a link (admin).
- `/broadcast`, `/pbroadcast`, `/users`, `/ban`, `/unban`, `/usage` — administration features (admin; see bot prompts).

## Health and security notes

- The service binds to `0.0.0.0:$PORT` and exposes `/` and `/healthz`.
- Link payloads are validated, and batch retrieval is capped at 200 messages to avoid accidental overload.
- Runtime setting changes made through Telegram are in memory only; update your secret/configuration before a redeploy if you want them to persist.
- Make the database channel private and grant the bot only the permissions it needs.

## License and attribution

This project is derived from [ArihantSharma/FileStoreBot](https://github.com/ArihantSharma/FileStoreBot) and remains licensed under GPL-3.0; see [LICENSE](LICENSE).
