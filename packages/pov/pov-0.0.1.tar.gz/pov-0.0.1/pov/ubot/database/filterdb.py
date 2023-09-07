from pov.filters import chat
from pov import Client
from . import cli
from typing import *
from datetime import datetime, timedelta
import pymongo.errors

collection = cli["pov"]["filters"]


from pymongo import MongoClient


def add_filter(chat_id, user_id, keyword, reply_text, media):
    collection.insert_one({"chat_id": chat_id, "user_id": user_id, "keyword": keyword, "reply_text": reply_text, "media": media, "buttons": buttons})

def get_filter(chat_id, user_id, keyword):
    return collection.find_one({"chat_id": chat_id, "user_id": user_id, "keyword": keyword})

def delete_filter(chat_id, user_id, keyword):
    collection.delete_one({"chat_id": chat_id, "user_id": user_id, "keyword": keyword})

def get_all_filters(chat_id, user_id):
    return collection.find({"chat_id": chat_id, "user_id": user_id})






