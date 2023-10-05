# legacy | osubot | auto host rotate | auto beatmap rotate

#### HOW TO CREATE CREDENTIALS

```
    go to your account settings (https://osu.ppy.sh/home/account/edit)
```

- HOW TO CREATE PASSWORD

```
    Create "Legacy API" and copy your "SERVER PASSWORD"
```

- HOW TO CREATE CLIENT ID/SESSION

```
   Create "OAuth" and copy your "CLIENT ID" and "CLIENT SECRET"
```

##### ENVIRONMENT

- USERNAME: your osu username
- PASSWORD: legacy api server password
- CLIENT_ID: oauth client id
- CLIENT_SECRET: oauth client secret

# DOCKER SETUP

- Download and Install Docker https://www.docker.com/products/docker-desktop/
- Edit docker-compose.yml environment
- Run Docker app

```
docker compose -f "docker-compose.yml" up -d --build
```

- Visit local link http://localhost:3000/

# HOW TO USE

- Login to your account using your username and server password
- Toggle ON IRC Button on Nav bar
- Create New Room
