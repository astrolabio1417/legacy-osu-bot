from typing import Optional
from bot.enums import SlotDict, MessageDict
from bot.constants import VALID_ROLES


def normalize_username(username: str) -> str:
    return username.strip().replace(" ", "_")


def parse_slot(message: str) -> SlotDict:
    message_words = message.split()
    slot = message_words[1]

    if message_words[2] != "Ready":
        status = " ".join(message_words[2:4])
        url = message_words[4]
        user_roles = " ".join(message_words[5:])
    else:
        status = message_words[2]
        url = message_words[3]
        user_roles = " ".join(message_words[4:])

    username = user_roles
    roles = []
    start_roles_index = user_roles.rfind("[")

    if user_roles.endswith("]") and start_roles_index != -1:
        roles = user_roles[start_roles_index + 1 : -1].replace(" ", "").split("/")
        roles = roles[:-1] + roles[-1].split(",")

        if any(role.strip() not in VALID_ROLES for role in roles):
            roles = []
        else:
            username = user_roles[: start_roles_index - 1]

    username = username.strip().replace(" ", "_")
    user_id = url.split("/")[-1]

    return SlotDict(
        username=username,
        user_id=user_id,
        status=status,
        slot=int(slot) if slot.isdigit() else 0,
        roles=roles,
    )


def parse_message(message: str) -> Optional[MessageDict]:
    words = message.strip().split(" ")

    if len(words) < 3 or not message.startswith(":"):
        return None

    no_channel_commands = {"JOIN", "PART", "QUIT"}
    invalid_channel_end_strings = {"!cho@ppy.sh", "!cho@cho.ppy.sh"}
    invalid_message_start_char = ":"

    sender = words[0][1:].rstrip("".join(invalid_channel_end_strings))
    command = words[1]
    channel = words[2]
    message = " ".join(words[3:])

    if command in no_channel_commands:
        channel = ""
        message = " ".join(words[2:])

    message = message.lstrip(invalid_message_start_char)

    return MessageDict(sender=sender, command=command, channel=channel, message=message)


def get_beatmapset_id_from_url(url: str) -> int:
    parts = url.split("/")
    beatmapset_id = parts[-2].partition("#")[0]
    return int(beatmapset_id)


def get_beatmap_id_from_url(url: str) -> int:
    parts = url.split("/")
    beatmap_id = parts[-1].partition("#")[0]
    return int(beatmap_id)


if __name__ == "__main__":
    pass
