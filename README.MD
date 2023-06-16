# legacy api | osubot | host rotate | map rotate

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

-   run the app

```
py main.js
```
