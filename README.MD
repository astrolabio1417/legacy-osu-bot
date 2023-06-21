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


    [
        {
            "beatmap": {
            "ar": [
                0,
                10
            ],
            "bpm": [
                0,
                200
            ],
            "cs": [
                0,
                10
            ],
            "current": 34604,
            "current_set": 5561,
            "force_stat": false,
            "length": [
                60,
                180
            ],
            "od": [
                0,
                10
            ],
            "star": [
                0,
                10
            ]
            },
            "bot_mode": "AUTO_HOST",
            "id": "5c3903d7-100a-11ee-b66d-2cf05d88d3b7",
            "is_closed": false,
            "is_configured": true,
            "is_connected": true,
            "is_created": true,
            "name": "test 1",
            "play_mode": "OSU",
            "room_id": "#mp_109110993",
            "room_size": 16,
            "score_mode": "SCORE",
            "skips": [],
            "team_mode": "HEAD_TO_HEAD",
            "users": []
        }
    ]

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
        "beatmap": {
            "ar": [
            0,
            10
            ],
            "bpm": [
            0,
            200
            ],
            "cs": [
            0,
            10
            ],
            "current": 123874,
            "current_set": 38720,
            "force_stat": false,
            "length": [
            60,
            180
            ],
            "od": [
            0,
            10
            ],
            "star": [
            0,
            10
            ]
        },
        "bot_mode": "AUTO_HOST",
        "id": "5c3903d7-100a-11ee-b66d-2cf05d88d3b7",
        "is_closed": false,
        "is_configured": false,
        "is_connected": false,
        "is_created": true,
        "name": "test 2",
        "play_mode": "OSU",
        "room_id": "",
        "room_size": 16,
        "score_mode": "SCORE",
        "skips": [],
        "team_mode": "HEAD_TO_HEAD",
        "users": []
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
            9,
            10
            ],
            "bpm": [
            0,
            200
            ],
            "cs": [
            0,
            10
            ],
            "current": 2229508,
            "current_set": 1064829,
            "force_stat": false,
            "length": [
            60,
            1800
            ],
            "od": [
            0,
            10
            ],
            "star": [
            5,
            6.2
            ]
        },
        "bot_mode": "AUTO_ROTATE_MAP",
        "id": "9e1bfe1b-100c-11ee-a1bf-2cf05d88d3b7",
        "is_closed": false,
        "is_configured": true,
        "is_connected": true,
        "is_created": true,
        "name": "5-6.2* | AR9+ | Test Auto Map Rotation",
        "play_mode": "OSU",
        "room_id": "#mp_109111115",
        "room_size": 16,
        "score_mode": "SCORE",
        "skips": [],
        "team_mode": "HEAD_TO_HEAD",
        "users": [
            "rouel"
        ]
    }

## Change a room's state

### Request

`PUT /room/:id/`

    curl -i -H 'Accept: application/json' -X PUT http://localhost:5000/room/abcd-efgt-asda/

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
        "beatmap": {
            "ar": [
            0,
            10
            ],
            "bpm": [
            0,
            200
            ],
            "cs": [
            0,
            10
            ],
            "current": 1917081,
            "current_set": 917930,
            "force_stat": false,
            "length": [
            60,
            1800
            ],
            "od": [
            0,
            10
            ],
            "star": [
            3.9,
            10
            ]
        },
        "bot_mode": "AUTO_ROTATE_MAP",
        "id": "9e1bfe1b-100c-11ee-a1bf-2cf05d88d3b7",
        "is_closed": false,
        "is_configured": true,
        "is_connected": true,
        "is_created": true,
        "name": "test 2",
        "play_mode": "MANIA",
        "room_id": "#mp_109111115",
        "room_size": 3,
        "score_mode": "SCORE_V2",
        "skips": [],
        "team_mode": "TEAM_VS",
        "users": [
            "rouel"
        ]
    }

## Delete a Room

### Request

`DELETE /room/:id`

    curl -i -H 'Accept: application/json' -X DELETE http://localhost:5000/room/abcd-efgt-asda/

### Response

    HTTP/1.1 204 No Content
    Status: 204 No Content
