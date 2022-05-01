from typing import Optional, TypedDict

from constants import VALID_ROLES


def parse_username(username: str) -> str:
    return f"{username}".strip().replace(" ", "_")


class SlotDict(TypedDict):
    status: str
    slot: int
    user_id: str
    username: str
    roles: list[str]


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

    # 50/50 for user who have bracket in name... fvckng names | Fvck REGEX
    if user_and_roles[-1] == "]" and start_roles_index != -1:
        username = user_and_roles[0 : start_roles_index - 1]
        roles = (
            user_and_roles[start_roles_index + 1 : -1]
            .replace(" ", "")
            .split("/")
        )
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


class MessageDict(TypedDict):
    sender: str
    command: str
    channel: str
    message: str


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

    return MessageDict(
        sender=sender, command=command, channel=channel, message=message
    )


def test_message_parser() -> None:
    a = """phatang ina ano nangyayari
:cho.ppy.sh 001 rouel :Welcome to the osu!Bancho.
:cho.ppy.sh 372 rouel :- web:    https://osu.ppy.sh
:cho.ppy.sh 372 rouel :- status: https://twitter.com/osustatus
:cho.ppy.sh 372 rouel :- boat:   https://twitter.com/banchoboat
:BanchoBot!cho@ppy.sh PRIVMSG rouel :Created the tournament match https://osu.ppy.sh/mp/100125707 yeet
:rouel!cho@ppy.sh JOIN :#mp_100125707
:BanchoBot!cho@cho.ppy.sh MODE #mp_100125707 +v rouel
:cho.ppy.sh 332 rouel #mp_100125707 :multiplayer game #13796
:cho.ppy.sh 333 rouel #mp_100125707 BanchoBot!BanchoBot@cho.ppy.sh 1651017610
:cho.ppy.sh 353 rouel = #mp_100125707 :@BanchoBot rouel +rouel 
:cho.ppy.sh 366 rouel #mp_100125707 :End of /NAMES list.
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :Host is changing map...
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :Beatmap changed to: Minstrel - Fiction [KKip's Hard] (https://osu.ppy.sh/b/2454858)
:rouel!cho@ppy.sh PRIVMSG #mp_100125707 :!mp start
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :The match has started!
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :Started the match
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :rouel finished playing (Score: 0, FAILED).
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :The match has finished!
:rouel!cho@ppy.sh PRIVMSG #mp_100125707 :!mp close
:rouel!cho@ppy.sh PART :#mp_100125707
:BanchoBot!cho@ppy.sh PRIVMSG #mp_100125707 :Closed the match"""

    for line in a.split("\n"):
        print(parse_message(line))


if __name__ == "__main__":
    test_message_parser()
