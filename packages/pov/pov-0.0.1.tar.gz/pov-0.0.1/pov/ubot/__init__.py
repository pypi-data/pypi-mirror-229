from pov import filters, Client
from config import CMD_HNDLR as cmds
from pov import DEVS

def pov(command: str, prefixes: cmds):
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
