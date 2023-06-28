import os
from typing import Any
from flask import Flask, request, send_from_directory, session
from irc import OsuIrc
from roombot import Room, RoomBot
from beatmaps import RoomBeatmap
from bot_enums import BOT_MODE, TEAM_MODE, SCORE_MODE, PLAY_MODE, RANK_STATUS
from roombot import Room
from flask_cors import CORS
from helpers import (
    convert_to_tuples,
    room_enum_parser,
    extract_enum,
    get_user_credentials,
    beatmap_enum_parser,
    is_password_valid,
    is_username_valid,
)

app = Flask(__name__, static_folder="dist")
app.secret_key = "BAD_SECRET_KEY"
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

credentials = get_user_credentials()

irc = OsuIrc(
    username=credentials.get("username", ""), password=credentials.get("password", "")
)
room_bot = RoomBot(irc=irc)


def create_room(data: Any) -> tuple[dict[str, Any], int]:
    beatmap = data.pop("beatmap", {})
    beatmap_enum_parser(beatmap)
    convert_to_tuples(beatmap)
    room_enum_parser(data)

    data["irc"] = irc
    data["beatmap"] = RoomBeatmap(**beatmap)
    new_room = room_bot.add_room(Room(**data))
    new_room.create()

    return new_room.get_json(), 201


def update_room(unique_id: str, data: Any) -> tuple[dict[str, Any], int]:
    beatmap = data.pop("beatmap", {})
    beatmap_enum_parser(beatmap)
    convert_to_tuples(beatmap)
    room_enum_parser(data)

    data["beatmap"] = beatmap

    if not unique_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(unique_id=unique_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.setattrs(**data)

    return room.get_json(), 200


def delete_room(room_unique_id: str) -> tuple[dict[str, Any], int]:
    if not is_username_valid(session.get("username", "")) or not is_password_valid(
        session.get("password", "")
    ):
        return {"message": "You are not Authorized user!"}, 401

    if not room_unique_id:
        return {"status": 400, "message": "Missing room_id on data"}, 400

    room = room_bot.get_room(unique_id=room_unique_id)

    if not room:
        return {"status": 400, "message": "No room found!"}, 400

    room.send_close()

    return {"id": room_unique_id}, 204


@app.route("/room", methods=["GET", "POST", "DELETE", "PUT"])
def room() -> Any:
    if not irc.is_running:
        return {"message": "Irc is not running..."}, 400

    if request.method == "GET":
        return room_bot.get_rooms_json(), 200

    if not is_username_valid(session.get("username", "")) or not is_password_valid(
        session.get("password", "")
    ):
        return {"message": "You are not Authorized user!"}, 401

    if request.method == "POST":
        return create_room(request.get_json())

    return {"status": 400, "message": "Wrong Method!"}, 400


@app.route("/room/<room_unique_id>", methods=["GET", "PUT", "DELETE"])
def room_view(room_unique_id: str) -> Any:
    if not irc.is_running:
        return {"message": "Irc is not running..."}, 400

    if request.method == "GET":
        room = room_bot.get_room(unique_id=room_unique_id)

        if not room:
            return {"message": "No room found", "status": 400}, 400

        return room.get_json(), 200

    if not is_username_valid(session.get("username", "")) or not is_password_valid(
        session.get("password", "")
    ):
        return {"message": "You are not Authorized user!"}, 401

    if request.method == "PUT":
        return update_room(room_unique_id, request.get_json())

    if request.method == "DELETE":
        return delete_room(room_unique_id)

    return {}, 400


@app.route("/start")
def start_irc() -> Any:
    if not is_username_valid(session.get("username", "")) or not is_password_valid(
        session.get("password", "")
    ):
        return {"message": "You are not Authorized user!"}, 401

    if irc.is_running:
        return {"message": "irc is running..."}, 400

    irc.start()
    room_bot.start(run_on_thread=True)
    return {"message": "irc is now running..."}, 200


@app.route("/stop")
def stop_irc() -> Any:
    if not is_username_valid(session.get("username", "")) or not is_password_valid(
        session.get("password", "")
    ):
        return {"message": "You are not Authorized user!"}, 401

    irc.stop()
    return {"message": "Irc is dead..."}, 200


@app.route("/session/login", methods=["POST"])
def login() -> Any:
    if request.method != "POST":
        return {}, 400

    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not is_username_valid(username) or not is_password_valid(password):
        return {"message": "Invalid username or password"}, 400

    session["username"] = username
    session["password"] = password
    session["is_admin"] = True

    return {"message": "ok"}, 200

@app.route("/session/logout", methods=["POST"])
def logout() -> Any:
    if request.method == 'POST':
        session.clear()
        return {}, 204
    
    return {}, 400

@app.route("/session")
def get_session() -> Any:
    return {
        "username": session.get("username", ""),
        "is_admin": session.get("is_admin"),
        "is_irc_running": irc.is_running,
    }


@app.route("/enums")
def bot_enums() -> Any:
    return {
        "BOT_MODE": extract_enum(BOT_MODE),
        "TEAM_MODE": extract_enum(TEAM_MODE),
        "SCORE_MODE": extract_enum(SCORE_MODE),
        "PLAY_MODE": extract_enum(PLAY_MODE),
        "RANK_STATUS": extract_enum(RANK_STATUS),
    }


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str) -> Any:
    if path != "" and os.path.exists(f"{app.static_folder}" + "/" + path):
        return send_from_directory(f"{app.static_folder}", path)

    return send_from_directory(f"{app.static_folder}", "index.html")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=PORT)
