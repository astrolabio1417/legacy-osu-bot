from dataclasses import dataclass, field
from typing import Any
from bot.osuapi import osu_api
from ossapi import Beatmap, Cursor, Beatmapset
from bot.enums import PLAY_MODE, RANK_STATUS, RoomBeatmapData
from ossapi.enums import BeatmapsetSearchGenre, BeatmapsetSearchLanguage
from my_logger import logger

default_beatmapset = osu_api.beatmapset(beatmapset_id=2005593)


@dataclass
class RoomBeatmap:
    play_mode: PLAY_MODE = PLAY_MODE.OSU
    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)
    rank_status: list[RANK_STATUS] = field(default_factory=lambda: [status for status in RANK_STATUS])
    genre: BeatmapsetSearchGenre = BeatmapsetSearchGenre.ANY
    language: BeatmapsetSearchLanguage = BeatmapsetSearchLanguage.ANY
    beatmap_list: list[Beatmap] = field(default_factory=list)

    _cursor: Cursor | None = None

    def __post_init__(self) -> None:
        self.generate_beatmaps()

    @property
    def current(self) -> Beatmap:
        return self.beatmap_list[0] if self.beatmap_list else default_beatmapset.beatmaps[0]

    def set_current(self, beatmap: Beatmap) -> Beatmap:
        self.beatmap_list.insert(0, beatmap)
        return self.current

    def get_json(self) -> RoomBeatmapData:
        return {
            "play_mode": self.play_mode.name,
            "star": self.star,
            "ar": self.ar,
            "cs": self.cs,
            "length": self.length,
            "bpm": self.bpm,
            "rank_status": [rank.name for rank in self.rank_status],
            "lists": self.get_json_list(),
            "current": self.current_json(),
            "genre": self.genre.name,
            "language": self.language.name,
        }

    def current_json(self) -> Beatmap:
        return {
            key: value
            for key, value in self.current.__dict__.items()
            if not key.startswith("_") and isinstance(value, (str, int, list, dict))
        }

    def get_json_list(self) -> list[Beatmap]:
        return [
            {
                key: value
                for key, value in beatmap.__dict__.items()
                if not key.startswith("_") and isinstance(value, (str, int, list, dict))
            }
            for beatmap in self.beatmap_list
        ]

    def configure(self, **kwargs: dict[str, Any]) -> None:
        changed = False

        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)

        if changed:
            self._cursor = None
            self.beatmap_list = []
            self.generate_beatmaps()

    def generate_beatmaps(self) -> list[Beatmap]:
        if len(self.beatmap_list) >= 3:
            return self.beatmap_list

        logger.info("generating beatmaps...")

        q = osu_api.search_beatmapsets(
            mode=self.play_mode,
            sort="plays_desc",
            cursor=self._cursor,
            genre=self.genre,
            language=self.language,
        )
        self._cursor = q.cursor

        for beatmapset in q.beatmapsets:
            beatmapset.beatmaps.sort(key=lambda x: x.difficulty_rating, reverse=True)

            for beatmap in beatmapset.beatmaps:
                if not self.get_beatmap_errors(beatmap):
                    self.beatmap_list.append(beatmap)
                    break

        return self.generate_beatmaps()

    def rotate(self) -> None:
        self.beatmap_list.pop(0)
        self.generate_beatmaps()

    def get_queue(self) -> str:
        if not self.beatmap_list:
            return "No Beatmaps"

        queue_links = [f"[{beatmap.url} {beatmap.beatmapset().title}]" for beatmap in self.beatmap_list[1:3]]
        return ", ".join(queue_links)

    def is_in_range(self, value: float | int, minimum: float | int, maximum: float | int) -> bool:
        return minimum <= value and maximum >= value

    def check_star(self, star: float) -> bool:
        return self.is_in_range(star, self.star[0], self.star[1])

    def check_bpm(self, bpm: float) -> bool:
        return self.is_in_range(bpm, self.bpm[0], self.bpm[1])

    def check_cs(self, cs: float) -> bool:
        return self.is_in_range(cs, self.cs[0], self.cs[1])

    def check_ar(self, ar: float) -> bool:
        return self.is_in_range(ar, self.ar[0], self.ar[1])

    def check_length(self, length: int) -> bool:
        return self.is_in_range(length, self.length[0], self.length[1])

    def check_rank(self, status: int) -> bool:
        return status in [status.value for status in self.rank_status]

    def get_beatmapset_errors(self, beatmapset: Beatmapset) -> list[str]:
        errors = []

        # TODO bypass for now, the wrapper ossapi beatmapset doesn't give the right values
        genre_id = beatmapset.genre.get("id")
        language_id = beatmapset.language.get("id")

        genre = BeatmapsetSearchGenre(genre_id) if genre_id else BeatmapsetSearchGenre.ANY
        language = BeatmapsetSearchLanguage(language_id) if language_id else BeatmapsetSearchLanguage.ANY

        if self.genre != BeatmapsetSearchGenre.ANY and self.genre != genre:
            errors.append(f"Genre {genre.name} != {self.genre.name}")

        if self.language != BeatmapsetSearchLanguage.ANY and self.language != language:
            errors.append(f"Language {language.name} != {self.language.name}")

        return errors

    def get_beatmap_errors(self, beatmap: Beatmap) -> list[str]:
        errors: list[str] = []

        error_checks = [
            (f"Play Mode {beatmap.mode.name} != {self.play_mode.name}", beatmap.mode_int == self.play_mode.value),
            (
                f"Star {beatmap.difficulty_rating} != {self.star[0]}-{self.star[1]}*",
                self.check_star(beatmap.difficulty_rating),
            ),
            (
                f"Rank Status {beatmap.ranked.name} != [{' | '.join([rank.name for rank in self.rank_status])}]",
                self.check_rank(beatmap.ranked.value),
            ),
            (f"AR {beatmap.ar} != {self.ar[0]}-{self.ar[1]}", self.check_ar(beatmap.ar)),
            (f"BPM {beatmap.bpm} != {self.bpm[0]}-{self.bpm[1]}", self.check_bpm(beatmap.bpm)),
            (
                f"Length {beatmap.total_length} != {self.length[0]}-{self.length[1]}",
                self.check_length(beatmap.total_length),
            ),
            (f"CS {beatmap.cs} != {self.cs[0]}-{self.cs[1]}", self.check_cs(beatmap.cs)),
        ]

        for error, is_valid in error_checks:
            if not is_valid:
                errors.append(error)

        return errors

    @property
    def links(self) -> str:
        beatmapset_id = self.current.beatmapset_id

        if not beatmapset_id:
            return "missing_beatmap_id"

        osu_link = f"[https://osu.ppy.sh/beatmapsets/{beatmapset_id} osu]"
        beatconnect_link = f"[https://beatconnect.io/b/{beatmapset_id}/ beatconnect]"
        chimu_link = f"[https://chimu.moe/d/{beatmapset_id} chimu]"

        return f"{osu_link} {beatconnect_link} {chimu_link}"


if __name__ == "__main__":
    bm = RoomBeatmap()
    print(bm.current)
