from typing import Optional, TypedDict

from bot_enums import CHIMU_GENRE, CHIMU_LANGUAGE, RANK_STATUS


class BeatmapAvailability(TypedDict):
    download_disabled: bool


class NamedDict(TypedDict):
    id: int
    name: str


class BeatmapDict(TypedDict):
    id: int
    difficulty_rating: float
    accuracy: float
    ar: float
    beatmapset_id: int
    bpm: int
    cs: int
    drain: int
    hit_length: int
    mode: str
    mode_int: int
    play_count: int
    ranked: int
    status: str
    total_length: int
    url: str
    title: Optional[str]
    difficulty_title: Optional[str]


class BeatmapSetDict(TypedDict):
    id: int
    title: str
    creator: str
    artist: str
    is_scoreable: int
    availability: BeatmapAvailability
    beatmaps: list[BeatmapDict]
    bpm: int
    favourite_count: int
    genre: NamedDict
    language: NamedDict
    play_count: int
    ranked: int
    ratings: list[int]


class ChimuItemChildren(TypedDict):
    BeatmapId: int
    ParentSetId: int
    DiffName: str
    FileMD5: str
    Mode: int
    BPM: int
    AR: int
    OD: int
    CS: int
    HP: int
    TotalLength: int
    HitLength: int
    Playcount: int
    Passcount: int
    MaxCombo: int
    DifficultyRating: float
    OsuFile: str
    DownloadPath: str


class ChimuItemDict(TypedDict):
    SetId: int
    ChildrenBeatmaps: list[ChimuItemChildren]
    RankedStatus: RANK_STATUS
    ApprovedDate: str
    LastUpdate: str
    LastChecked: str
    Artist: str
    Title: str
    Creator: str
    Source: str
    Tags: str
    HasVideo: bool
    Genre: CHIMU_GENRE
    Language: CHIMU_LANGUAGE
    Favourites: int
    Disabled: bool
