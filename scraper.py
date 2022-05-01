import json
import re
from typing import Optional, TypedDict
import requests


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


class BeatmapSetResponseDict(TypedDict):
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


def fetch_beatmap(
    url: str,
) -> Optional[BeatmapSetResponseDict]:
    try:
        response = requests.get(url, timeout=(10, 10))
        print(f"~ Fetch status|code: {response.ok} | {response.status_code}")
    except Exception as err:
        print(f"~ Fetch beatmap info error! | {err}")
        return None

    if response and response.ok and response.text:
        beatmap_info_search = re.search('\{"artist".+', response.text)

        if beatmap_info_search:
            beatmap_info = beatmap_info_search.group(0)

            if beatmap_info:
                try:
                    beatmap_info_json: BeatmapSetResponseDict = json.loads(
                        beatmap_info
                    )
                    return beatmap_info_json
                except json.decoder.JSONDecodeError as err:
                    print(f"Beatmap info decode error | {err}")

    print("Beatmap failed to fetch")
    return None


def test_fetch_beatmap() -> None:
    url = "https://osu.ppy.sh/b/1232328"
    print(fetch_beatmap(url))


if __name__ == "__main__":
    test_fetch_beatmap()
