import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Region, GuessResult, PlayerStats } from '@/types';

type DifficultyState = {
  targetRegion: Region | null;
  guesses: GuessResult[];
  gameOver: boolean;
  won: boolean;
  showGhostBrain: boolean;
  lastPlayedDate: string;
};

const defaultDiffState = (): DifficultyState => ({
  targetRegion: null,
  guesses: [],
  gameOver: false,
  won: false,
  showGhostBrain: false,
  lastPlayedDate: '',
});

const defaultStats: PlayerStats = {
  gamesPlayed: 0, gamesWon: 0,
  currentStreak: 0, maxStreak: 0,
  guessDistribution: [0, 0, 0, 0, 0, 0],
};

export type GameMode = 'daily' | 'training';

interface GameStore {
  difficulty: 'easy' | 'medium' | 'hard';
  mode: GameMode;
  dailyStates: Record<string, DifficultyState>;
  stats: PlayerStats;

  // Training state (not persisted across sessions)
  trainingTarget: Region | null;
  trainingGuesses: GuessResult[];
  trainingWrongRegions: Region[];
  trainingScore: number;

  // Daily game actions
  setDifficulty: (d: 'easy' | 'medium' | 'hard') => void;
  setMode: (m: GameMode) => void;
  setTargetRegion: (r: Region) => void;
  addGuess: (g: GuessResult) => void;
  resetGame: () => void;
  updateStats: (won: boolean, guessCount: number) => void;

  // Training actions
  setTrainingTarget: (r: Region) => void;
  addTrainingGuess: (g: GuessResult) => void;
  resetTraining: () => void;
}

export const useGameStore = create<GameStore>()(
  persist(
    (set, get) => ({
      difficulty: 'medium',
      mode: 'daily',
      dailyStates: {
        easy: defaultDiffState(),
        medium: defaultDiffState(),
        hard: defaultDiffState(),
      },
      stats: defaultStats,

      // Training state (reset on page load, not stored)
      trainingTarget: null,
      trainingGuesses: [],
      trainingWrongRegions: [],
      trainingScore: 0,

      setDifficulty: (difficulty) => set({ difficulty }),
      setMode: (mode) => set({ mode }),

      setTargetRegion: (targetRegion) => {
        const { difficulty, dailyStates } = get();
        set({
          dailyStates: {
            ...dailyStates,
            [difficulty]: { ...dailyStates[difficulty], targetRegion },
          },
        });
      },

      addGuess: (guess) => {
        const { difficulty, dailyStates } = get();
        const prev = dailyStates[difficulty];
        const newGuesses = [...prev.guesses, guess];
        const won = guess.isCorrect;
        const gameOver = won || newGuesses.length >= 6;
        const showGhostBrain = newGuesses.length >= 3;
        set({
          dailyStates: {
            ...dailyStates,
            [difficulty]: { ...prev, guesses: newGuesses, won, gameOver, showGhostBrain },
          },
        });
      },

      resetGame: () => {
        const { difficulty, dailyStates } = get();
        set({
          dailyStates: {
            ...dailyStates,
            [difficulty]: defaultDiffState(),
          },
        });
      },

      updateStats: (won, guessCount) => {
        const { stats } = get();
        const today = new Date().toDateString();
        const s = { ...stats };
        s.gamesPlayed += 1;
        if (won) {
          s.gamesWon += 1;
          s.currentStreak += 1;
          s.maxStreak = Math.max(s.maxStreak, s.currentStreak);
          s.guessDistribution = [...s.guessDistribution];
          s.guessDistribution[Math.min(guessCount - 1, 5)] += 1;
        } else {
          s.currentStreak = 0;
        }
        const { difficulty, dailyStates } = get();
        set({
          stats: s,
          dailyStates: {
            ...dailyStates,
            [difficulty]: { ...dailyStates[difficulty], lastPlayedDate: today },
          },
        });
      },

      // Training
      setTrainingTarget: (trainingTarget) =>
        set({ trainingTarget, trainingGuesses: [], trainingWrongRegions: [] }),

      addTrainingGuess: (guess) => {
        const { trainingGuesses, trainingWrongRegions, trainingScore } = get();
        const newGuesses = [...trainingGuesses, guess];
        const newWrong = guess.isCorrect
          ? trainingWrongRegions
          : [...trainingWrongRegions, guess.region];
        set({
          trainingGuesses: newGuesses,
          trainingWrongRegions: newWrong,
          trainingScore: guess.isCorrect ? trainingScore + 1 : trainingScore,
        });
      },

      resetTraining: () =>
        set({ trainingTarget: null, trainingGuesses: [], trainingWrongRegions: [], trainingScore: 0 }),
    }),
    {
      name: 'neurdle-storage',
      // Don't persist training state
      partialize: (state) => ({
        difficulty: state.difficulty,
        mode: state.mode,
        dailyStates: state.dailyStates,
        stats: state.stats,
      }),
    }
  )
);

// Selector helpers so components can read current daily state cleanly
export const useDailyState = () => {
  const { difficulty, dailyStates } = useGameStore();
  return dailyStates[difficulty] ?? defaultDiffState();
};
