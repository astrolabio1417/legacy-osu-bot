import os
from typing import Any
from flask import Flask, request, send_from_directory, session
from bot.irc import OsuIrc
from bot.roommanager import RoomManager
from bot.room import Room
from bot.beatmap import RoomBeatmap
from bot.enums import BOT_MODE, TEAM_MODE, SCORE_MODE, PLAY_MODE, RANK_STATUS, RoomData
from flask_cors import CORS
from bot.helpers import (
    parse_room_data,
    extract_enum,
    get_user_credentials,
    is_password_valid,
    is_username_valid,
)
from app_enums import BotEnums, LoginResponse, MessageResponse, Session
from ossapi.enums import BeatmapsetSearchGenre, BeatmapsetSearchLanguage


app = Flask(__name__, static_folder="dist")
app.secret_key = os.environ.get("SECRET_KEY", "BAD_SECRET_KEY")
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

credentials = get_user_credentials()

irc = OsuIrc(username=credentials.get("username", ""), password=credentials.get("password", ""))

roommanager = RoomManager(irc=irc)


def create_room(data: Any) -> tuple[RoomData | MessageResponse, int]:
    try:
        parse_room_data(data)
    except Exception as e:
        return {"message": str(e)}, 400

    data["irc"] = irc
    data["beatmap"] = RoomBeatmap(**data.pop("beatmap"))
    room = Room(**data)
    new_room = roommanager.add_room(room)
    new_room.create()

    return new_room.get_json(), 201


def update_room(unique_id: str, data: Any) -> tuple[MessageResponse | RoomData, int]:
    if not unique_id:
        return {"message": "Missing room_id on data"}, 400

    try:
        parse_room_data(data)
    except Exception as e:
        return {"message": str(e)}, 400

    room = roommanager.get_room(unique_id=unique_id)

    if not room:
        return {"message": "No room found!"}, 400

    room.configure(**data)

    return room.get_json(), 200


def delete_room(room_unique_id: str) -> tuple[MessageResponse | RoomData, int]:
    if not session.get("is_admin"):
        return {"message": "You are not Authorized user!"}, 401

    if not room_unique_id:
        return {"message": "Missing room_id"}, 400

    room = roommanager.get_room(unique_id=room_unique_id)

    if not room:
        return {"message": "No room found!"}, 400

    room.send_close()
    roommanager.remove_room(room)

    return {"message": "Room has been deleted"}, 204


@app.route("/room", methods=["GET", "POST", "DELETE", "PUT"])
def room() -> tuple[MessageResponse | RoomData | list[RoomData], int]:
    if not irc.is_running:
        return {"message": "Irc is not running..."}, 400

    if request.method == "GET":
        return roommanager.get_rooms_json(), 200

    if request.method == "POST":
        print(session)
        print(session.get("is_admin"))
        if not session.get("is_admin"):
            return {"message": "You are not Authorized user!"}, 401

        return create_room(request.get_json())

    return {"message": "Wrong Method!"}, 400


@app.route("/room/<room_unique_id>", methods=["GET", "PUT", "DELETE"])
def room_view(room_unique_id: str) -> tuple[MessageResponse | RoomData, int]:
    if not irc.is_running:
        return {"message": "Irc is not running..."}, 400

    if request.method == "GET":
        room = roommanager.get_room(unique_id=room_unique_id)

        if not room:
            return {"message": "No room found"}, 400

        return room.get_json(), 200

    if not session.get("is_admin"):
        return {"message": "You are not Authorized user!"}, 401

    if request.method == "PUT":
        return update_room(room_unique_id, request.get_json())

    if request.method == "DELETE":
        return delete_room(room_unique_id)

    return {"message": "Wrong Method"}, 400


@app.route("/start")
def start_irc() -> Any:
    if not session.get("is_admin"):
        return {"message": "You are not Authorized user!"}, 401

    if irc.is_running:
        return {"message": "IRC is already running..."}, 400

    irc.start()
    roommanager.start(run_on_thread=True)
    return {"message": "IRC is now running..."}, 200


@app.route("/stop")
def stop_irc() -> tuple[MessageResponse, int]:
    if not session.get("is_admin"):
        return {"message": "You are not Authorized user!"}, 401

    irc.stop()
    return {"message": "IRC is now stopped..."}, 200


@app.route("/session/login", methods=["POST"])
def login() -> tuple[LoginResponse | MessageResponse, int]:
    if request.method != "POST":
        return {"message": "Wrong Method!"}, 400

    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not is_username_valid(username) or not is_password_valid(password):
        return {"message": "Invalid username or password"}, 400

    session["username"] = username
    session["password"] = password
    session["is_admin"] = True

    return {
        "message": "ok",
        "is_admin": True,
        "is_irc_running": irc.is_running,
        "username": username,
    }, 200


@app.route("/session/logout", methods=["POST"])
def logout() -> tuple[dict[str, Any], int]:
    if request.method == "POST":
        session.clear()
        return {}, 204

    return {}, 400


@app.route("/session")
def get_session() -> Session:
    return {
        "username": session.get("username", ""),
        "is_admin": session.get("is_admin") is True,
        "is_irc_running": irc.is_running,
    }


Enums: BotEnums = {
    "BOT_MODE": extract_enum(BOT_MODE),
    "TEAM_MODE": extract_enum(TEAM_MODE),
    "SCORE_MODE": extract_enum(SCORE_MODE),
    "PLAY_MODE": extract_enum(PLAY_MODE),
    "RANK_STATUS": extract_enum(RANK_STATUS),
    "BEATMAP_GENRE": extract_enum(BeatmapsetSearchGenre),
    "BEATMAP_LANGUAGE": extract_enum(BeatmapsetSearchLanguage),
}


@app.route("/enums")
def bot_enums() -> BotEnums:
    return Enums


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str) -> Any:
    if path != "" and os.path.exists(f"{app.static_folder}" + "/" + path):
        return send_from_directory(f"{app.static_folder}", path)

    return send_from_directory(f"{app.static_folder}", "index.html")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    DEBUG = bool(os.environ.get("DEBUG") == "True")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
