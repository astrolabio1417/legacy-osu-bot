import re
from collections import deque
import uuid
from typing import Any
from dataclasses import dataclass, field
from bot.parsers import (
    get_beatmap_id_from_url,
    parse_slot,
    normalize_username,
)
from bot.beatmap import RoomBeatmap
from bot.counter import Counter
from bot.enums import BOT_MODE, PLAY_MODE, TEAM_MODE, SCORE_MODE, RoomData
from bot.osuapi import osu_api
from bot.irc import OsuIrc


class Users(deque[Any]):
    def append(self, __x: Any) -> None:
        if __x not in self:
            return super().append(__x)

    def remove(self, __value: Any) -> None:
        if __value in self:
            return super().remove(__value)


@dataclass
class Room:
    irc: OsuIrc
    beatmap: RoomBeatmap
    name: str
    password: str = ""

    bot_mode: BOT_MODE = BOT_MODE.AUTO_HOST
    play_mode: PLAY_MODE = PLAY_MODE.OSU
    team_mode: TEAM_MODE = TEAM_MODE.HEAD_TO_HEAD
    score_mode: SCORE_MODE = SCORE_MODE.SCORE
    room_size: int = 16

    room_id: str = ""
    unique_id: str = ""

    _closed: bool = False
    users: Users = field(default_factory=Users)
    skip_votes: set[str] = field(default_factory=set)
    abort_votes: set[str] = field(default_factory=set)
    tmp_users: set[str] = field(default_factory=set)
    _tmp_total_users: int = 0
    countdown_message_seconds = [3, 10, 30, 60, 90, 120, 150, 180]

    _counter: Counter = field(default_factory=Counter)

    is_connected = False
    is_created = False
    is_configured = False

    def __post_init__(self) -> None:
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())

        self._counter = Counter()
        self._counter.on_count = self.on_count
        self._counter.on_finished = self.on_count_finished

        room_modes = [
            ("Bot mode", self.bot_mode, BOT_MODE),
            ("Play mode", self.play_mode, PLAY_MODE),
            ("Team mode", self.team_mode, TEAM_MODE),
            ("Score mode", self.score_mode, SCORE_MODE),
        ]

        for name, selected, selection in room_modes:
            if selected not in selection:
                raise ValueError(f"{name} is invalid.")

    def get_json(self) -> RoomData:
        return {
            "id": self.unique_id,
            "name": self.name,
            "room_id": self.room_id,
            "bot_mode": self.bot_mode.name,
            "play_mode": self.play_mode.name,
            "team_mode": self.team_mode.name,
            "score_mode": self.score_mode.name,
            "room_size": self.room_size,
            "is_connected": self.is_connected,
            "is_created": self.is_created,
            "is_configured": self.is_configured,
            "users": list(self.users),
            "skips": list(self.skip_votes),
            "beatmap": self.beatmap.get_json(),
        }

    def on_count(self, count: int) -> None:
        if count in self.countdown_message_seconds:
            self.send_start_message(count)

    def on_count_finished(self) -> None:
        if self.users:
            self.send_message("!mp start")

    def configure(self, **kwargs: Any) -> None:
        beatmap = kwargs.pop("beatmap", {})
        self.password = kwargs.get("password", "")

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.beatmap.configure(**beatmap)
        self.is_configured = False
        self.__post_init__()
        self.on_match_created(self.room_id)

    def restart(self) -> None:
        self.on_closed()
        self.create()

    def connect(self) -> None:
        self.is_connected = True

    def disconnect(self) -> None:
        self.is_connected = False

    def create(self) -> bool:
        if not self.is_created:
            self.irc.send_private_message("BanchoBot", f"mp make {self.unique_id}")
            self.is_created = True

        return self.is_created

    def join(self, room_id: str | None = None) -> bool:
        if not self.room_id and not room_id:
            return False

        if room_id:
            self.room_id = room_id

        self.irc.send(f"JOIN {self.room_id}")
        return self.is_connected

    def send_close(self) -> None:
        self.send_message("!mp close")

    def on_closed(self) -> None:
        self.tmp_users.clear()
        self._counter.stop()
        self._tmp_total_users = 0
        self.room_id = ""
        self.users.clear()
        self.clear_skip_votes()
        self.clear_abort_votes()
        self.disconnect()
        self.is_created = False
        self.is_configured = False

    def on_match_created(self, room_id: str) -> None:
        self.room_id = room_id
        self.setup()

    def setup(self) -> None:
        if self.is_configured:
            return

        messages = [
            f"!mp name {self.name}",
            f"!mp password {self.password}",
            f"!mp set {self.team_mode.value} {self.score_mode.value} {self.room_size}",
            "!mp mods Freemod",
        ]

        self.send_messages(messages)
        self.set_current_beatmap(self.beatmap.current.id)
        self.is_configured = True

    def send_messages(self, messages: list[str]) -> None:
        for message in messages:
            self.send_message(message)

    def send_message(self, message: str) -> None:
        self.irc.send_private_message(self.room_id, message)

    def rotate(self) -> None:
        if self.bot_mode == BOT_MODE.AUTO_HOST:
            self.rotate_host()
        elif self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
            self.rotate_beatmap()

        self.skip_votes.clear()

    def rotate_host(self) -> None:
        if not self.users:
            return

        host = self.users.popleft()
        self.users.append(host)
        self.send_message(f"!mp host {self.users[0]}")

    def rotate_beatmap(self) -> None:
        self.beatmap.rotate()
        self.set_current_beatmap(self.beatmap.current.id)

    def set_current_beatmap(self, beatmap_id: int) -> None:
        message = f"!mp map {beatmap_id} {self.play_mode.value}"
        self.send_message(message)

    def add_user(self, username: str) -> None:
        normalized_username = normalize_username(username)
        self.users.append(normalized_username)

    def remove_user(self, username: str) -> None:
        self.users.remove(username)
        self.skip_votes.discard(username)
        self.abort_votes.discard(username)

    def on_host_changed(self, host: str) -> None:
        self.clear_skip_votes()
        self.clear_abort_votes()

        is_auto_host = self.bot_mode == BOT_MODE.AUTO_HOST

        if is_auto_host and not self.is_username_host(host):
            self.rotate_host()

    def is_username_host(self, target_username: str) -> bool:
        return not self.users or self.users[0] == target_username

    def on_match_started(self) -> None:
        self.stop_counter()
        self.clear_skip_votes()
        self.clear_abort_votes()

        if self.bot_mode == BOT_MODE.AUTO_HOST:
            self.rotate_host()

        if not self.users:
            self.send_message("!mp abort")

    def clear_skip_votes(self) -> None:
        self.skip_votes.clear()

    def clear_abort_votes(self) -> None:
        self.abort_votes.clear()

    def stop_counter(self) -> None:
        self._counter.stop()

    def get_queue(self) -> str:
        modes = {
            BOT_MODE.AUTO_HOST: ", ".join(list(self.users)),
            BOT_MODE.AUTO_ROTATE_MAP: self.beatmap.get_queue(),
        }

        return modes.get(self.bot_mode, "")

    def on_match_finished(self) -> None:
        queue = self.get_queue()
        message = f"!mp settings | Queue: {queue}"
        self.send_message(message)

        if self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
            self.rotate_beatmap()

    def on_match_ready(self) -> None:
        self.send_message("!mp start")

    def on_beatmap_changed_to(
        self,
        title: str,
        version: str,
        url: str,
        beatmap_id: int,
    ) -> None:
        if beatmap_id == self.beatmap.current.id:
            return

        beatmap_id = beatmap_id or self.beatmap.current.id
        message = f"!mp map {beatmap_id} {self.play_mode.value}"
        self.send_message(message)

    def on_changed_beatmap_to(self, title: str, url: str, beatmap_id: int) -> None:
        self.clear_skip_votes()
        self.clear_abort_votes()

        if self.bot_mode == BOT_MODE.AUTO_ROTATE_MAP:
            self.send_beatmap_alt()
            return

        if beatmap_id == self.beatmap.current.id:
            return

        beatmap = osu_api.beatmap(beatmap_id)

        if not beatmap:
            message = f"!mp map {self.beatmap.current.id} {self.play_mode.value} | Failed to find beatmap!"
            self.send_message(message)
            return

        # TODO bypas for now, ossapi wrapper can't fetch the full data of beatmapset using beatmap.beatmapset
        beatmapset = osu_api.beatmapset(beatmap.beatmapset_id)
        errors: list[str] = []

        beatmapset_errors = self.beatmap.get_beatmapset_errors(beatmapset)
        beatmap_errors = self.beatmap.get_beatmap_errors(beatmap)

        errors.extend(beatmapset_errors)
        errors.extend(beatmap_errors)

        if errors:
            message = f"!mp map {self.beatmap.current.id} {self.play_mode.value} | Violations: {', '.join(errors[0:2])}"
            self.send_message(message)
            return

        self.beatmap.set_current(beatmap)
        self.send_beatmap_alt()

    def on_slot(self, slot: int, status: str, user_id: str, username: str, roles: list[str]) -> None:
        self.tmp_users.add(username)
        self.users.append(username)

        if not len(self.tmp_users) >= self._tmp_total_users:
            return

        for _username in [*self.users]:
            if _username not in self.tmp_users:
                self.users.remove(_username)

    def on_players(self, players: int) -> None:
        self._tmp_total_users = players

    def on_skip(self, sender: str) -> None:
        self.skip_votes.add(sender)
        current_votes = len(self.skip_votes)
        half_total = round(len(self.users) / 2)

        auto_host_skip = self.bot_mode == BOT_MODE.AUTO_HOST and sender == self.users[0]
        enough_votes = current_votes >= half_total

        if enough_votes or (auto_host_skip):
            self.rotate()
            return

        self.send_message(f"Skip voting: {current_votes} / {half_total}")

    def on_abort(self, sender: str) -> None:
        self.abort_votes.add(sender)
        current_votes = len(self.abort_votes)
        half_total = round(current_votes / 2)

        if current_votes >= half_total:
            self.send_message("!mp abort")
            return

        self.send_message(f"Abort voting: {current_votes} / {half_total}")

    def on_message_start(self, message: str) -> None:
        words = message.strip().split()
        count = 3

        if len(words) == 2 and words[1].isdigit():
            count = int(words[1])

        self._counter.start(count)
        self.send_start_message(count)

    def send_start_message(self, seconds: int) -> None:
        self.send_message(f"Match starts in {seconds} seconds")

    def on_message_stop(self) -> None:
        self._counter.stop()
        self.send_message("Countdown aborted")

    def send_users(self) -> None:
        message = f"Users: {', '.join(self.users)}"
        self.send_message(message)

    def send_queue(self) -> None:
        message = f"Queue: {self.get_queue() or 'No Queue'}"
        self.send_message(message)

    def send_commands(self) -> None:
        message = f"Commands: !start <seconds>, !stop, !queue, !skip, !alt, !abort"
        self.send_message(message)

    def send_beatmap_alt(self) -> None:
        self.send_message(f"Links: {self.beatmap.links}")

    def on_message_receive(self, sender: str, message: str) -> None:
        if sender != "BanchoBot":
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
                case "!abort":
                    self.on_abort(sender=sender)

            return

        if message == "Closed the match":
            self.on_closed()
        elif "joined in slot" in message:
            username = normalize_username(message.split(" joined in slot")[0])
            self.add_user(username)

            # autohost | set first user as host
            if self.bot_mode == BOT_MODE.AUTO_HOST and len(self.users) == 1:
                self.rotate_host()
        elif message.endswith("left the game."):
            username = normalize_username(message.split(" left the game.")[0])

            # autohost | rotate on host leave
            if self.bot_mode == BOT_MODE.AUTO_HOST and self.users and self.users[0] == username:
                self.rotate_host()

            self.remove_user(username)
        elif message.endswith(" became the host."):
            username = normalize_username(message.split(" became the host.")[0])
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
            title = "".join(message_split[4:])

            self.on_changed_beatmap_to(
                title=title,
                beatmap_id=get_beatmap_id_from_url(url),
                url=url,
            )
        elif message.startswith("Slot "):
            self.on_slot(**parse_slot(message))
        elif message.startswith("Players: "):
            self.on_players(players=int(message.split(" ")[-1]))
