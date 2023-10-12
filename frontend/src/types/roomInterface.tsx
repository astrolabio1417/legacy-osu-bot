import { IBeatmap } from "./beatmapInterface";

export type IBotMode = "AUTO_HOST" | "AUTO_ROTATE_MAP";
export type IPlayMode = "OSU" | "TAIKO" | "CATCH_THE_BEAT" | "MANIA";
export type IScoreMode = "SCORE" | "ACCURACY" | "COMBO" | "SCORE_V2";
export type ITeamMode = "HEAD_TO_HEAD" | "TAG_COOP" | "TEAM_VS" | "TAG_VS";

export interface IRoomForm {
  name: string;
  room_size: number;
  bot_mode: IBotMode;
  play_mode: IPlayMode;
  score_mode: IScoreMode;
  team_mode: ITeamMode;
  beatmap: IBeatmap;
}

export interface IRoom extends IRoomForm {
  room_id: string;
  id: string;
  is_configured: boolean;
  is_connected: boolean;
  is_created: boolean;
  skips: string[];
  users: string[];
}
