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


def load_setups() -> list[dict]:
    """Load bot settings from SETUP_JSON or a local setup.json file.

    SETUP_JSON is designed for Render's secret environment-variable UI. A local
    setup.json remains convenient for development and is intentionally ignored.
    """
    raw = os.getenv("SETUP_JSON")
    source = "SETUP_JSON"
    if raw is None:
        path = Path(os.getenv("SETUP_FILE", "setup.json"))
        source = str(path)
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Configuration missing. Set SETUP_JSON or copy setup.example.json to setup.json."
            ) from exc

    try:
        setups = json.loads(raw)
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
