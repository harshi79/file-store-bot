from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_callback_query(filters.regex('^home$'))
async def home(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("⚠️ ᴀʙᴏᴜᴛ ⚠️", callback_data = "about"), InlineKeyboardButton("✌️ ᴏᴡɴᴇʀ ✌️", user_id = client.owner)]]
    if query.from_user.id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])
    await query.message.edit_text(
        text=client.messages.get('START', 'No Start Message').format(
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id

        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return

@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("ʜᴏᴍᴇ", callback_data = "home")]]
    await query.message.edit_text(
        text=client.messages.get('ABOUT', 'No Start Message').format(
            owner_id=client.owner,
            bot_username=client.username,
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id

        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c = c + 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
                continue
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:

        return await message.reply(f"**Error:** `{e}`")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c = c + 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
                continue
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:

        return await message.reply(f"**Error:** `{e}`")
