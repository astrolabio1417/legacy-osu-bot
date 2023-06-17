# legacy | osubot | host rotate | map rotate

##### TEAM_MODE

-   0: "HeadToHead"
-   1: "TagCoop"
-   2: "TeamVs"
-   3: "TagTeamVs"

##### SCORE_MODE

-   0: "Score"
-   1: "Accuracy"
-   2: "Combo"
-   3: "ScoreV2"

##### PLAY_MODE

-   0: "osu!"
-   1: "Taiko"
-   2: "Catch the Beat"
-   3: "osu!Mania"

##### BOT_MODE

-   0: "AutoHost"
-   1: "AutoRotateMap"

#### SETUP

-   download and install python https://www.python.org/downloads/
-   pip install -r requirements.txt

-   go to https://osu.ppy.sh/home/account/edit
-   on Legacy API create IRC
-   create config.json and add your credentials

```
{
    "username": "username",
    "password": "server password"
}
```

-   edit main.js
-   add room sample

```
    # auto host
    room_bot.add_room(
        Room(
            irc=irc,
            name="testing",
            password="test",
            bot_mode=BOT_MODE.AUTO_HOST,
            team_mode=TEAM_MODE.HEAD_TO_HEAD,
            score_mode=SCORE_MODE.SCORE,
            play_mode=PLAY_MODE.OSU,
            room_size=12,
            beatmap=RoomBeatmap(
                ar=(9.00, 10.00),
                star=(5.0, 6.0),
                length=(0, 300),
                bpm=(0, 500),
            ),
        )
    )

    # auto rotate map
    Room(
        irc=irc,
        name="testing 5.5-6.5* | AR9+ | JP songs | Auto Map Rotate",
        password="test",
        bot_mode=BOT_MODE.AUTO_ROTATE_MAP,
        team_mode=TEAM_MODE.HEAD_TO_HEAD,
        room_size=12,
        beatmap=RoomBeatmap(
            ar=(9.00, 10.00),
            star=(5.5, 6.5),
            length=(120, 240),
            bpm=(0, 500),
            asset_filename="list-std-ranked-jp.json",
        ),
    )
```

-   run the app

```
py main.js
```
