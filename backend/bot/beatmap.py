from dataclasses import dataclass, field
from typing import Any
from bot.api import osu_api
from ossapi import Beatmap, Cursor, Beatmapset
from bot.enums import PLAY_MODE, RANK_STATUS, RoomBeatmapData
from ossapi.enums import BeatmapsetSearchGenre, BeatmapsetSearchLanguage

default_beatmapset = osu_api.beatmapset(beatmapset_id=2005593)


@dataclass
class RoomBeatmap:
    play_mode: PLAY_MODE = PLAY_MODE.OSU
    star: tuple[float, float] = (0.00, 10.00)
    ar: tuple[float, float] = (0.00, 10.00)
    cs: tuple[float, float] = (0.00, 10.00)
    length: tuple[int, int] = (0, 1000000)
    bpm: tuple[int, int] = (0, 200)
    rank_status: list[RANK_STATUS] = field(
        default_factory=lambda: [status for status in RANK_STATUS]
    )
    genre: BeatmapsetSearchGenre = BeatmapsetSearchGenre.ANY
    language: BeatmapsetSearchLanguage = BeatmapsetSearchLanguage.ANY
    lists: list[Beatmap] = field(default_factory=list)

    _cursor: Cursor | None = None

    def __post_init__(self) -> None:
        self.generate_beatmaps()

    @property
    def current(self) -> Beatmap:
        return self.lists[0] if self.lists else default_beatmapset.beatmaps[0]

    def set_current(self, beatmap: Beatmap) -> Beatmap:
        self.lists.insert(0, beatmap)
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

    def get_list(self) -> list[Beatmap]:
        return self.lists

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
            for beatmap in self.lists
        ]

    def configure(self, **kwargs: dict[str, Any]) -> None:
        changed = False

        for key, value in kwargs.items():
            try:
                if not hasattr(self, key):
                    continue

                if self.__dict__.get(key) != value:
                    changed = True

                setattr(self, key, value)
            except AttributeError as err:
                print(f"There are no {key} attribute on Room. Error: ", err)
                pass

        if changed:
            self._cursor = None
            self.lists = []
            self.generate_beatmaps()

    def generate_beatmaps(self) -> list[Beatmap]:
        if len(self.lists) >= 3:
            return self.lists

        print("generating beatmaps")

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
                errors = self.get_beatmap_errors(beatmap)

                if errors:
                    continue

                self.lists.append(beatmap)
                break  # skip to next beatmapset, one beatmap per set

        return self.generate_beatmaps()

    def rotate(self) -> None:
        self.lists.pop(0)
        self.generate_beatmaps()

    def get_queue(self) -> str:
        if not self.lists:
            return "No Beatmaps"

        return ", ".join(
            [
                f"[{beatmap.url} {beatmap.beatmapset().title}]"
                for beatmap in self.lists[1:3]
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

    def get_beatmapset_errors(self, beatmapset: Beatmapset) -> list[str]:
        errors = []

        # TODO bypass for now, the wrapper ossapi beatmapset doesn't give the right values
        genre = beatmapset.genre.get("id")
        language = beatmapset.language.get("id")
        genre = BeatmapsetSearchGenre(genre) if genre else BeatmapsetSearchGenre.ANY
        language = (
            BeatmapsetSearchLanguage(language)
            if language
            else BeatmapsetSearchLanguage.ANY
        )

        if not self.genre == BeatmapsetSearchGenre.ANY and self.genre != genre:
            genre_error = f"Genre {genre.name} != {self.genre.name}"
            errors.append(genre_error)

        if (
            not self.language == BeatmapsetSearchLanguage.ANY
            and self.language != language
        ):
            language_error = f"Language {language.name} != {self.language.name}"
            errors.append(language_error)

        return errors

    def get_beatmap_errors(self, beatmap: Beatmap) -> list[str]:
        """return errors"""
        errors: list[str] = []

        play_mode_error = f"Play Mode {beatmap.mode.name} != {self.play_mode.name}"
        star_error = (
            f"Star {beatmap.difficulty_rating} != {self.star[0]}-{self.star[1]}*"
        )
        ar_error = f"AR {beatmap.ar} != {self.ar[0]}-{self.ar[1]}"
        bpm_error = f"BPM {beatmap.bpm} != {self.bpm[0]}-{self.bpm[1]}"
        length_error = (
            f"Length {beatmap.total_length} != {self.length[0]}-{self.length[1]}"
        )
        cs_error = f"CS {beatmap.cs} != {self.cs[0]}-{self.cs[1]}"
        rank_error = f"Rank Status {beatmap.ranked.name} != [{' | '.join([rank.name for rank in self.rank_status])}]"

        for error, is_valid in [
            (play_mode_error, beatmap.mode_int == self.play_mode.value),
            (star_error, self.check_star(beatmap.difficulty_rating)),
            (ar_error, self.check_ar(beatmap.ar)),
            (bpm_error, self.check_bpm(beatmap.bpm)),
            (length_error, self.check_length(beatmap.total_length)),
            (cs_error, self.check_cs(beatmap.cs)),
            (rank_error, self.check_rank(beatmap.ranked.value)),
        ]:
            if not is_valid:
                errors.append(error)

        return errors

    @property
    def links(self) -> str:
        id = self.current.beatmapset_id

        if not id:
            return "missing_beatmap_id"

        return f"[https://osu.ppy.sh/beatmapsets/{id} osu]  [https://beatconnect.io/b/{id}/ beatconnect]  [https://chimu.moe/d/{id} chimu]"


if __name__ == "__main__":
    bm = RoomBeatmap()
    print(bm.current)
