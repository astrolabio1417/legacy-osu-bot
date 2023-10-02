import json
from bot.room import Room
from bot.roommanager import RoomManager
from bot.beatmap import RoomBeatmap
from bot.irc import OsuIrc
from bot.enums import BOT_MODE, TEAM_MODE, PLAY_MODE, SCORE_MODE

with open("config.json", "r") as f:
    configuration = json.loads(f.read())

if not configuration.get("username") or not configuration.get("password"):
    raise KeyError("username or password not found on config.json!")

irc = OsuIrc(
    username=configuration.get("username"),
    password=configuration.get("password"),
)
room_manager = RoomManager(irc=irc)

###
### start add room here
###

# room_bot.add_room(
#     Room(
#         irc=irc,
#         name="test x",
#         password="test",
#         bot_mode=BOT_MODE.AUTO_ROTATE_MAP,
#         team_mode=TEAM_MODE.HEAD_TO_HEAD,
#         room_size=12,
#         beatmap=RoomBeatmap(
#             ar=(9.00, 10.00),
#             star=(5.5, 6.5),
#             length=(120, 240),
#             bpm=(0, 500),
#         ),
#     )
# )


room_manager.add_room(
    Room(
        irc=irc,
        name="test1",
        beatmap=RoomBeatmap(
            play_mode=PLAY_MODE.OSU,
            ar=(9.00, 10.00),
        ),
        bot_mode=BOT_MODE.AUTO_HOST,
        team_mode=TEAM_MODE.HEAD_TO_HEAD,
        room_size=12,
        password="test",
        play_mode=PLAY_MODE.OSU,
        score_mode=SCORE_MODE.SCORE,
    )
)


###
### end add room
###


try:
    room_manager.start(run_on_thread=True)
    room_manager.create_rooms()
    a = input("Enter to exit")
except KeyboardInterrupt:
    irc.close()
