from dataclasses import dataclass, field
import json
import re
from typing import Any, Optional, TypedDict
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


@dataclass
class ChimuSearchDict:
    status: Optional[
        int
    ] = 1  # 1 ranked, 2 approved, 3 qualified, 4 loved, 0 pending, -1 wip, -2 graveyard
    mode: Optional[int] = 0  # 0 standard, 1 taiko, 2 CtB, 3 mania
    genre: Optional[
        int
    ] = None  # 2 game, 3 anime, 4 rock, 5 pop, 6 other, 7 novelty, 9 hiphop, 10 electronic
    language: Optional[
        int
    ] = None  # 2 english, 3 japanese, 4 chinese, 5 instrument, 6 korean, 7 french, 8 german, 9 swedish, 10 spanish, 11 italian
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_bpm: Optional[int] = None
    max_bpm: Optional[int] = None
    min_ar: Optional[float] = None
    max_ar: Optional[float] = None
    min_diff: Optional[float] = None
    max_diff: Optional[float] = None
    min_hp: Optional[float] = None
    max_hp: Optional[float] = None
    min_cs: Optional[float] = None
    max_cs: Optional[float] = None
    min_od: Optional[float] = None
    max_od: Optional[float] = None

    def get_dict(self) -> dict[str, Any]:
        _dict = {}
        for key in self.__dict__:
            if self.__dict__[key] != None:
                _dict[key] = self.__dict__[key]
        return _dict


def chimu_search(
    settings: ChimuSearchDict,
    offset: tuple[int, int] = (0, 100000000),
    filename: str = "",
) -> None:
    beatmaps = []
    new_settings = settings.get_dict()
    print(new_settings)
    max_retry = 10
    retry = 0

    while True:
        print(f"OFFSET {offset[0]}/{offset[1]}")

        try:
            response = requests.get(
                "https://api.chimu.moe/v1/search",
                params={**new_settings, "offset": offset[0]},
            )
        except:
            print(f"request error {offset[0]}")
            continue

        if not response.ok:
            print(f"bad response {offset[0]}")
            if retry >= max_retry:
                return
            retry += 1
            continue

        try:
            json_response = json.loads(response.text)
        except json.JSONDecodeError:
            print(f"json loads error! {offset[0]}")
            continue

        if not json_response.get("data"):
            print(json_response)
            print(f"No Data Found on Offset {offset}")
            return

        if type(json_response.get("data")) == list:
            beatmaps += json_response.get("data")
            offset = (len(beatmaps), offset[1])

            with open(f"files/{filename}.json", "w") as f:
                f.write(json.dumps(beatmaps))

            retry = 0
            
            if offset[0] >= offset[1]:
                print(f"Finished. Total {len(beatmaps)}")
                return
        else:
            print("request response is invalid or not a list")


def chimu_test() -> None:
    settings = ChimuSearchDict(mode=0, status=1, language=3)
    chimu_search(
        settings=settings,
        filename="std-06-17-23-1v-jp",
    )


def chimu_beatmapset_parser(beatmapsets: list[Any]) -> list[Any]:
    beatmaps = []

    for beatmapset in beatmapsets:
        for difficulty in beatmapset.get("ChildrenBeatmaps"):
            beatmaps.append(
                {
                    "title": beatmapset.get("Title"),
                    "difficulty_name": difficulty.get("DiffName"),
                    "beatmap_status": beatmapset.get("RankedStatus"),
                    "beatmapset": beatmapset.get("SetId"),
                    "beatmap_id": difficulty.get("BeatmapId"),
                    "gamemode": difficulty.get("Mode"),
                    "difficulty_ar": difficulty.get("AR"),
                    "difficulty_hp": difficulty.get("HP"),
                    "bpm": difficulty.get("BPM"),
                    "play_length": difficulty.get("TotalLength"),
                    "difficulty_od": difficulty.get("OD"),
                    "favorites": beatmapset.get("Favourites"),
                    "difficulty": difficulty.get("DifficultyRating"),
                    "difficulty_cs": difficulty.get("CS"),
                    "pass_count": difficulty.get("Passcount"),
                    "language": beatmapset.get("Language"),
                    "genre": beatmapset.get("Genre"),
                    "total_length": difficulty.get("TotalLength"),
                    "play_count": difficulty.get("Playcount"),
                    "artist": beatmapset.get("Artist"),
                    "creator": beatmapset.get("Creator"),
                }
            )

    return beatmaps


if __name__ == "__main__":
    # chimu_test()
    pass
