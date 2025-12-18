# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import re
import string
import sys
import typing


def tty_print(text: str, tty: bool):
    """
    Print text to terminal if tty is True,
    otherwise removes all ANSI escape sequences
    """
    print(text if tty else re.sub(r"\033\[[0-9;]*m", "", text))


def tty_input(text: str, tty: bool) -> str:
    """
    Print text to terminal if tty is True,
    otherwise removes all ANSI escape sequences
    """
    return input(text if tty else re.sub(r"\033\[[0-9;]*m", "", text))


def api_config(tty: typing.Optional[bool] = None):
    """Request API config from user and set"""
    # This functionality has been removed in favor of hardcoded defaults.
    # Leaving empty or just printing a message.
    from . import main
    from ._internal import print_banner
    
    if tty:
        print_banner("banner.txt")

    print("\033[0;92mUsing default API credentials (no input required).\033[0m")
    
    # Defaults are handled in main.py directly now.
    pass
