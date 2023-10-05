import json
import os
from typing import Any
from bot.enums import (
    BOT_MODE,
    PLAY_MODE,
    SCORE_MODE,
    TEAM_MODE,
    RANK_STATUS,
    UserCredentials,
)
from ossapi.enums import BeatmapsetSearchGenre, BeatmapsetSearchLanguage


def get_user_credentials() -> UserCredentials:
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if username and password:
        return {
            "username": username,
            "password": password,
        }

    if not os.path.exists("config.json"):
        raise KeyError("Env vars or config.json is required!")

    with open("config.json", "r") as f:
        configuration = json.loads(f.read())

    if not configuration.get("username") or not configuration.get("password"):
        raise KeyError("No user IRC credentials found! set config.json or env vars to continue...")

    return {
        "username": configuration.get("username"),
        "password": configuration.get("password"),
    }


def parse_beatmap_data(beatmap: dict[str, Any]) -> dict[str, Any]:
    required_keys = [
        "star",
        "play_mode",
        "ar",
        "cs",
        "length",
        "bpm",
        "rank_status",
        "genre",
        "language",
    ]

    if not isinstance(beatmap, dict) or not all(key in beatmap for key in required_keys):
        raise ValueError("Invalid beatmap data")

    keys_to_convert = ["star", "ar", "cs", "od", "length", "bpm"]

    for key in keys_to_convert:
        if key in beatmap and isinstance(beatmap[key], list):
            beatmap[key] = tuple(beatmap[key])

    beatmap["rank_status"] = [RANK_STATUS[status] for status in beatmap["rank_status"]]

    beatmap_enums = {
        "genre": BeatmapsetSearchGenre,
        "language": BeatmapsetSearchLanguage,
    }

    for beatmap_key, enum in beatmap_enums.items():
        if beatmap_key not in beatmap:
            continue

        beatmap[beatmap_key] = enum[beatmap[beatmap_key]]

    return beatmap


def parse_room_data(room: dict[str, Any]) -> dict[str, Any]:
    required_keys = [
        "name",
        "bot_mode",
        "play_mode",
        "team_mode",
        "score_mode",
        "room_size",
    ]

    if not isinstance(room, dict) or not all(key in room for key in required_keys):
        raise ValueError("Invalid room data")

    room_enums = {
        "bot_mode": BOT_MODE,
        "play_mode": PLAY_MODE,
        "team_mode": TEAM_MODE,
        "score_mode": SCORE_MODE,
    }

    for room_key, enum in room_enums.items():
        room[room_key] = enum[room.get(room_key, None)]

    room["beatmap"]["play_mode"] = room.get("play_mode", PLAY_MODE.OSU)
    parse_beatmap_data(room["beatmap"])

    return room


def extract_enum(enum: Any) -> list[str]:
    return [a.name for a in enum]


def is_username_valid(username: str) -> bool:
    user_credentials = get_user_credentials()
    return str(username) == user_credentials.get("username")


def is_password_valid(password: str) -> bool:
    user_credentials = get_user_credentials()
    return str(password) == user_credentials.get("password")
