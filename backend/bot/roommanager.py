from __future__ import annotations
import re
import threading

from my_logger import logger
from typing import Optional
from dataclasses import dataclass, field
from bot.parsers import parse_message

from bot.enums import MESSAGE_YIELD, RoomData
from bot.room import Room
from bot.irc import OsuIrc


@dataclass
class RoomManager:
    irc: OsuIrc
    rooms: list[Room] = field(default_factory=list)

    def get_rooms_json(self) -> list[RoomData]:
        return [room.get_json() for room in self.rooms]

    def get_room(self, unique_id: str = "", room_id: str = "") -> Optional[Room]:
        for room in self.rooms:
            if (unique_id and unique_id == room.unique_id) or (room_id and room_id == room.room_id):
                return room
        return None

    def add_room(self, room: Room) -> Room:
        self.rooms.append(room)
        return room

    def remove_room(self, room: Room) -> bool:
        try:
            self.rooms.remove(room)
            return True
        except ValueError:
            return False

    def disconnect_rooms(self) -> None:
        for room in self.rooms:
            room.disconnect()

    def on_match_created(self, message: str) -> None:
        match_info = re.search(r"https://osu.ppy.sh/mp/(\d*)? (.*)", message)

        if not match_info:
            return

        room_id, name = match_info.groups()
        room = self.get_room(unique_id=name)

        if room:
            room.on_match_created(room_id=f"#mp_{room_id}")
            room.connect()

    def on_message_receive(self, message: Optional[str | MESSAGE_YIELD]) -> None:
        if isinstance(message, str):
            message_dict = parse_message(message=message)

            if not message_dict:
                return

            if message_dict.get("command") != "QUIT":
                logger.debug(message_dict)

            channel = message_dict.get("channel", "")
            cmd_str = message_dict.get("command", "")
            sender = message_dict.get("sender", "")
            message = message_dict.get("message", "")

            if cmd_str == "QUIT":
                return

            if channel == self.irc.username and sender == "BanchoBot":
                if message.startswith("Created the tournament match"):
                    self.on_match_created(message)
            elif channel.startswith("#mp_"):
                room = self.get_room(room_id=channel)

                if isinstance(room, Room):
                    room.on_message_receive(sender, message)
            elif channel == self.irc.username and message.startswith("#mp_"):
                room = self.get_room(room_id=message.split(" ")[0])

                if not isinstance(room, Room):
                    return

                if cmd_str == "403":
                    room.restart()
                elif cmd_str == "332":
                    room.connect()

            return

        match message:
            case MESSAGE_YIELD.DISCONNECT:
                logger.error("Connection has been lost")
                self.disconnect_rooms()
            case MESSAGE_YIELD.RECONECTION_FAILED:
                logger.error("Reconnection failed")
            case MESSAGE_YIELD.RECONNECTED:
                logger.info("Connection has been reestablished")
                self.join_rooms()

    def create_rooms(self) -> None:
        for room in self.rooms:
            if room._closed:
                room.create()

    def join_rooms(self) -> None:
        for room in self.rooms:
            room.join()

    def run_message_listener(self) -> None:
        for message in self.irc.message_generator():
            self.on_message_receive(message)

    def start(self, run_on_thread: bool = False) -> Optional[threading.Thread]:
        self.irc.start()

        if run_on_thread:
            thread = threading.Thread(target=self.run_message_listener)
            thread.start()
            return thread

        self.run_message_listener()
        return None
