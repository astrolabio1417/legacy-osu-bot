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

-   run the backend

```
flask run
```

# REST API

The REST API to the example app is described below.

## Get list of Room

### Request

`GET /room/`

    curl -i -H 'Accept: application/json' http://localhost:5000/room/

### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Content-Type: application/json


    {
        "lists": [
            {
                "beatmap": {
                    "ar": [
                        9.0,
                        10.0
                    ],
                    "bpm": [
                        0,
                        200
                    ],
                    "cs": [
                        0.0,
                        10.0
                    ],
                    "current": 2201963,
                    "current_set": 1053771,
                    "force_stat": true,
                    "length": [
                        60,
                        150
                    ],
                    "od": [
                        0.0,
                        10.0
                    ],
                    "star": [
                        5.0,
                        6.0
                    ]
                },
                "bot_mode": {
                    "name": "AUTO_HOST",
                    "value": "AutoHost"
                },
                "is_closed": false,
                "is_configured": true,
                "is_connected": false,
                "is_created": true,
                "name": "Testing Room 1",
                "play_mode": {
                    "name": "OSU",
                    "value": [
                        "osu!",
                        0
                    ]
                },
                "room_id": "#mp_109084008",
                "room_size": 16,
                "score_mode": {
                    "name": "SCORE",
                    "value": [
                        "Score",
                        0
                    ]
                },
                "skips": [],
                "team_mode": {
                    "name": "HEAD_TO_HEAD",
                    "value": [
                        "HeadToHead",
                        0
                    ]
                },
                "users": [
                    "rouel"
                ]
            }
        ],
        "message": "ok",
        "status": 200
    }

## Create a new Room

### Request

`POST /room/`

    curl -i -H 'Accept: application/json' -d 'name=testingroom&password=testing' http://localhost:5000/room/

    {
        "bot_mode": "AUTO_HOST" | "AUTO_ROTATE_MAP",
        "play_mode": "OSU" | "TAIKO" | "CATCH_THE_BEAT" | "MANIA",
        "team_mode": "HEAD_TO_HEAD" | "TAG_COOP" | "TEAM_VS" | "TAG_VS",
        "score_mode": "SCORE" | "ACCURACY" | "COMBO" | "SCORE_V2",
        "room_size": int,
        "name": string required,
        "password": string,
        "beatmap": {
            "star": [float, float],
            "cs": [float, float],
            "od": [float, float],
            "ar": [float, float],
            "length": [int, int],
            "bpm": [int, int],
            "current": int,
            "current_set": int,
            "force_stat": bool
        }
    }

### Response

    HTTP/1.1 201 Created
    Status: 201 Created
    Content-Type: application/json

    {
        "message": "Room has been created!",
        "status": 201
    }

## Get a specific Room

### Request

`GET /room/:room_id`

    curl -i -H 'Accept: application/json' http://localhost:5000/room/mp_999999

### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Content-Type: application/json

     {
        "beatmap": {
            "ar": [
                9.0,
                10.0
            ],
            "bpm": [
                0,
                200
            ],
            "cs": [
                0.0,
                10.0
            ],
            "current": 2201963,
            "current_set": 1053771,
            "force_stat": true,
            "length": [
                60,
                150
            ],
            "od": [
                0.0,
                10.0
            ],
            "star": [
                5.0,
                6.0
            ]
        },
        "bot_mode": {
            "name": "AUTO_HOST",
            "value": "AutoHost"
        },
        "is_closed": false,
        "is_configured": true,
        "is_connected": false,
        "is_created": true,
        "name": "Testing Room 1",
        "play_mode": {
            "name": "OSU",
            "value": [
                "osu!",
                0
            ]
        },
        "room_id": "#mp_109084008",
        "room_size": 16,
        "score_mode": {
            "name": "SCORE",
            "value": [
                "Score",
                0
            ]
        },
        "skips": [],
        "team_mode": {
            "name": "HEAD_TO_HEAD",
            "value": [
                "HeadToHead",
                0
            ]
        },
        "users": [
            "rouel"
        ]
    }

## Change a room's state

### Request

`PUT /room/:room_id/`

    curl -i -H 'Accept: application/json' -X PUT http://localhost:5000/room/mp_99999/

     {
        "bot_mode": "AUTO_HOST" | "AUTO_ROTATE_MAP",
        "play_mode": "OSU" | "TAIKO" | "CATCH_THE_BEAT" | "MANIA",
        "team_mode": "HEAD_TO_HEAD" | "TAG_COOP" | "TEAM_VS" | "TAG_VS",
        "score_mode": "SCORE" | "ACCURACY" | "COMBO" | "SCORE_V2",
        "room_size": int,
        "name": string required,
        "password": string,
        "beatmap": {
            "star": [float, float],
            "cs": [float, float],
            "od": [float, float],
            "ar": [float, float],
            "length": [int, int],
            "bpm": [int, int],
            "current": int,
            "current_set": int,
            "force_stat": bool
        }
    }

### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Content-Type: application/json

    {
        "message": "Room has been updated!",
        "status": 200
    }

## Delete a Room

### Request

`DELETE /room/:room_id`

    curl -i -H 'Accept: application/json' -X DELETE http://localhost:5000/room/mp_999999/

### Response

    HTTP/1.1 204 No Content
    Status: 204 No Content
