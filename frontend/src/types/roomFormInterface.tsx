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
    length: [number, number];
    bpm: [number, number];
    rank_status: string[];
    force_stat: boolean;
  };
}
