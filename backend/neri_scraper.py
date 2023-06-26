import json
import requests
from base64 import b64encode
from dataclasses import dataclass
from bot_typing import BeatmapSetDict
from typing import Optional, TypedDict


@dataclass
class NeriSetting:
    """
    m: 0 | 1 | 2 | 3 | all | o | t | c | m | std | taiko | ctb | mania | osu | osu! | standard | osu!taiko | catch | osu!catch | osu!mania
    s: ranked | qualified | loved | pending | wip | graveyard | unranked | -2 | -1 | 0 | 1 | 2 | 3 | 4
    sort: ranked_asc | ranked_date | favourites_asc | favourite_count | plays_asc | play_count | updated_asc | last_updated | title_asc | title | artist_asc | artist | ranked_desc | favourites_desc | plays_desc | updated_desc | title_desc | artist_desc | default
    """

    m: int | str = "all"
    q: Optional[str] = None
    s: str = "ranked,qualified,loved"
    sort: str = "plays_desc"
    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)


class NeriBeatmap(TypedDict):
    id: int
    beatmapset_id: int
    mode: str
    mode_int: int
    status: str
    ranked: int
    total_length: int
    difficulty_rating: float
    version: str
    accuracy: int
    ar: float
    cs: float
    drain: int
    bpm: int
    convert: bool
    playcount: int


class NeriBeatmapset(TypedDict):
    id: int
    artist: str
    creator: str
    favourite_count: int
    play_count: int
    source: str
    status: str
    title: str
    bpm: int
    ranked: int
    genre: dict[str, str]
    language: dict[str, str]
    beatmaps: list[NeriBeatmap]


API = "https://api.nerinyan.moe"


client = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://nerinyan.moe",
    "Referer": "https://nerinyan.moe/",
}


def search(b64: str = "", page: int = 1, page_size: int = 50) -> list[BeatmapSetDict]:
    if not b64:
        raise KeyError("b64 is required!")

    print(f"{API}/search?b64={b64}&p={page}&ps={page_size}")
    res = client.get(
        f"{API}/search?b64={b64}&p={page}&ps={page_size}",
        headers=headers,
    )
    data: list[BeatmapSetDict] = res.json()

    return data


def neri_search(
    page: int = 1, page_size: int = 1000, settings: NeriSetting = NeriSetting()
) -> list[BeatmapSetDict]:
    query = {
        "extra": "",
        "ranked": settings.s or "",
        "nsfw": True,
        "option": "",
        "m": settings.m or "",
        "totalLength": {"min": settings.length[0] or 0, "max": settings.length[1] or 0},
        "maxCombo": {"min": 0, "max": 0},
        "difficultyRating": {
            "min": settings.star[0] or 0,
            "max": settings.star[1] or 0,
        },
        "accuracy": {"min": 0, "max": 0},
        "ar": {"min": settings.ar[0] or 0, "max": settings.ar[1] or 0},
        "cs": {"min": settings.cs[0] or 0, "max": settings.cs[1] or 0},
        "drain": {"min": 0, "max": 0},
        "bpm": {"min": settings.bpm[0] or 0, "max": settings.bpm[1] or 0},
        "sort": settings.sort or "plays_desc",
        "page": 0,
        "query": "",
    }

    data = search(
        b64encode(json.dumps(query).encode()).decode(),
        page_size=page_size,
        page=page,
    )
    return [remove_unusable_keys_from_bmset(beatmapset) for beatmapset in data]


def fetcher_loop(
    page: int = 1, end_page: int = 1, page_size: int = 1000
) -> list[BeatmapSetDict]:
    beatmapsets = []
    errors = 0

    while page <= end_page:
        print("page: ", page)

        try:
            data = search(
                "eyJleHRyYSI6IiIsInJhbmtlZCI6InJhbmtlZCxxdWFsaWZpZWQsbG92ZWQiLCJuc2Z3Ijp0cnVlLCJvcHRpb24iOiIiLCJtIjoiIiwidG90YWxMZW5ndGgiOnsibWluIjowLCJtYXgiOjB9LCJtYXhDb21ibyI6eyJtaW4iOjAsIm1heCI6MH0sImRpZmZpY3VsdHlSYXRpbmciOnsibWluIjowLCJtYXgiOjB9LCJhY2N1cmFjeSI6eyJtaW4iOjAsIm1heCI6MH0sImFyIjp7Im1pbiI6MCwibWF4IjowfSwiY3MiOnsibWluIjowLCJtYXgiOjB9LCJkcmFpbiI6eyJtaW4iOjAsIm1heCI6MH0sImJwbSI6eyJtaW4iOjAsIm1heCI6MH0sInNvcnQiOiJwbGF5c19kZXNjIiwicGFnZSI6MCwicXVlcnkiOiIifQ==",
                page_size=page_size,
                page=page,
            )

            if not data or len(data) == 0:
                print("Stopping the loop. No list on page:", page)
                break

            [remove_unusable_keys_from_bmset(beatmapset) for beatmapset in data]

            beatmapsets.extend(data)

            with open("neri-datasets-popular.json", "w") as f:
                f.write(json.dumps(beatmapsets))

            print("file updated total", len(beatmapsets))
            errors = 0
            page += 1
        except Exception as err:
            print(
                "catch error: ",
                err,
            )

            if errors >= 5:
                print("Stopping the loop. Max error exceed in page: ", page)
                break

            errors += 1

    return beatmapsets


def remove_unusable_keys_from_bmset(beatmapset: BeatmapSetDict) -> BeatmapSetDict:
    unusable_beatmapset_keys = [
        "description",
        "hype",
        "title_unicode",
        "user_id",
        "video",
        "can_be_hyped",
        "discussion",
        "legacy_thread_url",
        "nominations_summary",
        "ranked_date",
        "storyboard",
        "submitted_date",
        "has_favourited",
        "cache",
        "availability",
        "artist_unicode",
        "nsfw",
        "is_scoreable",
        "deleted_at",
        "tags",
        "ratings_string",
        "last_updated",
    ]

    unusable_beatmap_keys = [
        "is_scoreable",
        "last_updated",
        "deleted_at",
        "checksum",
        "user_id",
        "osu_file",
        "max_combo",
        "count_circles",
        "count_sliders",
        "count_spinners",
        "hit_length",
        "passcount",
    ]

    for i in unusable_beatmapset_keys:
        if i in beatmapset:
            beatmapset.pop(i)  # type: ignore

        for beatmap in beatmapset["beatmaps"]:
            for bk in unusable_beatmap_keys:
                if bk in beatmap:
                    del beatmap[bk]  # type: ignore

    return beatmapset


if __name__ == "__main__":
    data = neri_search(page_size=50)
