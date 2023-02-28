import os
import sys
import winreg

import vdf
from pyautogui import size as resolution

STEAM_CONFIG: str = r"/steamapps/libraryfolders.vdf"
GAME_APPID: str = "1046930"
GAME_SETTINGS_DIR: str = r"/steamapps/common/Underlords/game/dac/cfg/video.txt"


def get_resolution() -> int:
    """Получает разрешение основного монитора."""
    width, height = resolution()
    return width, height


def locate_steam() -> str:
    """
    Ищет путь установки Steam в регистре, а именно папку со 'steam.exe'.
    Возвращает ответ в формате 'диск:/Steam'.
    """
    try:
        hkey = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"
        )
    except Exception as error:
        hkey = None
        print(sys.exc_info(error))

    try:
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")
    except Exception as error:
        steam_path = None
        print(sys.exc_info(error))

    return steam_path[0]


def locate_game_drive(steam_path: str) -> str:
    """
    Определяет, на каком диске установлена игра,
    возвращает строку в формате: 'диск:/Steam'.
    """
    steam_config_path: str = rf"{steam_path}{STEAM_CONFIG}"

    with open(steam_config_path, "r") as f:
        f = vdf.load(f)

    for i in f["libraryfolders"]:
        if GAME_APPID in f["libraryfolders"][f"{i}"]["apps"].keys():
            game_path: str = f["libraryfolders"][f"{i}"]["path"]

    return game_path


def change_settings(game_drive: str, width: int, height: int):
    """
    Проверяет наличие файла 'video.txt' в директории игры, делает его бэкап,
    перезаписывает настройки разрешения.
    """
    settings_file = rf"{game_drive}{GAME_SETTINGS_DIR}"
    if os.path.isfile(settings_file) is False:
        sys.exit(
            "В папке игры нет файла с настройками видео. "
            "Убедитесь, что после утановки игра была запущена хотя бы раз."
        )

    with open(settings_file, "r") as f:
        f = vdf.load(f)

    vdf.dump(f, open(f"{settings_file} backup.txt", "w"), pretty=True)
    print("Бэкап сохранён.")
    f["video.cfg"].update(
        {"setting.defaultres": width}
    )
    f["video.cfg"].update(
        {"setting.defaultresheight": height}
    )
    vdf.dump(f, open(settings_file, "w"), pretty=True)
    print(f"Разрешение изменено на {width}x{height}.")


def run_game(steam_path: str):
    """Запускает игру."""
    os.chdir(f"{steam_path}")
    os.system(f"steam steam://rungameid/{GAME_APPID} -novid")
    print("Игра запускается...")


def main():
    """Основная логика работы скрипта."""
    try:
        steam_path = locate_steam()
        game_drive = locate_game_drive(steam_path)
        width, height = get_resolution()
        change_settings(game_drive, width, height)
        run_game(steam_path)
        sys.exit()

    except Exception as error:
        sys.exit(
            f"Произошла неизвестная ошибка: {error}."
            "Работа скрипта остановлена."
        )


if __name__ == "__main__":
    main()
