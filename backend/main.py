import json
from irc import OsuIrc
from roombot import Room, RoomBot
from beatmaps import RoomBeatmap
from bot_enums import BOT_MODE, TEAM_MODE

with open("config.json", "r") as f:
    configuration = json.loads(f.read())

if not configuration.get("username") or not configuration.get("password"):
    raise KeyError("username or password not found on config.json!")

irc = OsuIrc(
    username=configuration.get("username"),
    password=configuration.get("password"),
)
room_bot = RoomBot(irc=irc)

###
### start add room here
###

room_bot.add_room(
    Room(
        irc=irc,
        name="5.5-6.5* | AR9+ 2-4Mins | Test Auto Map Rotate",
        password="test",
        bot_mode=BOT_MODE.AUTO_ROTATE_MAP,
        team_mode=TEAM_MODE.HEAD_TO_HEAD,
        room_size=12,
        beatmap=RoomBeatmap(
            ar=(9.00, 10.00),
            star=(5.5, 6.5),
            length=(120, 240),
            bpm=(0, 500),
        ),
    )
)

###
### end add room
###

try:
    room_bot.start()
except KeyboardInterrupt:
    irc.close()
