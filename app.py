import json
from typing import Any
from flask import Flask, request
import json
import threading
from irc import OsuIrc
from roombot import Room, RoomBot
from beatmaps import RoomBeatmap
from bot_enums import BOT_MODE, TEAM_MODE, SCORE_MODE, PLAY_MODE
from roombot import Room
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

with open("config.json", "r") as f:
    configuration = json.loads(f.read())

if not configuration.get("username") or not configuration.get("password"):
    raise KeyError("username or password not found on config.json!")

irc = OsuIrc(
    username=configuration.get("username"),
    password=configuration.get("password"),
)
room_bot = RoomBot(irc=irc)


try:
    threading.Thread(target=room_bot.start, args=()).start()
except KeyboardInterrupt:
    irc.close()


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


def create_room(data: Any) -> dict[str, Any]:
    beatmap = data.pop("beatmap", {})

    convert_to_tuples(beatmap)
    enum_parser(data)

    data["irc"] = irc
    data["beatmap"] = RoomBeatmap(**beatmap)
    room_bot.add_room(Room(**data)).create()

    return {"message": "Room has been created!", "status": 201}


def update_room(room_id: str, data: Any) -> tuple[dict[str, Any], int]:
    beatmap = data.pop("beatmap", {})

    convert_to_tuples(beatmap)
    enum_parser(data)

    data["beatmap"] = beatmap

    if not room_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(room_id=room_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.setattrs(**data)

    return {"status": 200, "message": "Room has been updated!"}, 200


def delete_room(room_id: str) -> tuple[dict[str, Any], int]:
    if not room_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(room_id=room_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.close()

    return {"status": 200, "message": "Room has been closed!"}, 204


@app.route("/")
def hello_world() -> str:
    return "<h1>Hello world</h1>"


@app.route("/room", methods=["GET", "POST", "DELETE", "PUT"])
def room() -> Any:
    if request.method == "GET":
        return {"lists": room_bot.get_rooms_json(), "status": 200, "message": "ok"}, 200

    if request.method == "POST":
        return create_room(request.get_json()), 201

    return {"status": 400, "message": "Wrong Method!"}, 400


@app.route("/room/<room_id>", methods=["GET", "PUT", "DELETE"])
def room_view(room_id: str) -> Any:
    if request.method == "GET":
        room = room_bot.get_room(room_id=f"#{room_id}")

        if not room:
            return {"message": "No room found", "status": 400}, 400

        return room.get_json(), 200

    if request.method == "PUT":
        return update_room(f"#{room_id}", request.get_json())

    if request.method == "DELETE":
        return delete_room(f"#{room_id}")

    return room_id


@app.route("/enums")
def bot_enums() -> Any:
    return {
        "BOT_MODE": extract_enum(BOT_MODE),
        "TEAM_MODE": extract_enum(TEAM_MODE),
        "SCORE_MODE": extract_enum(SCORE_MODE),
        "PLAY_MODE": extract_enum(PLAY_MODE),
    }


def extract_enum(e: Any) -> list[dict[str, Any]]:
    return [{"name": a.name, "value": a.value} for a in e]
