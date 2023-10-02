# legacy | osubot | host rotate | map rotate

##### TEAM_MODE

- 0: "HeadToHead"
- 1: "TagCoop"
- 2: "TeamVs"
- 3: "TagTeamVs"

##### SCORE_MODE

- 0: "Score"
- 1: "Accuracy"
- 2: "Combo"
- 3: "ScoreV2"

##### PLAY_MODE

- 0: "osu!"
- 1: "Taiko"
- 2: "Catch the Beat"
- 3: "osu!Mania"

##### BOT_MODE

- 0: "AutoHost"
- 1: "AutoRotateMap"

# DOCKER SETUP

- Download and Install Docker https://www.docker.com/products/docker-desktop/
- Edit docker-compose.yml environment
- Run Docker app

```
docker compose -f "docker-compose.yml" up -d --build
```

- Visit local link http://localhost:3000/
