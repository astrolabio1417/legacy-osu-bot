import { IBeatmap } from "./beatmapInterface";

export type IBotMode = "AUTO_HOST" | "AUTO_ROTATE_MAP";
export type IPlayMode = "OSU" | "TAIKO" | "CATCH_THE_BEAT" | "MANIA";
export type IScoreMode = "SCORE" | "ACCURACY" | "COMBO" | "SCORE_V2";
export type ITeamMode = "HEAD_TO_HEAD" | "TAG_COOP" | "TEAM_VS" | "TAG_VS";

export interface IRoom {
  id: string;
  name: string;
  room_id: string;
  room_size: number;
  bot_mode: IBotMode;
  play_mode: IPlayMode;
  score_mode: IScoreMode;
  team_mode: ITeamMode;
  is_configured: boolean;
  is_connected: boolean;
  is_created: boolean;
  beatmap: IBeatmap;
  skips: string[];
  users: string[];
}
