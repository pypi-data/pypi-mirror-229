from pov.filters import chat
from . import cli
from typing import Dict, List, Union
from datetime import datetime, timedelta

collection = cli["pov"]["active_users"]


async def add_user(user_id):
    user = {
        '_id': user_id,
        'last_active': datetime.now()
    }
    collection.replace_one({'_id': user_id}, user, upsert=True)

async def remove_user(user_id):
    collection.delete_one({'_id': user_id})

async def get_active_users():
    return [doc['_id'] async for doc in collection.find({'last_active': {'$gte': datetime.now() - timedelta(days=7)}})]