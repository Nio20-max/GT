/* Shared TypeScript interfaces for Goal Tactics */

export interface User {
  id: string;
  username: string;
  email?: string;
  token: string;
}

export interface Club {
  id: string;
  name: string;
  logo?: string;
  level: number;
  reputation: number;
}

export interface Player {
  id: string;
  name: string;
  position: PlayerPosition;
  rating: number;
  age: number;
  stamina: number;
  skills: PlayerSkills;
}

export type PlayerPosition =
  | "GK"
  | "CB"
  | "LB"
  | "RB"
  | "CM"
  | "LM"
  | "RM"
  | "CAM"
  | "CDM"
  | "LW"
  | "RW"
  | "ST";

export interface PlayerSkills {
  speed: number;
  shooting: number;
  passing: number;
  defending: number;
  dribbling: number;
  physical: number;
}

export interface FinanceSummary {
  balance: number;
  income: number;
  expenses: number;
  currency: string;
}

export interface Stadium {
  id: string;
  name: string;
  capacity: number;
  level: number;
}

export interface LeagueStanding {
  rank: number;
  clubId: string;
  clubName: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  points: number;
}

export interface TransferListing {
  id: string;
  player: Player;
  askingPrice: number;
  listedAt: string;
}

export interface ChatMessage {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
}

export interface HudResources {
  medipacks: number;
  stars: number;
  money: number;
}
