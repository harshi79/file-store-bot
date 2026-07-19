import asyncio
import json
import os
from pathlib import Path

from bot import Bot, web_app
from pyrogram import compose

DEFAULT_MESSAGES = {
    "START": "Hello {mention}! Send me a file link to retrieve it.",
    "FSUB": "Please join the required channel(s) to continue.",
    "ABOUT": "A private file-store bot.",
    "REPLY": "You are not allowed to use this command.",
    "START_PHOTO": "",
    "FSUB_PHOTO": "",
    "CAPTION": "",
}
REQUIRED_FIELDS = {
    "session", "token", "api_id", "api_hash", "owner_id", "admins", "db_uri", "db_name", "db"
}


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    if value.lower() in {"true", "1", "yes", "on"}:
        return True
    if value.lower() in {"false", "0", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false.")


def individual_env_setup() -> list[dict] | None:
    """Build one bot setup from conventional environment variables.

    This makes Render's individual-variable UI and .env.example convenient.
    SETUP_JSON remains the preferred option when deploying multiple bots.
    """
    if not os.getenv("BOT_TOKEN"):
        return None
    try:
        fsubs = json.loads(os.getenv("FSUBS_JSON", "[]"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("FSUBS_JSON must be valid JSON, for example [].") from exc
    admins = [value.strip() for value in os.getenv("ADMIN_IDS", "").split(",") if value.strip()]
    return [{
        "session": os.getenv("BOT_SESSION", "filestore_bot"),
        "token": os.environ["BOT_TOKEN"],
        "api_id": os.getenv("API_ID"),
        "api_hash": os.getenv("API_HASH"),
        "owner_id": os.getenv("OWNER_ID"),
        "admins": admins,
        "db_uri": os.getenv("MONGODB_URI"),
        "db_name": os.getenv("MONGODB_DB", "filestorebot"),
        "db": os.getenv("DB_CHANNEL_ID"),
        "workers": os.getenv("BOT_WORKERS", "8"),
        "fsubs": fsubs,
        "auto_del": os.getenv("AUTO_DELETE_SECONDS", "0"),
        "protect": env_bool("PROTECT_CONTENT", False),
        "disable_btn": env_bool("DISABLE_BUTTONS", True),
        "messages": {
            "START": os.getenv("START_MESSAGE", DEFAULT_MESSAGES["START"]),
            "FSUB": os.getenv("FSUB_MESSAGE", DEFAULT_MESSAGES["FSUB"]),
            "ABOUT": os.getenv("ABOUT_MESSAGE", DEFAULT_MESSAGES["ABOUT"]),
            "REPLY": os.getenv("REPLY_MESSAGE", DEFAULT_MESSAGES["REPLY"]),
            "START_PHOTO": os.getenv("START_PHOTO", ""),
            "FSUB_PHOTO": os.getenv("FSUB_PHOTO", ""),
            "CAPTION": os.getenv("CAPTION_TEMPLATE", ""),
        },
    }]


def load_setups() -> list[dict]:
    """Load SETUP_JSON, a local setup.json file, or individual environment variables."""
    raw = os.getenv("SETUP_JSON")
    source = "SETUP_JSON"
    if raw is not None:
        try:
            setups = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{source} is not valid JSON: {exc.msg} (line {exc.lineno}).") from exc
    else:
        env_setup = individual_env_setup()
        if env_setup:
            setups = env_setup
            source = "individual environment variables"
        else:
            path = Path(os.getenv("SETUP_FILE", "setup.json"))
            source = str(path)
            try:
                setups = json.loads(path.read_text(encoding="utf-8"))
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Configuration missing. Set BOT_TOKEN with the variables in .env.example, "
                    "set SETUP_JSON, or copy setup.example.json to setup.json."
                ) from exc
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{source} is not valid JSON: {exc.msg} (line {exc.lineno}).") from exc

    if not isinstance(setups, list) or not setups:
        raise RuntimeError(f"{source} must be a non-empty JSON array of bot configurations.")

    for index, setup in enumerate(setups, start=1):
        if not isinstance(setup, dict):
            raise RuntimeError(f"Configuration #{index} must be an object.")
        missing = REQUIRED_FIELDS - setup.keys()
        if missing:
            raise RuntimeError(f"Configuration #{index} is missing: {', '.join(sorted(missing))}.")
        setup.setdefault("workers", 8)
        setup.setdefault("fsubs", [])
        setup.setdefault("auto_del", 0)
        setup.setdefault("protect", False)
        setup.setdefault("disable_btn", True)
        messages = DEFAULT_MESSAGES.copy()
        messages.update(setup.get("messages", {}))
        setup["messages"] = messages
        for numeric in ("api_id", "owner_id", "db", "workers", "auto_del"):
            try:
                setup[numeric] = int(setup[numeric])
            except (TypeError, ValueError) as exc:
                raise RuntimeError(f"Configuration #{index}: {numeric} must be an integer.") from exc
        if not isinstance(setup["admins"], list):
            raise RuntimeError(f"Configuration #{index}: admins must be a JSON array.")
        setup["admins"] = [int(user_id) for user_id in setup["admins"]]
    return setups


async def run_bots() -> None:
    apps = []
    for setup in load_setups():
        apps.append(Bot(**setup))
    await compose(apps)


async def runner() -> None:
    await asyncio.gather(run_bots(), web_app())


if __name__ == "__main__":
    asyncio.run(runner())
