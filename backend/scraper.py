import json
import re
import requests
from typing import Optional
from bot_typing import BeatmapSetDict


def fetch_beatmap(url: str, errors: int = 0) -> Optional[BeatmapSetDict]:
    try:
        response = requests.get(url, timeout=(10, 10))
        print(f"~ Fetch status|code: {response.ok} | {response.status_code}")
    except (
        requests.exceptions.Timeout,
        TimeoutError,
        requests.exceptions.ReadTimeout,
    ) as err:
        print(f"~ Fetch beatmap timeout error! | {err}")
        max_errors = 3

        if errors >= max_errors:
            return None

        return fetch_beatmap(url, errors + 1)
    except Exception as err:
        print(f"~ Fetch beatmap info error! | {err}")
        return None

    if response and response.ok and response.text:
        beatmap_info_search = re.search('\{"artist".+', response.text)

        if beatmap_info_search:
            beatmap_info = beatmap_info_search.group(0)

            if beatmap_info:
                try:
                    beatmap_info_json: BeatmapSetDict = json.loads(beatmap_info)
                    return beatmap_info_json
                except json.decoder.JSONDecodeError as err:
                    print(f"Beatmap info decode error | {err}")

    print("Beatmap failed to fetch")
    return None


if __name__ == "__main__":
    pass
