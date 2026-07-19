import asyncio

from aiohttp import web
from plugins import web_server
from pyrogram import Client
from datetime import datetime

from config import LOGGER, PORT
from helper import MongoDB


class Bot(Client):
    def __init__(
        self, session, token, api_id, api_hash, owner_id, admins, db_uri, db_name,
        db, workers=8, fsubs=None, messages=None, auto_del=0, protect=False,
        disable_btn=True, **_unused,
    ):
        super().__init__(
            name=session,
            api_hash=api_hash,
            api_id=api_id,
            plugins={"root": "plugins"},
            workers=workers,
            bot_token=token,
        )
        self.LOGGER = LOGGER
        self.name = session
        self.db = db
        self.fsub = fsubs or []
        self.owner = owner_id
        self.fsub_dict = {}
        self.admins = list(dict.fromkeys([*admins, owner_id]))
        self.messages = messages or {}
        self.auto_del = auto_del
        self.protect = protect
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = self.messages.get("REPLY", "Do not send any useless message in the bot.")
        self.mongodb = MongoDB(db_uri, db_name)
        self.req_channels = []

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        for channel in self.fsub:
            try:
                channel_id, request, timer = int(channel[0]), bool(channel[1]), int(channel[2])
                chat = await self.get_chat(channel_id)
                link = None
                if timer <= 0:
                    # Public channels can use their public link; otherwise create one.
                    link = chat.invite_link or (await self.create_chat_invite_link(
                        channel_id, creates_join_request=request
                    )).invite_link
                self.fsub_dict[channel_id] = [chat.title, link, request, timer]
                if request:
                    self.req_channels.append(channel_id)
            except (IndexError, TypeError, ValueError) as exc:
                self.LOGGER(__name__, self.name).error("Invalid fsubs entry %r: %s", channel, exc)
                await self.stop()
                raise
            except Exception as exc:
                self.LOGGER(__name__, self.name).error(
                    "Cannot configure force-subscription channel %r. Ensure the bot is an admin "
                    "with invite-link permission: %s", channel, exc
                )
                await self.stop()
                raise
        if self.req_channels:
            await self.mongodb.set_channels(self.req_channels)
        try:
            self.db_channel = await self.get_chat(self.db)
            test = await self.send_message(chat_id=self.db_channel.id, text="FileStoreBot startup check")
            await test.delete()
        except Exception as exc:
            self.LOGGER(__name__, self.name).error(
                "Database channel check failed for %s. Add the bot as an admin with post/delete "
                "permissions and verify db: %s", self.db, exc
            )
            await self.stop()
            raise
        self.username = usr_bot_me.username
        self.LOGGER(__name__, self.name).info("Bot @%s started.", self.username)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")


async def web_app():
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()
    # Keep this task alive so the health server is not garbage-collected.
    await asyncio.Event().wait()
