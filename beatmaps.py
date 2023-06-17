from typing import TypedDict
from dataclasses import dataclass, field
from scraper import fetch_beatmap


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


@dataclass
class RoomBeatmap:
    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    od: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)
    current: int = 0
    lists: list[RoomBeatmapDict] = field(default_factory=list)
    asset_filename: str = "chimu-std-ranked-5to7star.json"
    force_stat: bool = False

    def load_beatmaps(self, filename: str, play_mode: int) -> list[RoomBeatmapDict]:
        import json

        with open(f"beatmapsets/{filename}", "r") as f:
            try:
                beatmaplist: list[RoomBeatmapDict] = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return []

            if beatmaplist:
                valid_beatmaps = []

                for beatmap in beatmaplist:
                    if not beatmap.get("beatmap_id", False):
                        print(beatmap.get("beatmap_id"))
                        continue

                    play_mode = beatmap.get("gamemode", -1) == play_mode
                    ar = (
                        beatmap.get("difficulty_ar", 0.00) >= self.ar[0]
                        and beatmap.get("difficulty_ar", 0.00) <= self.ar[1]
                    )
                    star = (
                        beatmap.get("difficulty", 0.00) >= self.star[0]
                        and beatmap.get("difficulty", 0.00) <= self.star[1]
                    )
                    length = (
                        beatmap.get("total_length", 0) >= self.length[0]
                        and beatmap.get("total_length", 0) <= self.length[1]
                    )
                    bpm = beatmap.get("bpm", 0) >= self.bpm[0] and beatmap.get(
                        "bpm", 0
                    ) <= beatmap.get("bpm", 0)

                    if play_mode and ar and star and length and bpm:
                        valid_beatmaps.append(beatmap)

                import random

                random.shuffle(valid_beatmaps)
                print(f"{len(valid_beatmaps)} Total beatmaps!")
                self.lists = valid_beatmaps
                return self.lists

        return []

    def rotate(self) -> None:
        self.lists = self.lists[1:] + self.lists[0:1]

    def get_first(self) -> RoomBeatmapDict:
        return self.lists[0]

    def get_queue(self) -> str:
        return ", ".join(
            [
                f"[https://osu.ppy.sh/b/{beatmap.get('beatmap_id', 0)} {beatmap.get('title', 'no_title')}]"
                for beatmap in self.lists[0:5]
            ]
        )

    def check_is_in_range(
        self, value: float | int, min: float | int, max: float | int
    ) -> bool:
        return min <= value and max >= value

    def check_star(self, star: float) -> bool:
        return self.check_is_in_range(star, self.star[0], self.star[1])

    def check_bpm(self, bpm: float) -> bool:
        return self.check_is_in_range(bpm, self.bpm[0], self.bpm[1])

    def check_ar(self, ar: float) -> bool:
        return self.check_is_in_range(ar, self.ar[0], self.ar[1])

    def check_length(self, length: int) -> bool:
        return self.check_is_in_range(length, self.length[0], self.length[1])

    def check_beatmap(self, url: str) -> int:
        beatmap = fetch_beatmap(url=url)

        if beatmap:
            beatmapset_id = beatmap.get("id", self.current)

            # if self.force_stat:
            #     if not self.check_star(beatmap.get("ratings", 0)):
            #         # todo
            #         return self.current

            #     return self.current

            self.current = beatmapset_id if type(beatmapset_id) == int else self.current

        return self.current


def message_beatmap_links(title: str, beatmap_id: int) -> str:
    return (
        f"[https://osu.ppy.sh/beatmapsets/{beatmap_id} {title}]  [https://beatconnect.io/b/{beatmap_id}/ beatconnect]  [https://chimu.moe/d/{beatmap_id} chimu]"
        if beatmap_id
        else "missing_beatmap_id"
    )
