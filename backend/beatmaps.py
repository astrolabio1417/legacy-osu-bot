import random
from dataclasses import dataclass, field
from typing import Any, Optional
from bot_enums import RANK_STATUS, PLAY_MODE
from neri_scraper import neri_search, NeriSetting
from bot_typing import BeatmapDict, BeatmapSetDict
from scraper import fetch_beatmap


@dataclass
class RoomBeatmap:
    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)
    rank_status: list[RANK_STATUS] = field(
        default_factory=lambda: [
            RANK_STATUS.APPROVED,
            RANK_STATUS.RANKED,
            RANK_STATUS.LOVED,
            RANK_STATUS.QUALIFIED,
        ]
    )
    current: int = 0
    current_set: int = 0
    lists: list[BeatmapDict] = field(default_factory=list)
    asset_filename: str = "beatmaps-2.json"
    force_stat: bool = False

    def get_json(self) -> dict[str, Any]:
        return {
            "star": self.star,
            "ar": self.ar,
            "cs": self.cs,
            "length": self.length,
            "bpm": self.bpm,
            "rank_status": [rank.name for rank in self.rank_status],
            "current": self.current,
            "current_set": self.current_set,
            "force_stat": self.force_stat,
        }

    def get_list(self) -> list[BeatmapDict]:
        return self.lists

    def update(
        self,
        star: Optional[tuple[float, float]] = None,
        ar: Optional[tuple[float, float]] = None,
        cs: Optional[tuple[float, float]] = None,
        length: Optional[tuple[int, int]] = None,
        bpm: Optional[tuple[int, int]] = None,
        force_stat: Optional[bool] = None,
        asset_filename: Optional[str] = None,
    ) -> None:
        self.star = star or self.star
        self.ar = ar or self.ar
        self.cs = cs or self.cs
        self.length = length or self.length
        self.bpm = bpm or self.bpm
        self.force_stat = force_stat or self.force_stat
        self.asset_filename = asset_filename or self.asset_filename

    def setattrs(self, **kwargs: dict[str, Any]) -> None:
        for key, value in kwargs.items():
            try:
                if hasattr(self, key):
                    setattr(self, key, value)
            except AttributeError:
                pass

    def setup_beatmaps(self, play_mode: int, max: int = 1000) -> list[BeatmapDict]:
        beatmapsets = neri_search(
            page_size=50 if max == 1 else max,
            settings=NeriSetting(
                m=play_mode,
                star=self.star,
                cs=self.cs,
                length=self.length,
                bpm=self.bpm,
                ar=self.ar,
                s=",".join([str(rank.value) for rank in self.rank_status]),
            ),
        )
        beatmaps: list[BeatmapDict] = []

        for beatmapset in beatmapsets:
            for beatmap in reversed(beatmapset.get("beatmaps", [])):
                errors = self.get_beatmap_errors(beatmap, play_mode)

                if errors:
                    continue

                beatmap["difficulty_title"] = str(beatmap.get("version", ""))
                beatmap[
                    "title"
                ] = f"{beatmapset['title']} {beatmap['difficulty_title']}"
                # select one beatmap per beatmapset
                beatmaps.append(beatmap)
                break

        print("total fetch map: ", len(beatmapsets))
        print("total map: ", len(beatmaps))
        self.lists = beatmaps

        return beatmaps[0:1] if max == 1 else beatmaps

    def load_beatmaps(self, play_mode: int, max: int = 999999) -> list[BeatmapDict]:
        import json

        with open(f"./datasets/{self.asset_filename}", "r") as f:
            try:
                beatmaplist: list[BeatmapDict] = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return []

            if beatmaplist:
                valid_beatmaps = []
                random.shuffle(beatmaplist)

                for beatmap in beatmaplist:
                    if not beatmap.get("id", False):
                        continue

                    play_mode = beatmap.get("mode_int", -1) == play_mode
                    ar = self.check_ar(beatmap.get("ar", 0.00))
                    star = self.check_star(beatmap.get("difficulty_rating", 0.00))
                    length = self.check_length(beatmap.get("total_length", 0))
                    bpm = self.check_bpm(beatmap.get("bpm", 0))

                    if play_mode and ar and star and length and bpm:
                        valid_beatmaps.append(beatmap)

                        if len(valid_beatmaps) >= max:
                            break

                print(f"{len(valid_beatmaps)} Total beatmaps!")
                self.lists = valid_beatmaps
                return self.lists

        return []

    def init_current(self, play_mode: int) -> BeatmapDict | None:
        self.setup_beatmaps(play_mode, max=1)

        if not self.lists:
            return None

        self.current = self.lists[0].get("id", 0)
        self.current_set = self.lists[0].get("beatmapset_id", 0)
        return self.lists[0]

    def rotate(self) -> None:
        self.lists = self.lists[1:] + self.lists[0:1]

    def get_first(self) -> BeatmapDict:
        return self.lists[0]

    def get_queue(self) -> str:
        return ", ".join(
            [
                f"[https://osu.ppy.sh/beatmapsets/{beatmap.get('beatmapset_id', 0)} {beatmap.get('title', 'no_title')} - {beatmap.get('difficulty_title', '?')}]"
                for beatmap in self.lists[0:3]
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

    def check_cs(self, cs: float) -> bool:
        return self.check_is_in_range(cs, self.cs[0], self.cs[1])

    def check_ar(self, ar: float) -> bool:
        return self.check_is_in_range(ar, self.ar[0], self.ar[1])

    def check_length(self, length: int) -> bool:
        return self.check_is_in_range(length, self.length[0], self.length[1])

    def check_rank(self, status: int) -> bool:
        return status in [status.value for status in self.rank_status]

    def get_beatmap(
        self, url: str, beatmap_id: int
    ) -> tuple[BeatmapSetDict, BeatmapDict] | None:
        beatmapset = fetch_beatmap(url=url)

        if not beatmapset:
            return None

        for bm in beatmapset.get("beatmaps", []):
            if bm.get("id") == beatmap_id:
                return (beatmapset, bm)

        return None

    def get_beatmap_errors(self, beatmap: BeatmapDict, mode_int: int) -> list[str]:
        """return errors"""
        errors: list[str] = []

        if not beatmap:
            return False

        mode = beatmap.get("mode_int") == mode_int
        star = self.check_star(beatmap.get("difficulty_rating", 0))
        ar = self.check_ar(beatmap.get("ar", 0))
        bpm = self.check_bpm(beatmap.get("bpm", 0))
        length = self.check_length(beatmap.get("total_length", 0))
        cs = self.check_cs(beatmap.get("cs", 0))
        rank = self.check_rank(beatmap.get("ranked", 1))

        play_error = f"Play Mode {PLAY_MODE(beatmap.get('mode_int', -9)).name} != {PLAY_MODE(mode_int).name}"
        star_error = (
            f"Star {beatmap.get('difficulty_rating')} != {self.star[0]}-{self.star[1]}*"
        )
        ar_error = f"AR {beatmap.get('ar')} != {self.ar[0]}-{self.ar[1]}"
        bpm_error = f"BPM {beatmap.get('bpm')} != {self.bpm[0]}-{self.bpm[1]}"
        length_error = (
            f"Length {beatmap.get('total_length')} != {self.length[0]}-{self.length[1]}"
        )
        cs_error = f"CS {beatmap.get('cs')} != {self.cs[0]}-{self.cs[1]}"
        rank_error = f"Rank Status {RANK_STATUS(beatmap.get('ranked', -9)).name} != [{' | '.join([rank.name for rank in self.rank_status])}]"

        for name, is_valid in [
            (play_error, mode),
            (star_error, star),
            (ar_error, ar),
            (bpm_error, bpm),
            (length_error, length),
            (cs_error, cs),
            (rank_error, rank),
        ]:
            if not is_valid:
                errors.append(name)

        return errors


def message_beatmap_links(title: str, beatmap_id: int) -> str:
    return (
        f"[https://osu.ppy.sh/beatmapsets/{beatmap_id} {title}]  [https://beatconnect.io/b/{beatmap_id}/ beatconnect]  [https://chimu.moe/d/{beatmap_id} chimu]"
        if beatmap_id
        else "missing_beatmap_id"
    )
