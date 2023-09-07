from pov.filters import chat
from . import cli
from typing import Dict, List, Union
from datetime import datetime, timedelta
from .accesdb import *
import schedule
import asyncio
collection = cli["pov"]["active"]



async def get_active_time(user_id):
    expire_date = await get_expired_date(user_id)
    if expire_date:
        active_time = expire_date - datetime.now()
        return active_time
    else:
        return None

async def get_expired_date(user_id):
    user = await collection.users.find_one({'_id': user_id})
    if user:
        return user.get('expire_date')
    else:
        return None

async def rem_expired_date(user_id):
    await collection.users.update_one(
        {"_id": user_id}, {"$unset": {"expire_date": ""}}, upsert=True
    )

async def remove_expired():
    async for user in collection.users.find({"expire_date": {"$lt": datetime.now()}}):
        await delete_user_access(user["_id"])
        await rem_expired_date(user["_id"])


async def set_expired_date(user_id, expire_date):
    collection.users.update_one({'_id': user_id}, {'$set': {'expire_date': expire_date}}, upsert=True)
    schedule.every().day.at("00:00").do(remove_expired)
    async def schedule_loop():
        while True:
            await asyncio.sleep(1)
            schedule.run_pending()
    asyncio.create_task(schedule_loop())