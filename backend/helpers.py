import json
import os
from typing import Any, TypedDict
from bot_enums import BOT_MODE, PLAY_MODE, SCORE_MODE, TEAM_MODE


class UserCredentialsDict(TypedDict):
    username: str
    password: str


def get_user_credentials() -> UserCredentialsDict:
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if username and password:
        return {
            "username": username,
            "password": password,
        }

    with open("config.json", "r") as f:
        configuration = json.loads(f.read())

    if not configuration.get("username") or not configuration.get("password"):
        raise KeyError(
            "No user IRC credentials found! set config.json or env vars to continue..."
        )

    return {
        "username": configuration.get("username"),
        "password": configuration.get("password"),
    }


def convert_to_tuples(data: dict[str, Any]) -> dict[str, Any]:
    """list to tuple"""
    beatmap_tuples = ["star", "ar", "cs", "od", "length", "bpm"]

    for key, value in data.items():
        if key in beatmap_tuples and type(value) == list:
            data[key] = tuple(value)

    return data


def enum_parser(data: dict[str, Any]) -> dict[str, Any]:
    room_enums = {
        "bot_mode": BOT_MODE,
        "play_mode": PLAY_MODE,
        "team_mode": TEAM_MODE,
        "score_mode": SCORE_MODE,
    }

    for key, value in data.items():
        enum_value = room_enums.get(key)

        if enum_value:
            try:
                data[key] = enum_value[value]
            except KeyError:
                data.pop(key)

    return data


def extract_enum(e: Any) -> list[str]:
    return [a.name for a in e]
