# 📁 File Store Bot



**File Store Bot** is a lightning-fast, powerful Telegram bot designed to handle file storage, user access control, admin tools, and full customization — all through Telegram UI.



---



## 🚀 Features



- **📦 Multi-Bot Deployment:**  

  Deploy multiple bots from a single codebase using a shared setup file. Each bot has its own configuration — great for resellers or power users.



- **📨 Unlimited Force Subscription:**  

  Add as many channels as you want for force-subscription. Supports **request-based access** — users don’t need to be added to the channel manually. Each link generated has a **timer and auto-expiry** for better control.



- **⚙️ Admin Controls:**  

  Add or remove multiple admins **in a single command**, all from within the bot itself.



- **🖼️ Start & FSUB Media:**  

  Provide image URLs or directly send photos to customize the **Start** and **Force Subscribe** messages.



- **🛡️ Protect & Auto-Delete Content:**  

  Enable content protection or set auto-delete timers for files — all configurable from within the bot.



- **💬 Fully Editable Messages:**  

  Customize start, about, reply, and FSUB messages with formatting and placeholders (see below).



- **🚫 Ban / Unban Users:**  

  Control access to the bot by banning or unbanning users instantly.



---



## 🛠️ Message Placeholders



### ✨ START Message



```python

client.messages.get('START', 'No Start Msg').format(

    first=message.from_user.first_name,

    last=message.from_user.last_name,

    username=None if not message.from_user.username else '@' + message.from_user.username,

    mention=message.from_user.mention,

    id=message.from_user.id

)

```



📌 Supported placeholders:

- `{first}` — user's first name  

- `{last}` — user's last name  

- `{username}` — `@username` or `None`  

- `{mention}` — a clickable mention  

- `{id}` — Telegram user ID  



---



### 🧾 ABOUT Message



```python

client.messages.get('ABOUT', 'No Start Message').format(

    owner_id=client.owner,

    bot_username=client.username,

    first=query.from_user.first_name,

    last=query.from_user.last_name,

    username=None if not query.from_user.username else '@' + query.from_user.username,

    mention=query.from_user.mention,

    id=query.from_user.id

)

```



📌 Supported placeholders:

- `{owner_id}` — owner’s Telegram ID  

- `{bot_username}` — bot’s `@username`  

- `{first}` / `{last}` / `{username}` / `{mention}` / `{id}` — same as START placeholders  



❌ Force Subscribe messages **do not support** placeholders.



---



## 🧑‍💻 Configuration Files



### 📄 config.py



This file contains the global bot settings.



```python

PORT = '8080'

OWNER_ID = 6321064549

MSG_EFFECT = 5046509860389126442

```



---



### 📁 setup.json



A list of configurations — one for each bot you want to run.



```json

[

    {

        "session": "ses",  // unique session name for this bot

        "token": "YOUR_BOT_TOKEN",

        "api_id": "YOUR_API_ID",

        "api_hash": "YOUR_API_HASH",

        "workers": 8,



        "db_uri": "mongodb+srv://Cluster0:your_db@cluster.mongodb.net/?retryWrites=true&w=majority",

        "db_name": "name",



        "fsubs": [[-1002074478106, true, 5]],  // [channel_id, request_enabled, link_expiry_in_minutes]

        "db": -1002074478106,  // logs or updates group



        "auto_del": 0,  // auto delete message time in seconds (0 = disabled)



        "messages": {

            "START": "<blockquote expandable>__Start message here...__</blockquote>",

            "FSUB": "",

            "ABOUT": "This bot is operated by {owner_id}.",

            "REPLY": "Your reply text here.",

            "START_PHOTO": "",  // image URL or Telegram file ID

            "FSUB_PHOTO": ""

        },



        "admins": [78324663, 73468932],

        "disable_btn": true,

        "protect": false

    }

]

```



📝 Notes:

- You can add **multiple bot configs** in the same `setup.json`

- Make sure **`session` names are unique** for each entry

- The `fsubs` list supports multiple channels



---



## 💡 Usage Guide



1. **Clone the repo**:



```bash

git clone https://github.com/ArihantSharma/FileStoreBot

cd FileStoreBot

bash start.sh

```



2. **Install requirements**:



```bash

pip install -r requirements.txt

```



3. **Edit your `config.py`** and `setup.json` as explained above.



4. **Run the bot**:



```bash

python3 main.py

```



You’re done!



---



## 🛒 Purchase Full Source



Want to use or resell this bot?



📩 **Contact [@VOATcb](https://t.me/VOATcb) on Telegram** to purchase the code or for support.



---



## 📜 License



This code is proprietary. You are not allowed to redistribute, resell, or publish it without explicit permission from the owner.

