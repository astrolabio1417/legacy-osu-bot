from __future__ import annotations
import re
import uuid
from typing import TYPE_CHECKING, Any, Optional
from dataclasses import dataclass, field
from parsers import parse_message, parse_slot, parse_username
from beatmaps import message_beatmap_links, RoomBeatmap
from counter import Counter
from bot_enums import MESSAGE_YIELD, PLAY_MODE, TEAM_MODE, SCORE_MODE, BOT_MODE

if TYPE_CHECKING:
    from irc import OsuIrc


@dataclass
class Room:
    irc: OsuIrc
    beatmap: RoomBeatmap
    name: str
    id: str = ""
    room_id: str = ""
    password: str = ""
    closed: bool = False

    bot_mode: BOT_MODE = BOT_MODE.AUTO_HOST
    play_mode: PLAY_MODE = PLAY_MODE.OSU
    team_mode: TEAM_MODE = TEAM_MODE.HEAD_TO_HEAD
    score_mode: SCORE_MODE = SCORE_MODE.SCORE
    room_size: int = 16

    users: list[str] = field(default_factory=list)
    skips: list[str] = field(default_factory=list)
    tmp_users: list[str] = field(default_factory=list)
    tmp_total_users: int = 0
    show_countdown_message_in_seconds = [3, 10, 30, 60, 90, 120, 150, 180]

    counter: Counter = Counter()

    __connected = False
    __created = False
    __configured = False

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid1())

        self.counter = Counter()
        self.counter.on_count = self.on_count
        self.counter.on_finished = self.on_count_finished

        modes = [
            ("Bot mode", self.bot_mode, BOT_MODE),
            ("Play mode", self.play_mode, PLAY_MODE),
            ("Team mode", self.team_mode, TEAM_MODE),
            ("Score mode", self.score_mode, SCORE_MODE),
        ]
        beatmap_stats = [
            ("star", self.beatmap.star),
            ("approach rate", self.beatmap.ar),
            ("overall difficulty", self.beatmap.od),
            ("circle size", self.beatmap.cs),
        ]

        for name, selected, selection in modes:
            if selected not in selection:
                raise ValueError(f"{name} is invalid.")

        for name, setting in beatmap_stats:
            if setting[0] < 0 or setting[1] > 10:
                raise ValueError(f"{name} is invalid.")

        if self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
            self.beatmap.load_beatmaps(self.play_mode.value)

        if self.bot_mode == BOT_MODE.AUTO_HOST and not self.beatmap.current:
            self.beatmap.init_current(self.play_mode.value)

    def get_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "room_id": self.room_id,
            "is_closed": self.closed,
            "bot_mode": self.bot_mode.name,
            "play_mode": self.play_mode.name,
            "team_mode": self.team_mode.name,
            "score_mode": self.score_mode.name,
            "room_size": self.room_size,
            "is_connected": self.__connected,
            "is_created": self.__created,
            "is_configured": self.__configured,
            "users": self.users,
            "skips": self.skips,
            "beatmap": self.beatmap.get_json(),
        }

    def on_count(self, count: int) -> int:
        print(f"count {count}")

        if count in self.show_countdown_message_in_seconds:
            self.send_start_on(count)

        return count

    def on_count_finished(self) -> bool:
        print("count finished!")

        if self.users:
            self.irc.send_private(self.room_id, "!mp start")

        return True

    def update(
        self,
        name: Optional[str] = None,
        password: Optional[str] = None,
        play_mode: Optional[PLAY_MODE] = None,
        team_mode: Optional[TEAM_MODE] = None,
        score_mode: Optional[SCORE_MODE] = None,
        bot_mode: Optional[BOT_MODE] = None,
        room_size: Optional[int] = None,
        beatmap: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name or self.name
        self.password = password or self.password
        self.play_mode = play_mode or self.play_mode
        self.team_mode = team_mode or self.team_mode
        self.score_mode = score_mode or self.score_mode
        self.room_size = room_size or self.room_size
        self.bot_mode = bot_mode or self.bot_mode

        if beatmap:
            self.beatmap.update(**beatmap)

        self.__configured = False
        self.__post_init__()
        self.on_match_created(self.room_id)

    def setattrs(self, **kwargs: dict[str, Any]) -> None:
        beatmap = kwargs.pop("beatmap", {})

        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError as err:
                print(f"There are no {k} attribute on Room. Error: ", err)
                pass

        self.beatmap.setattrs(**beatmap)

        self.__configured = False
        self.__post_init__()
        self.on_match_created(self.room_id)

    def restart(self) -> None:
        self.room_id = ""
        self.users = []
        self.skips = []
        self.__connected = False
        self.__created = False
        self.__configured = False
        self.create()

    def disconnect(self) -> None:
        """disconnection of irc socket"""
        self.__connected = False

    def create(self) -> bool:
        if not self.__created:
            self.irc.send_private("BanchoBot", f"mp make {self.id}")
            self.__created = True
            self.closed = False

        return self.__created

    def join(self, room_id: str | None = None) -> bool:
        if not self.room_id and not room_id:
            return False

        if room_id:
            self.room_id = room_id

        self.irc.send(f"JOIN {self.room_id}")
        self.__connected = True
        return self.__connected

    def on_match_created(self, room_id: str) -> None:
        self.room_id = room_id
        print(f"Room Created {self.room_id} {self.name}")
        self.irc.send_private(self.room_id, f"JOIN {self.room_id}")
        self.__connected = True
        self.setup()
        self.rotate()

        if self.bot_mode == BOT_MODE.AUTO_HOST and self.beatmap.current:
            self.rotate_beatmap()

    def send_close(self) -> None:
        self.irc.send_private(self.room_id, "!mp close")

    def close(self) -> None:
        print(f"Close the match {self.name} {self.room_id}")
        self.closed = True
        self.__created = False
        self.__configured = False
        self.room_id = ""

    def setup(self) -> None:
        print(f"Setup {self.room_id} {self.name}")

        if self.__configured:
            return

        messages = [
            f"!mp name {self.name}",
            f"!mp password {self.password}",
            f"!mp set {self.team_mode.value} {self.score_mode.value} {self.room_size}",
            "!mp mods Freemod",
        ]

        for message in messages:
            self.irc.send_private(self.room_id, message)

        self.__configured = True

    def rotate(self) -> None:
        if self.bot_mode == BOT_MODE.AUTO_HOST:
            self.rotate_host()
        elif self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
            self.rotate_beatmap()
        self.skips = []

    def rotate_host(self) -> None:
        if self.users:
            self.users = self.users[1:] + self.users[0:1]
            self.irc.send_private(self.room_id, f"!mp host {self.users[0]}")

    def rotate_beatmap(self) -> None:
        if not self.beatmap.lists:
            return

        self.set_map(self.beatmap.get_first().get("id", 0))
        self.beatmap.rotate()

    def set_map(self, beatmap_id: int) -> None:
        self.irc.send_private(
            self.room_id, f"!mp map {beatmap_id} {self.play_mode.value}"
        )

    def add_user(self, username: str) -> None:
        username = parse_username(username)
        print(f"{self.room_id}: {username} joined the room.")

        if username not in self.users:
            self.users.append(username)
            print(f"{self.room_id}: {username} has been added")

    def remove_user(self, username: str) -> None:
        print(f"{self.room_id}: {username} left the room.")

        if username in self.users:
            self.users.remove(username)

    def on_host_changed(self, username: str) -> None:
        print(f"{self.room_id}: changed host to {username}")
        self.skips = []

        # auto host | enforce user queue
        if self.bot_mode == BOT_MODE.AUTO_HOST and not self.is_username_host(username):
            self.rotate_host()

    def is_username_host(self, username: str) -> bool:
        return not self.users or self.users[0] == username

    def on_match_started(self) -> None:
        print(f"{self.room_id}: Match started")
        self.counter.stop()
        self.skips = []

        if self.bot_mode == BOT_MODE.AUTO_HOST:
            self.rotate_host()

    def get_queue(self) -> str:
        if self.bot_mode == BOT_MODE.AUTO_HOST:
            return ", ".join(self.users[0:5])
        elif self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP and self.beatmap.lists:
            return self.beatmap.get_queue()

        return "no_queue"

    def on_match_finished(self) -> None:
        print(f"{self.room_id}: Match finished")
        self.irc.send_private(
            self.room_id,
            f"!mp settings | Queue: {self.get_queue()}",
        )

        # auto rotate map
        if self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
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
        print(f"{self.room_id}: Beatmap change to {title} {url} {beatmap_id}")

        if beatmap_id == self.beatmap.current:
            return

        self.irc.send_private(
            self.room_id,
            f"!mp map {beatmap_id if beatmap_id else self.beatmap.current} {self.play_mode.value}",
        )

    def on_changed_beatmap_to(self, title: str, url: str, beatmap_id: int) -> None:
        print(f"{self.room_id}: Change beatmap to {title} {url}")

        if beatmap_id == self.beatmap.current:
            return

        self.skips = []

        print(f"~ CURRENT BEATMAP ", self.beatmap.current)
        bm = self.beatmap.get_beatmap(url, beatmap_id)

        if not bm:
            # no beatmap found
            self.irc.send_private(self.room_id, "Beatmap Fetch Error")
            return

        beatmapset, beatmap = bm

        if self.beatmap.force_stat and self.beatmap.current:
            errors = self.beatmap.check_beatmap(beatmap)

            if beatmap.get("mode_int") != self.play_mode.value:
                errors.append(("Play Mode"))

            if errors:
                self.irc.send_private(
                    self.room_id,
                    f"!mp map {self.beatmap.current} {self.play_mode.value} | Rule Violations: {', '.join(errors)}",
                )
                return

        self.beatmap.current = beatmap_id
        beatmapset_id = beatmapset.get("id", 0)
        self.beatmap.current_set = beatmapset.get("id", self.beatmap.current_set)

        if beatmapset_id:
            self.irc.send_private(
                self.room_id,
                f"Alternative Links: {message_beatmap_links(title, beatmapset_id)}",
            )

    def on_slot(
        self,
        slot: int,
        status: str,
        user_id: str,
        username: str,
        roles: list[str],
    ) -> None:
        self.tmp_users.append(username)
        print(
            f"{self.room_id}: {username}[{user_id}] - Slot {slot} | Status {status} | Roles: {roles}"
        )

        if username not in self.users:
            self.users.append(username)

        # remove offline users
        if len(self.tmp_users) >= self.tmp_total_users:
            for _username in [*self.users]:
                if _username not in self.tmp_users:
                    self.users.remove(_username)

    def on_players(self, players: int) -> None:
        print(f"{self.room_id}: {players} players")
        self.tmp_total_users = players

    def on_skip(self, sender: str) -> None:
        if sender in self.skips:
            return

        self.skips.append(sender)
        current_votes = len(self.skips)
        total = round(len(self.users) / 2)

        if current_votes >= total or (
            self.bot_mode == BOT_MODE.AUTO_HOST and sender == self.users[0]
        ):
            self.rotate()
            return

        self.irc.send_private(self.room_id, f"Skip voting: {current_votes} / {total}")

    def on_message_start(self, message: str) -> None:
        words = message.strip().split()

        if message == "!start":
            self.counter.start(3)
            self.send_start_on(3)
        elif len(words) == 2 and words[1].isdigit():
            count = int(words[1])
            self.counter.start(count)
            self.send_start_on(count)

    def send_start_on(self, seconds: int) -> None:
        self.irc.send_private(self.room_id, f"Match starts in {seconds} seconds")

    def on_message_stop(self) -> None:
        self.counter.stop()
        self.irc.send_private(self.room_id, "Countdown aborted")

    def send_users(self) -> None:
        self.irc.send_private(self.room_id, f"Users: {', '.join(self.users)}")

    def send_queue(self) -> None:
        self.irc.send_private(self.room_id, f"Queue: {self.get_queue()}")

    def send_commands(self) -> None:
        self.irc.send_private(
            self.room_id,
            f"Commands: !start <seconds>, !stop, !queue, !skip, !alt",
        )

    def send_beatmap_alt(self) -> None:
        self.irc.send_private(
            self.room_id,
            f"Alternative Links: {message_beatmap_links('osu.ppy.sh', self.beatmap.current_set)}",
        )

    def on_message_receive(self, sender: str, message: str) -> None:
        """room message"""

        if sender != "BanchoBot":
            """players chat"""

            if message.startswith("!start"):
                self.on_message_start(message)
                return

            match message:
                case "!stop":
                    self.on_message_stop()
                case "!users":
                    self.send_users()
                case "!skip":
                    self.on_skip(sender=sender)
                case "!queue":
                    self.send_queue()
                case "!info":
                    self.send_commands()
                case "!alt":
                    self.send_beatmap_alt()

            return

        """banchobot chats"""
        if message == "Closed the match":
            self.close()
        elif "joined in slot" in message:
            username = parse_username(message.split(" joined in slot")[0])
            self.add_user(username)

            # autohost | set first user as host
            if self.bot_mode == BOT_MODE.AUTO_HOST and len(self.users) == 1:
                self.rotate_host()
        elif message.endswith("left the game."):
            username = parse_username(message.split(" left the game.")[0])

            # autohost | rotate on host leave
            if (
                self.bot_mode == BOT_MODE.AUTO_HOST
                and self.users
                and self.users[0] == username
            ):
                self.rotate_host()

            self.remove_user(username)
        elif message.endswith(" became the host."):
            username = parse_username(message.split(" became the host.")[0])
            self.on_host_changed(username)
        elif message == "The match has started!":
            self.on_match_started()
        elif message == "The match has finished!":
            self.on_match_finished()
        elif message == "All players are ready":
            self.on_match_ready()
        elif message.startswith("Beatmap changed to: "):
            search = re.search("Beatmap.*?: (.*)? \[(.*?)\] \((.*)?\)", message)
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


@dataclass
class RoomBot:
    irc: OsuIrc
    rooms: list[Room] = field(default_factory=list)

    def get_rooms_json(self) -> list[dict[str, Any]]:
        return [room.get_json() for room in self.rooms]

    def get_room(self, unique_id: str = "", room_id: str = "") -> Optional[Room]:
        for room in self.rooms:
            if (unique_id and unique_id == room.id) or (
                room_id and room_id == room.room_id
            ):
                return room
        return None

    def add_room(self, room: Room) -> Room:
        self.rooms.append(room)
        return room

    def remove_room(self, room: Room) -> bool:
        if room in self.rooms:
            self.rooms.remove(room)
            return True
        return False

    def disconnect_rooms(self) -> None:
        for room in self.rooms:
            room.disconnect()

    def on_match_created(self, message: str) -> None:
        id_name = re.search("https://osu.ppy.sh/mp/(\d*)? (.*)", message)

        if id_name:
            name, room_id = id_name.group(2), id_name.group(1)
            room = self.get_room(unique_id=name)

            if room:
                room.on_match_created(room_id=f"#mp_{room_id}")

    def on_message_receive(self, message: Optional[str | MESSAGE_YIELD]) -> None:
        if isinstance(message, str):
            message_dict = parse_message(message=message)

            if not message_dict:
                return

            channel = message_dict.get("channel", "")
            cmd_str = message_dict.get("command", "")
            sender = message_dict.get("sender", "")
            message = message_dict.get("message", "")

            if cmd_str == "QUIT":
                return

            print(channel, cmd_str, sender, message)

            is_room_not_created = (
                sender == "cho.ppy.sh"
                and message.startswith("#mp_")
                and "No such channel #mp_" in message
            )

            if is_room_not_created:
                room_id = message.split(" ")[0]
                room = self.get_room(room_id=room_id)

                if room:
                    room.restart()

            if channel == self.irc.username:
                """PRIVATE MESSAGE"""
                if sender == "BanchoBot":
                    if message.startswith("Created the tournament match"):
                        self.on_match_created(message)
            elif channel.startswith("#mp_"):
                """ROOM MESSAGE"""
                room = self.get_room(room_id=channel)

                if isinstance(room, Room):
                    room.on_message_receive(sender, message)

            return

        match message:
            case MESSAGE_YIELD.DISCONNECT:
                self.disconnect_rooms()
            case MESSAGE_YIELD.RECONECTION_FAILED:
                print("Reconnecting...")
            case MESSAGE_YIELD.RECONNECTED:
                self.join_rooms()

    def create_rooms(self) -> None:
        for room in self.rooms:
            room.create()
        return

    def join_rooms(self) -> None:
        for room in self.rooms:
            room.join()
        return

    def start(self) -> None:
        """start receiving messages"""
        print("Starting osu IRC")

        self.irc.start()

        print("Create and Join Rooms")
        self.create_rooms()

        with open("logs/messages1.txt", "w") as f:
            for message in self.irc.message_generator():
                f.write(f"{message}\n")
                self.on_message_receive(message)
