from pov.types import InlineKeyboardButton, WebAppInfo
from pov import CMD_HNDLR as cmds
class Data:

    text_help_menu = (
        f"**Help Menu**\n** • Prefixes** : `!`, `?`, `-`, `^`, `.`"
    )
    reopen = [[InlineKeyboardButton("Open", callback_data="reopen")]]
