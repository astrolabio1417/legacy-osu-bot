const CONFIG = {
  api: import.meta.env.API ?? `http://localhost:8000/`,
  BEATMAP_SETTING_KEYS: [
    "star",
    "cs",
    "ar",
    "od",
    "length",
    "bpm",
    "force_stat",
  ],
  ROOM_SETTING_KEYS: [
    "room_size",
    "score_mode",
    "play_mode",
    "bot_mode",
    "team_mode",
    "name",
  ],
};

// eslint-disable-next-line react-refresh/only-export-components
export { CONFIG };
