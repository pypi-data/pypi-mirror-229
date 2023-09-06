from os import getcwd
from pathlib import Path

from je_editor.utils.json.json_file import read_json
from je_editor.utils.json.json_file import write_json

user_setting_dict = {
    "font": "Lato",
    "font_size": 12,
    "encoding": "utf-8",
    "last_file": None,
    "python_compiler": None
}


def write_user_setting() -> None:
    user_setting_file = Path(getcwd() + "/user_setting.json")
    write_json(str(user_setting_file), user_setting_dict)


def read_user_setting() -> None:
    user_setting_file = Path(getcwd() + "/user_setting.json")
    if user_setting_file.exists() and user_setting_file.is_file():
        user_setting_dict.update(read_json(str(user_setting_file)))
