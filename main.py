import json
from irc import OsuIrc
from roombot import Room, RoomBot
from beatmaps import RoomBeatmap
from constants import BOT_MODE, TEAM_MODE, SCORE_MODE, PLAY_MODE

with open("config.json", "r") as f:
    configuration = json.loads(f.read())

if not configuration.get("username") or not configuration.get("password"):
    raise KeyError("username or password not found on config.json!")

irc = OsuIrc(
    username=configuration.get("username"),
    password=configuration.get("password"),
)
room_bot = RoomBot(irc=irc)
# room_bot.add_room(
#     Room(
#         irc=irc,
#         name="5.5-6.5* | AR9+ | JP songs | Auto Map Rotate",
#         password="",
#         bot_mode=1,
#         team_mode=0,
#         room_size=12,
#         beatmap=RoomBeatmap(
#             ar=(9.00, 10.00),
#             star=(5.5, 6.5),
#             length=(120, 240),
#             bpm=(0, 500),
#             asset_filename="list-std-ranked-jp.json",
#         )
#     )
# )

room_bot.add_room(
    Room(
        irc=irc,
        # name="5.0 - 6.0* | AR9+ | 0-5Mins | Auto Host Rotate",
        name="testing",
        password="test",
        bot_mode=BOT_MODE.AUTO_HOST,
        team_mode=TEAM_MODE.HEAD_TO_HEAD,
        score_mode=SCORE_MODE.SCORE,
        play_mode=PLAY_MODE.OSU,
        room_size=12,
        beatmap=RoomBeatmap(
            ar=(9.00, 10.00),
            star=(5.0, 6.0),
            length=(0, 300),
            bpm=(0, 500),
        ),
    )
)

try:
    room_bot.start()
except KeyboardInterrupt:
    irc.close()
