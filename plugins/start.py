import asyncio

import humanize
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import MAX_BATCH_SIZE
from helper.helper_func import decode, delete_files, force_sub, get_messages


@Client.on_message(filters.command("start") & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await client.mongodb.present_user(user_id):
        try:
            await client.mongodb.add_user(user_id)
        except Exception as exc:
            client.LOGGER(__name__, client.name).warning("Could not add user: %s", exc)

    if await client.mongodb.is_banned(user_id):
        return await message.reply("**You have been banned from using this bot.**")

    text = message.text or ""
    if len(text) <= 7:
        return await send_home(client, message)

    try:
        payload = text.split(" ", 1)[1]
        argument = (await decode(payload)).split("-")
        if argument[0] != "get" or len(argument) not in (2, 3):
            raise ValueError("unsupported link payload")
        multiplier = abs(client.db_channel.id)
        ids = [int(int(value) / multiplier) for value in argument[1:]]
        if any(message_id <= 0 for message_id in ids):
            raise ValueError("invalid message ID")
        if len(ids) == 2:
            step = 1 if ids[0] <= ids[1] else -1
            ids = list(range(ids[0], ids[1] + step, step))
        if len(ids) > MAX_BATCH_SIZE:
            return await message.reply("This link contains too many files. Ask an admin for a smaller batch link.")
    except (IndexError, ValueError, UnicodeDecodeError) as exc:
        client.LOGGER(__name__, client.name).warning("Invalid start link: %s", exc)
        return await message.reply("This file link is invalid or expired.")

    pending = await message.reply("Please wait…")
    try:
        messages = await get_messages(client, ids)
    except Exception as exc:
        client.LOGGER(__name__, client.name).warning("Error retrieving messages: %s", exc)
        return await pending.edit_text("Something went wrong while retrieving the files.")
    if not messages:
        return await pending.edit("Couldn't find the files in the database.")
    await pending.delete()

    sent_messages = []
    for stored_message in messages:
        if not stored_message:
            continue
        caption_template = client.messages.get("CAPTION", "")
        original_caption = stored_message.caption.html if stored_message.caption else ""
        caption = caption_template.format(previouscaption=original_caption) if caption_template else original_caption
        try:
            sent_messages.append(await stored_message.copy(
                chat_id=user_id,
                caption=caption,
                reply_markup=stored_message.reply_markup if not client.disable_btn else None,
                protect_content=client.protect,
            ))
        except FloodWait as exc:
            await asyncio.sleep(exc.x)
            sent_messages.append(await stored_message.copy(chat_id=user_id, caption=caption, protect_content=client.protect))
        except Exception as exc:
            client.LOGGER(__name__, client.name).warning("Failed to send a file: %s", exc)

    if client.auto_del > 0 and sent_messages:
        notice = await client.send_message(
            user_id,
            f"<blockquote><b><i>This file will be deleted automatically in "
            f"{humanize.naturaldelta(client.auto_del)}. Forward it to Saved Messages if needed.</i></b></blockquote>",
        )
        asyncio.create_task(delete_files(sent_messages, client, notice, text))


async def send_home(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("⚠️ About", callback_data="about"),
        InlineKeyboardButton("✌️ Owner", user_id=client.owner),
    ]]
    if message.from_user.id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⛩️ Settings", callback_data="settings")])
    values = {
        "first": message.from_user.first_name,
        "last": message.from_user.last_name,
        "username": f"@{message.from_user.username}" if message.from_user.username else None,
        "mention": message.from_user.mention,
        "id": message.from_user.id,
    }
    text = client.messages.get("START", "No start message.").format(**values)
    photo = client.messages.get("START_PHOTO", "")
    if photo:
        return await client.send_photo(message.chat.id, photo, caption=text, reply_markup=InlineKeyboardMarkup(buttons))
    return await client.send_message(message.chat.id, text, reply_markup=InlineKeyboardMarkup(buttons))
