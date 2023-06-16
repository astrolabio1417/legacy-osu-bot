from typing import Literal



TEAM_MODE = {0: "HeadToHead", 1: "TagCoop", 2: "TeamVs", 3: "TagTeamVs"}
TEAM_MODE_T = Literal[0, 1, 2, 3]

SCORE_MODE = {0: "Score", 1: "Accuracy", 2: "Combo", 3: "ScoreV2"}
SCORE_MODE_T = Literal[0, 1, 2, 3]

PLAY_MODE = {0: "osu!", 1: "Taiko", 2: "Catch the Beat", 3: "osu!Mania"}
PLAY_MODE_T = Literal[0, 1, 2, 3]

BOT_MODE = {0: "AutoHost", 1: "AutoRotateMap"}
BOT_MODE_T = Literal[0, 1]

VALID_ROLES = [
    "Host",
    "TeamBlue",
    "TeamRed",
    "Hidden",
    "HardRock",
    "SuddenDeath",
    "Flashlight",
    "SpunOut",
    "NoFail",
    "Easy",
    "Relax",
    "Relax2",
]

MESSAGE_YIELD = {
    'DISCONNECTED': -1,
    'RECONECTION_FAILED': -2,
    'RECONNECTED': -3,
}