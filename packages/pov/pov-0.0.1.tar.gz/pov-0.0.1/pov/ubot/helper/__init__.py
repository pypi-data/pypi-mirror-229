import os
import sys
from pyrogram import filters, Client
from config import CMD_HNDLR as cmds
from ubotlibs import DEVS

from .adminHelpers import *
from .aiohttp_helper import*
from .basic import *
from .constants import *
from .data import *
from .inline import *
from .interval import *
from .parser import *
from .PyroHelpers import *
from .utility import *
from .what import *


def Ubot(command: str, prefixes: cmds):
    def wrapper(func):
        @Client.on_message(filters.command(command, prefixes) & filters.me)
        async def wrapped_func(client, message):
            await func(client, message)

        return wrapped_func

    return wrapper

def Devs(command: str):
    def wrapper(func):
        @Client.on_message(filters.command(command, ".") & filters.user(DEVS))
        def wrapped_func(client, message):
            return func(client, message)

        return wrapped_func

    return wrapper


def restart():
    os.execvp(sys.executable, [sys.executable, "-m", "Ubot"])

