export interface Region {
  id: string;
  name: string;
  hemisphere: 'left' | 'right' | 'bilateral';
  difficulty: 'easy' | 'normal' | 'hard';
  category: 'cortical' | 'subcortical' | 'tract';
  lobe: string;
  centroid_mni: [number, number, number];
  lateral_extent_mm?: number;  // mean absolute x of hemisphere centroids; used for L/M direction
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
  difficulty: 'easy' | 'normal' | 'hard';
  targetRegion: Region | null;
  guesses: GuessResult[];
  gameOver: boolean;
  won: boolean;
  showGlassBrain: boolean;
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
