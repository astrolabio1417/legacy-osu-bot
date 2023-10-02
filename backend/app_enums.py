from typing import TypedDict


class BotEnums(TypedDict):
    BOT_MODE: list[str]
    TEAM_MODE: list[str]
    PLAY_MODE: list[str]
    SCORE_MODE: list[str]
    RANK_STATUS: list[str]
    BEATMAP_GENRE: list[str]
    BEATMAP_LANGUAGE: list[str]


class Session(TypedDict):
    username: str
    is_admin: bool
    is_irc_running: bool


class MessageResponse(TypedDict):
    message: str


class LoginResponse(MessageResponse, Session):
    pass
