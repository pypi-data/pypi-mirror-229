from pov.filters import chat
from pov import Client, filters
from pov.types import Message
import asyncio
from . import cli
from typing import Dict, List, Union
from datetime import datetime, timedelta


collection = cli["pov"]["tag_log"]


tagged_messages_filter = filters.group & filters.private & filters.mentioned & filters.incoming


async def logs(user_id: int) -> bool:
    log = {"user_id": user_id}
    try:
        result = await collection.users.update_one(
            {'user_id': user_id},
            {'$set': {'tag_log': True}},
            upsert=True
        )
        if result.modified_count > 0 or result.upserted_id:
            await message.edit("**Tag alert Activated Successfully**")
            await log_tagged_messages()
            return True
    except:
        return False


async def relog(user_id: int) -> bool:
    log = {"user_id": user_id}
    try:
        result = await collection.users.update_one(
            {'user_id': user_id},
            {'$set': {'tag_log': False}},
            upsert=True
        )
        if result.modified_count > 0 or result.upserted_id:
            await message.edit("**Tag alert Deactivated Successfully**")
            return False
    except:
        return False


async def log_tagged_messages():
    async for message in client.iter_messages(chat_id=CHAT_ID, filter=tagged_messages_filter):
        user_id = message.from_user.id
        pov = f"<b>📨 #TAGS #MESSAGE</b>\n<b> • : </b>{message.from_user.mention}"
        pov += f"\n<b> • Group : </b>{message.chat.title}"
        pov += f"\n<b> • 👀 </b><a href='{message.link}'>Lihat Pesan</a>"
        pov += f"\n<b> • Message : </b><code>{message.text}</code>"
        await asyncio.sleep(0.1)
        await client.send_message(
            BOTLOG_CHATID,
            pov,
            parse_mode="html",
            disable_web_page_preview=True,
        )
