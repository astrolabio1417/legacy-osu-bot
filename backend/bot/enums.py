from enum import Enum, IntEnum
from typing import TypedDict
from ossapi.enums import BeatmapsetSearchGenre, BeatmapsetSearchLanguage
from ossapi import Beatmap


class TEAM_MODE(IntEnum):
    HEAD_TO_HEAD = 0
    TAG_COOP = 1
    TEAM_VS = 2
    TAG_VS = 3


class SCORE_MODE(IntEnum):
    SCORE = 0
    ACCURACY = 1
    COMBO = 2
    SCORE_V2 = 3


class PLAY_MODE(IntEnum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


class BOT_MODE(Enum):
    AUTO_HOST = "AutoHost"
    AUTO_ROTATE_MAP = "AutoRotateMap"


class MESSAGE_YIELD(Enum):
    DISCONNECT = "DISCONNECT"
    RECONECTION_FAILED = "RECONECTION_FAILED"
    RECONNECTED = "RECONNECTED"


class RANK_STATUS(IntEnum):
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4
    PENDING = 0
    WIP = -1
    GRAVEYARD = -2


class MessageDict(TypedDict):
    sender: str
    command: str
    channel: str
    message: str


class SlotDict(TypedDict):
    status: str
    slot: int
    user_id: str
    username: str
    roles: list[str]


class UserCredentials(TypedDict):
    username: str
    password: str


class RoomData(TypedDict):
    id: str
    name: str
    room_id: str
    bot_mode: str
    play_mode: str
    team_mode: str
    score_mode: str
    room_size: int
    is_connected: bool
    is_configured: bool
    is_created: bool
    users: list[str]
    skips: list[str]
    beatmap: Beatmap


class RoomBeatmapData(TypedDict):
    play_mode: str  # PLAY_MODE
    star: tuple[float, float]
    ar: tuple[float, float]
    cs: tuple[float, float]
    length: tuple[int, int]
    bpm: tuple[int, int]
    rank_status: list[str]  # list[RANK_STATUS]
    lists: list[Beatmap]
    current: Beatmap
    genre: BeatmapsetSearchGenre
    language: BeatmapsetSearchLanguage
