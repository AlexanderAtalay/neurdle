export interface Region {
  id: string;
  name: string;
  hemisphere: 'left' | 'right' | 'bilateral';
  difficulty: 'easy' | 'medium' | 'hard';
  category: 'cortical' | 'subcortical';
  lobe: string;
  centroid_mni: [number, number, number];
  mesh_file: string;
  mesh_files?: string[];  // for bilateral regions, lists all hemisphere meshes
  brodmann?: string;
  description?: string;
  fun_fact?: string;
  aliases: string[];
}

export interface GuessResult {
  region: Region;
  distance_mm: number;
  proximity_pct: number;
  direction: string[];
  isCorrect: boolean;
}

export interface GameState {
  difficulty: 'easy' | 'medium' | 'hard';
  targetRegion: Region | null;
  guesses: GuessResult[];
  gameOver: boolean;
  won: boolean;
  showGhostBrain: boolean;
  maxGuesses: 6;
}

export interface PlayerStats {
  gamesPlayed: number;
  gamesWon: number;
  currentStreak: number;
  maxStreak: number;
  guessDistribution: number[];
}

export type DistanceEntry = { distance_mm: number; direction: string[] };
export type DistanceMap = Record<string, Record<string, DistanceEntry>>;
