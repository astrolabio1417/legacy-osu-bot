from __future__ import annotations
import re
import threading

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
            if (unique_id and unique_id == room.unique_id) or (
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
            if room._closed:
                room.create()
        return

    def join_rooms(self) -> None:
        for room in self.rooms:
            room.join()
        return

    def run_message_listener(self) -> None:
        for message in self.irc.message_generator():
            self.on_message_receive(message)

    def start(self, run_on_thread: int = False) -> threading.Thread:
        """start receiving messages"""
        print("Starting osu IRC")

        self.irc.start()

        thread = threading.Thread(target=self.run_message_listener, args=())
        thread.start()

        if not run_on_thread:
            thread.join()

        return thread
