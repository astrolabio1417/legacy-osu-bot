from typing import Optional
from bot.enums import SlotDict, MessageDict
from bot.constants import VALID_ROLES


def normalize_username(username: str) -> str:
    return f"{username}".strip().replace(" ", "_")


def parse_slot(message: str) -> SlotDict:
    words = message.split()
    slot = words[1]
    user_and_roles = url = username = None

    if words[2] != "Ready":
        status = " ".join(words[2:4])
        url = words[4]
        user_and_roles = " ".join(words[5:])
    else:
        status = words[2]
        url = words[3]
        user_and_roles = " ".join(words[4:])

    username = user_and_roles
    roles = []
    start_roles_index = user_and_roles.rfind("[")

    if user_and_roles[-1] == "]" and start_roles_index != -1:
        username = user_and_roles[0 : start_roles_index - 1]
        roles = user_and_roles[start_roles_index + 1 : -1].replace(" ", "").split("/")
        roles = roles[0:-1] + roles[-1].split(",")

        for role in roles:
            if role.strip() not in VALID_ROLES:
                username = user_and_roles
                roles = []
                break

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

    NO_CHANNEL_COMMANDS = ["JOIN", "PART", "QUIT"]
    INVALID_CHANNEL_END_STRINGS = ["!cho@ppy.sh", "!cho@cho.ppy.sh"]
    INVALID_MESSAGE_START_CHAR = ":"
    sender = words[0][1:]
    command = words[1]
    channel = words[2]
    message = ""

    for invalid_str in INVALID_CHANNEL_END_STRINGS:
        if sender.endswith(invalid_str):
            sender = sender[0 : -len(invalid_str)]

    if command in NO_CHANNEL_COMMANDS:
        channel = ""
        message = " ".join(words[2:])
    else:
        message = " ".join(words[3:])

    if message.startswith(INVALID_MESSAGE_START_CHAR):
        message = message[1:]

    return MessageDict(sender=sender, command=command, channel=channel, message=message)


def get_beatmapset_id_from_url(url: str) -> int:
    parts = url.split("/")
    beatmapset_id = parts[-2].split("#")[0]
    print(f"beatmapset_id: {beatmapset_id}, url: {url}, parts: {parts}")
    return int(beatmapset_id)


def get_beatmap_id_from_url(url: str) -> int:
    parts = url.split("/")
    beatmap_id = parts[-1].split("#")[0]
    return int(beatmap_id)


if __name__ == "__main__":
    pass
