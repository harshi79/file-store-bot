import motor.motor_asyncio


class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str):
        if (uri, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.channel_data = instance.db["channels"]
            instance.settings_data = instance.db["settings"]
            cls._instances[(uri, db_name)] = instance
        return cls._instances[(uri, db_name)]

    async def set_channels(self, channels: list[int]):
        await self.settings_data.update_one(
            {"_id": "required_channels"}, {"$set": {"channels": channels}}, upsert=True
        )

    async def get_channels(self) -> list[int]:
        data = await self.settings_data.find_one({"_id": "required_channels"})
        return data.get("channels", []) if data else []

    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one({"_id": channel_id}, {"$addToSet": {"users": user_id}}, upsert=True)

    async def remove_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one({"_id": channel_id}, {"$pull": {"users": user_id}})

    async def get_channel_users(self, channel_id: int) -> list[int]:
        doc = await self.channel_data.find_one({"_id": channel_id})
        return doc.get("users", []) if doc else []

    async def is_user_in_channel(self, channel_id: int, user_id: int) -> bool:
        return await self.channel_data.find_one({"_id": channel_id, "users": user_id}, {"_id": 1}) is not None

    async def present_user(self, user_id: int) -> bool:
        return bool(await self.user_data.find_one({"_id": user_id}))

    async def add_user(self, user_id: int, ban: bool = False):
        await self.user_data.update_one({"_id": user_id}, {"$setOnInsert": {"ban": ban}}, upsert=True)

    async def full_userbase(self) -> list[int]:
        return [doc["_id"] async for doc in self.user_data.find({}, {"_id": 1})]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({"_id": user_id})

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({"_id": user_id}, {"$set": {"ban": True}})

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({"_id": user_id}, {"$set": {"ban": False}})

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_data.find_one({"_id": user_id})
        return user.get("ban", False) if user else False
