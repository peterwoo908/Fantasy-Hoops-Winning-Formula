export type ProjectionRow = {
  Date: string;
  PLAYER_NAME: string;
  Team: string;
  Opp: string;
  Fantasy_Team?: string;
  Free_Agent?: boolean;
  Injury_Status?: string;
  Pred_MIN: number;
  Pred_FP: number;
  L3_FP_per_Min?: number;
  Opp_DefRtg?: number;
  Schedule_Rest?: number;
  Long_Absence_Flag?: number;
};

export type ApiResponse<T> = {
  file: string;
  rows: T[];
};