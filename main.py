import json
from irc import OsuIrc
from roombot import Room, RoomBot

with open("config.json", "r") as f:
    configuration = json.loads(f.read())

if not configuration.get("username") or not configuration.get("password"):
    raise KeyError("username or password not found on config.json!")

irc = OsuIrc(
    username=configuration.get("username"),
    password=configuration.get("password"),
)
irc.start()
room_bot = RoomBot(irc=irc)
# room_bot.add_room(
#     Room(
#         irc=irc,
#         name="5-6* | ar9+ | 2-5mins | jp | test",
#         password="test",
#         bot_mode=1,
#         team_mode=2,
#         ar=(9.00, 10.00),
#         star=(5.00, 6.00),
#         length=(120, 300),
#         bpm=(170, 500),
#         beatmapset_filename="chimu-std-jp-ranked-5to7star.json",
#     )
# )
# room_bot.add_room(Room(irc=irc, name="yeet 02", password="test", bot_mode=0))
try:
    room_bot.start()
except KeyboardInterrupt:
    irc.close()
