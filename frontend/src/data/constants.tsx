/* eslint-disable react-refresh/only-export-components */

export const API = import.meta.env.VITE_API ?? `http://localhost:8000/`;

export const BEATMAP_KEYS = ["star", "cs", "ar", "od", "length", "bpm"];

export const ROOM_KEYS = [
  "room_size",
  "score_mode",
  "play_mode",
  "bot_mode",
  "team_mode",
  "name",
];
