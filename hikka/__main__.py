"""Entry point. Checks for user and starts main script"""

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import getpass
import os
import subprocess
import sys

from ._internal import restart

if (
    getpass.getuser() == "root"
    and "--root" not in " ".join(sys.argv)
    and all(trigger not in os.environ for trigger in {"DOCKER", "GOORM"})
):
    print("🚫" * 15)
    print("Вы пытаетесь запустить Hikka от имени суперпользователя (root).")
    print("Пожалуйста, создайте нового пользователя и перезапустите скрипт.")
    print("Если это действие намеренное, передайте аргумент --root.")
    print("🚫" * 15)
    print()
    print("Введите force_insecure, чтобы проигнорировать это предупреждение")
    if input("> ").lower() != "force_insecure":
        sys.exit(1)


def deps():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-q",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            "-r",
            "requirements.txt",
        ],
        check=True,
    )


if sys.version_info < (3, 8, 0):
    print("🚫 Ошибка: вы должны использовать Python версии 3.8.0 или выше")
elif __package__ != "hikka":  # In case they did python __main__.py
    print("🚫 Ошибка: вы не можете запускать это как скрипт; используйте запуск как модуль (python3 -m hikka)")
else:
    try:
        import hikkatl
    except Exception:
        pass
    else:
        try:
            import hikkatl  # noqa: F811

            if tuple(map(int, hikkatl.__version__.split("."))) < (2, 0, 4):
                raise ImportError

            import hikkapyro

            if tuple(map(int, hikkapyro.__version__.split("."))) < (2, 0, 103):
                raise ImportError
        except ImportError:
            print("🔄 Установка зависимостей...")
            deps()
            restart()

    try:
        from . import log

        log.init()

        from . import main
    except ImportError as e:
        print(f"{str(e)}\n🔄 Попытка установки зависимостей... Просто подождите ⏱")
        deps()
        restart()

    if "HIKKA_DO_NOT_RESTART" in os.environ:
        del os.environ["HIKKA_DO_NOT_RESTART"]

    main.hikka.main()  # Execute main function
