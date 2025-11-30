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
    from . import main
    from ._internal import print_banner

    if tty is None:
        print("\033[0;91mСъешь ещё этих мягких французских булок, да выпей чаю\033[0m")
        tty = input("Текст выше цветной? [y/N] (д/Н)").lower() in ["y", "д", "yes", "да"]

    if tty:
        print_banner("banner.txt")

    tty_print("\033[0;95mДобро пожаловать в Hikka Userbot!\033[0m", tty)
    tty_print("\033[0;96m1. Перейдите на https://my.telegram.org и войдите в аккаунт\033[0m", tty)
    tty_print("\033[0;96m2. Нажмите на \033[1;96mAPI development tools\033[0m", tty)
    tty_print(
        (
            "\033[0;96m3. Создайте новое приложение, заполнив необходимые"
            " поля\033[0m"
        ),
        tty,
    )
    tty_print(
        (
            "\033[0;96m4. Скопируйте ваши \033[1;96mAPI ID\033[0;96m и \033[1;96mAPI"
            " hash\033[0m"
        ),
        tty,
    )

    while api_id := tty_input("\033[0;95mВведите API ID: \033[0m", tty):
        if api_id.isdigit():
            break

        tty_print("\033[0;91mНекорректный ID\033[0m", tty)

    if not api_id:
        tty_print("\033[0;91mОтменено\033[0m", tty)
        sys.exit(0)

    while api_hash := tty_input("\033[0;95mВведите API hash: \033[0m", tty):
        if len(api_hash) == 32 and all(
            symbol in string.hexdigits for symbol in api_hash
        ):
            break

        tty_print("\033[0;91mНекорректный hash\033[0m", tty)

    if not api_hash:
        tty_print("\033[0;91mОтменено\033[0m", tty)
        sys.exit(0)

    main.save_config_key("api_id", int(api_id))
    main.save_config_key("api_hash", api_hash)
    tty_print("\033[0;92mКонфигурация API сохранена\033[0m", tty)
