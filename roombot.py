from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import re
from dataclasses import dataclass, field
from parsers import parse_message, parse_slot, parse_username
from scraper import fetch_beatmap
from beatmaps import message_beatmap_links
from constants import BOT_MODE, PLAY_MODE, SCORE_MODE, TEAM_MODE

if TYPE_CHECKING:
    from beatmaps import RoomBeatmapDict
    from irc import OsuIrc


@dataclass
class Room:
    irc: OsuIrc
    name: str = "yeet"
    room_id: str = ""
    password: str = "test"
    closed: bool = False

    bot_mode: int = 0
    play_mode: int = 0
    team_mode: int = 0
    score_mode: int = 0
    room_size: int = 16

    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    od: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)
    __beatmap: int = 0

    __beatmaps: list[RoomBeatmapDict] = field(default_factory=list)
    __users: list[str] = field(default_factory=list)
    __skips: list[str] = field(default_factory=list)
    beatmapset_filename: str = "chimu-std-ranked-5to7star.json"

    __tmp_users: list[str] = field(default_factory=list)
    __tmp_total_users: int = 0

    __connected = False
    __created = False
    __configured = False

    def __post_init__(self) -> None:
        modes = [
            ("Bot mode", self.bot_mode, BOT_MODE),
            ("Play mode", self.play_mode, PLAY_MODE),
            ("Team mode", self.team_mode, TEAM_MODE),
            ("Score mode", self.score_mode, SCORE_MODE),
        ]
        beatmap_stats = [
            ("star", self.star),
            ("approach rate", self.ar),
            ("overall difficulty", self.od),
            ("circle size", self.cs),
        ]

        for name, selected, selection in modes:
            if selected not in selection:
                raise ValueError(f"{name} is invalid.")

        for name, setting in beatmap_stats:
            if setting[0] < 0 or setting[1] > 10:
                raise ValueError(f"{name} is invalid.")

        if self.bot_mode == 1:
            self.load_beatmaps(self.beatmapset_filename)

    def load_beatmaps(self, filename: str) -> Optional[list[RoomBeatmapDict]]:
        import json

        with open(f"beatmapsets/{filename}", "r") as f:
            try:
                beatmaplist: list[RoomBeatmapDict] = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return None

            if beatmaplist:
                valid_beatmaps = []

                for beatmap in beatmaplist:
                    if not beatmap.get("beatmap_id", False):
                        print(beatmap.get("beatmap_id"))
                        continue

                    play_mode = beatmap.get("gamemode", -1) == self.play_mode
                    ar = (
                        beatmap.get("difficulty_ar", 0.00) >= self.ar[0]
                        and beatmap.get("difficulty_ar", 0.00) <= self.ar[1]
                    )
                    star = (
                        beatmap.get("difficulty", 0.00) >= self.star[0]
                        and beatmap.get("difficulty", 0.00) <= self.star[1]
                    )
                    length = (
                        beatmap.get("total_length", 0) >= self.length[0]
                        and beatmap.get("total_length", 0) <= self.length[1]
                    )
                    bpm = beatmap.get("bpm", 0) >= self.bpm[0] and beatmap.get(
                        "bpm", 0
                    ) <= beatmap.get("bpm", 0)

                    if play_mode and ar and star and length and bpm:
                        valid_beatmaps.append(beatmap)

                import random

                random.shuffle(valid_beatmaps)
                print(f"{len(valid_beatmaps)} Total beatmaps!")
                self.__beatmaps = valid_beatmaps
                return self.__beatmaps
        return None

    def update(
        self,
        name: Optional[str],
        password: Optional[str],
        play_mode: Optional[int],
        team_mode: Optional[int],
        score_mode: Optional[int],
        room_size: Optional[int],
    ) -> None:
        self.name = name or self.name
        self.password = password or self.password
        self.play_mode = play_mode or self.play_mode
        self.team_mode = team_mode or self.team_mode
        self.score_mode = score_mode or self.score_mode
        self.room_size = room_size or self.room_size

    def check_room(self) -> None:
        """create the room or reconnect to the room"""
        if self.closed:
            return

        if not self.irc.connected:
            return

        if self.room_id and not self.__connected:
            self.irc.send(f"JOIN {self.room_id}")
            self.__connected = True
        elif not self.__created:
            self.irc.send_private("BanchoBot", f"mp make {self.name}")
            self.__created = True

    def disconnect(self) -> None:
        """disconnection of irc socket"""
        self.__connected = False

    def on_match_created(self, room_id: str) -> None:
        print(f"Room Created {room_id} {self.name}")
        self.room_id = room_id
        self.setup()
        self.rotate()

    def on_match_closed(self) -> None:
        print(f"Close the match {self.name} {self.room_id}")
        self.closed = True
        self.__created = False
        self.__configured = False
        self.room_id = ""

    def setup(self) -> None:
        print(f"Setup {self.room_id} {self.name}")
        messages = [
            f"!mp name {self.name}",
            f"!mp password {self.password}",
            f"!mp set {self.team_mode} {self.score_mode} {self.room_size}",
            "!mp mods Freemod",
        ]

        for message in messages:
            self.irc.send_private(self.room_id, message)

        self.__configured = True

    def rotate(self) -> None:
        if self.bot_mode == 0:
            self.rotate_host()
        elif self.bot_mode == 1:
            self.rotate_beatmap()
        self.__skips = []

    def rotate_host(self) -> None:
        if self.__users:
            self.__users = self.__users[1:] + self.__users[0:1]
            self.irc.send_private(self.room_id, f"!mp host {self.__users[0]}")

    def rotate_beatmap(self) -> None:
        if self.__beatmaps:
            self.irc.send_private(
                self.room_id,
                f"!mp map {self.__beatmaps[0].get('beatmap_id', 0)} {self.play_mode}",
            )
            self.__beatmaps = self.__beatmaps[1:] + self.__beatmaps[0:1]

    def on_user_joined(self, username: str) -> None:
        username = parse_username(username)
        print(f"{self.room_id}: {username} joined the room.")

        if username not in self.__users:
            self.__users.append(username)
            print(f"{self.room_id}: {username} has been added")

        if self.bot_mode == 0 and len(self.__users) == 1:
            self.rotate_host()

    def on_user_left(self, username: str) -> None:
        print(f"{self.room_id}: {username} left the room.")

        # autohost | rotate on host leave
        if self.bot_mode == 0 and self.__users and self.__users[0] == username:
            self.rotate_host()

        if username in self.__users:
            self.__users.remove(username)

    def on_host_changed(self, username: str) -> None:
        print(f"{self.room_id}: changed host to {username}")
        self.__skips = []

        # auto host
        if self.bot_mode == 0 and self.__users[0] != username:
            self.rotate_host()

    def on_match_started(self) -> None:
        print(f"{self.room_id}: Match started")
        self.__skips = []

        if self.bot_mode == 0:
            self.rotate_host()

    def get_queue(self) -> str:
        if self.bot_mode == 0:
            return ", ".join(self.__users[0:5])
        elif self.bot_mode == 1 and self.__beatmaps:
            message = [
                f"[https://osu.ppy.sh/b/{beatmap.get('beatmap_id', 0)} {beatmap.get('title', 'no_title')}]"
                for beatmap in self.__beatmaps[0:5]
            ]
            return ", ".join(message)

        return "no_queue"

    def on_match_finished(self) -> None:
        print(f"{self.room_id}: Match finished")
        self.irc.send_private(
            self.room_id,
            f"!mp settings | Queue: {self.get_queue()}",
        )

        # auto rotate map
        if self.bot_mode == 1:
            self.rotate_beatmap()

    def on_match_ready(self) -> None:
        print(f"{self.room_id}: Match ready")
        self.irc.send_private(self.room_id, "!mp start")

    def on_beatmap_changed_to(
        self,
        title: str,
        version: str,
        url: str,
        beatmap_id: int,
    ) -> None:
        print(f"{self.room_id}: Beatmap change to {title} {url}")
        self.irc.send_private(
            self.room_id,
            f"!mp map {beatmap_id} {self.play_mode}",
        )

    def on_changed_beatmap_to(
        self, title: str, url: str, beatmap_id: int
    ) -> None:
        print(f"{self.room_id}: Change beatmap to {title} {url}")
        self.__skips = []
        beatmap = fetch_beatmap(url=url)

        if beatmap:
            beatmapset_id = beatmap.get("id", self.__beatmap)
            self.__beatmap = (
                beatmapset_id if type(beatmapset_id) == int else self.__beatmap
            )
            self.irc.send_private(
                self.room_id,
                f"Alternative Links: {message_beatmap_links(title, beatmap.get('id', 0))}",
            )

    def on_slot(
        self,
        slot: int,
        status: str,
        user_id: str,
        username: str,
        roles: list[str],
    ) -> None:
        self.__tmp_users.append(username)
        print(
            f"{self.room_id}: {username}[{user_id}] - Slot {slot} | Status {status} | Roles: {roles}"
        )

        if username not in self.__users:
            self.__users.append(username)

        # remove offline users
        if len(self.__tmp_users) >= self.__tmp_total_users:
            for _username in [*self.__users]:
                if _username not in self.__tmp_users:
                    self.__users.remove(_username)

    def on_players(self, players: int) -> None:
        print(f"{self.room_id}: {players} players")
        self.__tmp_total_users = players

    def on_skip(self, sender: str) -> None:
        if sender in self.__skips:
            return

        self.__skips.append(sender)
        current_votes = len(self.__skips)
        total = round(len(self.__users) / 2)

        if current_votes >= total or (
            self.bot_mode == 0 and sender == self.__users[0]
        ):
            self.rotate()
            return

        self.irc.send_private(
            self.room_id, f"Skip voting: {current_votes} / {total}"
        )

    def on_message_start(self, message: str) -> None:
        words = message.strip().split()

        if message == "!start":
            self.irc.send_private(self.room_id, "!mp start")
        elif len(words) == 2 and words[1].isdigit():
            self.irc.send_private(self.room_id, f"!mp start {words[1]}")

    def on_message_stop(self) -> None:
        self.irc.send_private(self.room_id, "!mp aborttimer")

    def on_message_users(self) -> None:
        self.irc.send_private(
            self.room_id, f"Users: {', '.join(self.__users)}"
        )

    def on_message_queue(self) -> None:
        self.irc.send_private(self.room_id, f"Queue: {self.get_queue()}")

    def on_message_info(self) -> None:
        self.irc.send_private(
            self.room_id,
            f"Commands: start <seconds>, stop, queue, skip, alt | Nothing to see here...",
        )

    def on_message_alt(self) -> None:
        self.irc.send_private(
            self.room_id,
            f"Alternative Links: {message_beatmap_links('osu.ppy.sh', self.__beatmap)}",
        )

    def on_message_receive(self, sender: str, message: str) -> None:
        """room message"""

        if sender == "BanchoBot":
            """banchobot chats"""
            if message == "Closed the match":
                self.on_match_closed()
            elif "joined in slot" in message:
                username = parse_username(message.split(" joined in slot")[0])
                self.on_user_joined(username)
            elif message.endswith("left the game."):
                username = parse_username(message.split(" left the game.")[0])
                self.on_user_left(username)
            elif message.endswith(" became the host."):
                username = parse_username(
                    message.split(" became the host.")[0]
                )
                self.on_host_changed(username)
            elif message == "The match has started!":
                self.on_match_started()
            elif message == "The match has finished!":
                self.on_match_finished()
            elif message == "All players are ready":
                self.on_match_ready()
            elif message.startswith("Beatmap changed to: "):
                search = re.search(
                    "Beatmap.*?: (.*)? \[(.*?)\] \((.*)?\)", message
                )
                if search:
                    self.on_beatmap_changed_to(
                        version=search.group(2),
                        title=search.group(1),
                        url=search.group(3),
                        beatmap_id=int(search.group(3).split("/")[-1]),
                    )
            elif message.startswith("Changed beatmap to "):
                message_split = message.split(" ")
                url = message_split[3]
                url_split = url.split("/")
                beatmap_id = url_split[-1]
                title = "".join(message_split[4:])
                self.on_changed_beatmap_to(
                    title=title,
                    beatmap_id=int(beatmap_id) if beatmap_id.isdigit() else 0,
                    url=url,
                )
            elif message.startswith("Slot "):
                self.on_slot(**parse_slot(message))
            elif message.startswith("Players: "):
                self.on_players(players=int(message.split(" ")[-1]))
        else:
            """players chat"""
            if message.startswith("!start"):
                self.on_message_start(message)
            elif message == "!stop":
                self.on_message_stop()
            elif message == "!users":
                self.on_message_users()
            elif message == "!skip":
                self.on_skip(sender=sender)
            elif message == "!queue":
                self.on_message_queue()
            elif message == "!info":
                self.on_message_info()
            elif message == "!alt":
                self.on_message_alt()


@dataclass
class RoomBot:
    irc: OsuIrc
    rooms: list[Room] = field(default_factory=list)

    def get_room(self, name: str = "", room_id: str = "") -> Optional[Room]:
        for _room in self.rooms:
            if name == _room.name or room_id == _room.room_id:
                return _room
        return None

    def add_room(self, room: Room) -> Optional[Room]:
        for _room in self.rooms:
            if _room.name == room.name:
                return None

        self.rooms.append(room)
        return room

    def remove_room(self, room: Room) -> bool:
        if room in self.rooms:
            self.rooms.remove(room)
            return True
        return False

    def disconnect_rooms(self) -> None:
        for _room in self.rooms:
            _room.disconnect()

    def check_rooms(self) -> None:
        for _room in self.rooms:
            _room.check_room()

    def on_match_created(self, message: str) -> None:
        id_name = re.search("https://osu.ppy.sh/mp/(\d*)? (.*)", message)

        if id_name:
            name, room_id = id_name.group(2), id_name.group(1)
            room = self.get_room(name=name)

            if room:
                room.on_match_created(room_id=f"#mp_{room_id}")

    def on_message_receive(self, message: Optional[str | int | bool]) -> None:
        self.check_rooms()

        if isinstance(message, str):
            message_dict = parse_message(message=message)

            if not message_dict:
                return

            channel = message_dict.get("channel", "")
            cmd_str = message_dict.get("command", "")
            sender = message_dict.get("sender", "")
            message = message_dict.get("message", "")

            if cmd_str != "QUIT":
                print(message)
            elif channel == self.irc.username:
                """PRIVATE MESSAGE"""
                if sender == "BanchoBot":
                    if message.startswith("Created the tournament match"):
                        self.on_match_created(message)
            elif channel.startswith("#mp_"):
                """ROOM MESSAGE"""
                room = self.get_room(room_id=channel)

                if isinstance(room, Room):
                    room.on_message_receive(sender, message)
        elif message == -1:
            self.disconnect_rooms()
        elif message == -2:
            print("Reconnecting...")

    def start(self) -> None:
        """start receiving messages"""
        print("starting")

        for message in self.irc.message_generator():
            self.on_message_receive(message)
