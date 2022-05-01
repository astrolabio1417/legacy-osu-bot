from typing import TypedDict


class RoomBeatmapDict(TypedDict):
    beatmapset: int
    beatmap_id: int
    difficulty_name: str
    beatmap_status: str
    gamemode: int
    title: str
    difficulty_ar: float
    difficulty_hp: float
    bpm: int
    play_length: int
    difficulty_od: float
    favorites: int
    difficulty: float
    difficulty_cs: float
    pass_count: int
    language: str
    total_length: int
    play_count: int


def message_beatmap_links(title: str, beatmap_id: int) -> str:
    return (
        f"[https://osu.ppy.sh/beatmapsets/{beatmap_id} {title}]  [https://beatconnect.io/b/{beatmap_id}/ beatconnect]  [https://chimu.moe/d/{beatmap_id} chimu]"
        if beatmap_id
        else "missing_beatmap_id"
    )
