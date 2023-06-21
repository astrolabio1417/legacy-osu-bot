export type IBotMode = "AUTO_HOST" | "AUTO_ROTATE_MAP";
export type IPlayMode = "OSU" | "TAIKO" | "CATCH_THE_BEAT" | "MANIA";
export type IScoreMode = "SCORE" | "ACCURACY" | "COMBO" | "SCORE_V2";
export type ITeamMode = "HEAD_TO_HEAD" | "TAG_COOP" | "TEAM_VS" | "TAG_VS";

export interface IRoomForm {
  name: string;
  room_size: number;
  bot_mode: string;
  play_mode: string;
  score_mode: string;
  team_mode: string;
  beatmap: {
    star: [number, number];
    cs: [number, number];
    ar: [number, number];
    od: [number, number];
    length: [number, number];
    bpm: [number, number];
    force_stat: boolean;
  };
}

export interface IBeatmap {
  ar: [number, number];
  bpm: [number, number];
  cs: [number, number];
  current: number;
  current_set: number;
  force_stat: boolean;
  length: [number, number];
  od: [number, number];
  star: [number, number];
}

export interface IRoom {
  id: string;
  name: string;
  room_id: string;
  room_size: number;
  bot_mode: IBotMode;
  play_mode: IPlayMode;
  score_mode: IScoreMode;
  team_mode: ITeamMode;
  is_closed: boolean;
  is_configured: boolean;
  is_connected: boolean;
  is_created: boolean;
  beatmap: IBeatmap;
  skips: string[];
  users: string[];
}

export interface IEnumsResponse {
  BOT_MODE: string[];
  PLAY_MODE: string[];
  SCORE_MODE: string[];
  TEAM_MODE: string[];
}
