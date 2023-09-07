
import logging
import motor.motor_asyncio
import codecs
import pickle

from string import ascii_lowercase
from typing import Dict, List, Union

from config import MONGO_URL

cli = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
