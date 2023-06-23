import os
from typing import Any
from flask import Flask, request
import threading
from irc import OsuIrc
from roombot import Room, RoomBot
from beatmaps import RoomBeatmap
from bot_enums import BOT_MODE, TEAM_MODE, SCORE_MODE, PLAY_MODE
from roombot import Room
from flask_cors import CORS
from helpers import (
    convert_to_tuples,
    enum_parser,
    extract_enum,
    get_user_credentials,
)

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

credentials = get_user_credentials()

irc = OsuIrc(
    username=credentials["username"],
    password=credentials["password"],
)
room_bot = RoomBot(irc=irc)


try:
    threading.Thread(target=room_bot.start, args=()).start()
except KeyboardInterrupt:
    irc.close()


def create_room(data: Any) -> tuple[dict[str, Any], int]:
    beatmap = data.pop("beatmap", {})

    convert_to_tuples(beatmap)
    enum_parser(data)

    data["irc"] = irc
    data["beatmap"] = RoomBeatmap(**beatmap)
    new_room = room_bot.add_room(Room(**data))
    new_room.create()

    return new_room.get_json(), 201


def update_room(unique_id: str, data: Any) -> tuple[dict[str, Any], int]:
    beatmap = data.pop("beatmap", {})

    convert_to_tuples(beatmap)
    enum_parser(data)

    data["beatmap"] = beatmap

    if not unique_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(unique_id=unique_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.setattrs(**data)

    return room.get_json(), 200


def delete_room(room_unique_id: str) -> tuple[dict[str, Any], int]:
    if not room_unique_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(unique_id=room_unique_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.send_close()

    return {"id": room_unique_id}, 204


@app.route("/")
def hello_world() -> str:
    return "<h1>Hello world</h1>"


@app.route("/room", methods=["GET", "POST", "DELETE", "PUT"])
def room() -> Any:
    if request.method == "GET":
        return room_bot.get_rooms_json(), 200

    if request.method == "POST":
        return create_room(request.get_json())

    return {"status": 400, "message": "Wrong Method!"}, 400


@app.route("/room/<room_unique_id>", methods=["GET", "PUT", "DELETE"])
def room_view(room_unique_id: str) -> Any:
    if request.method == "GET":
        room = room_bot.get_room(unique_id=room_unique_id)

        if not room:
            return {"message": "No room found", "status": 400}, 400

        return room.get_json(), 200

    if request.method == "PUT":
        return update_room(room_unique_id, request.get_json())

    if request.method == "DELETE":
        return delete_room(room_unique_id)

    return {}, 400


@app.route("/enums")
def bot_enums() -> Any:
    return {
        "BOT_MODE": extract_enum(BOT_MODE),
        "TEAM_MODE": extract_enum(TEAM_MODE),
        "SCORE_MODE": extract_enum(SCORE_MODE),
        "PLAY_MODE": extract_enum(PLAY_MODE),
    }


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=PORT)
