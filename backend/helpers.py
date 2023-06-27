import json
import os
from typing import Any, TypedDict
from bot_enums import BOT_MODE, PLAY_MODE, SCORE_MODE, TEAM_MODE, RANK_STATUS


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


def beatmap_enum_parser(beatmap: dict[str, Any]) -> dict[str, Any]:
    if "rank_status" in beatmap:
        rank_status = []

        for enum_key in beatmap["rank_status"]:
            try:
                rank_status.append(RANK_STATUS[enum_key])
            except ValueError as err:
                print("Rank enum key error", err)
                pass

        beatmap["rank_status"] = rank_status

    return beatmap


def room_enum_parser(room: dict[str, Any]) -> dict[str, Any]:
    room_enums = {
        "bot_mode": BOT_MODE,
        "play_mode": PLAY_MODE,
        "team_mode": TEAM_MODE,
        "score_mode": SCORE_MODE,
    }

    for room_key, enum in room_enums.items():
        if room_key not in room:
            continue
        try:
            room[room_key] = enum[room[room_key]]
        except KeyError:
            room.pop(room_key)

    return room


def extract_enum(e: Any) -> list[str]:
    return [a.name for a in e]
