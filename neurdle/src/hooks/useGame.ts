'use client';
import { useEffect, useRef, useCallback } from 'react';
import { useGameStore } from '@/store/gameStore';
import { loadRegions } from '@/lib/regions';
import { getDailyRegion } from '@/lib/daily';
import { getGuessResult } from '@/lib/distance';
import type { Region, DistanceMap } from '@/types';

// Module-level cache so distances are only fetched once
let cachedDistances: DistanceMap | null = null;
async function loadDistances(): Promise<DistanceMap> {
  if (cachedDistances) return cachedDistances;
  const res = await fetch('/data/distances_bilateral.json');
  cachedDistances = await res.json();
  return cachedDistances!;
}

function getRandomRegion(regions: Region[], difficulty: string, excludeId?: string): Region {
  const pool = regions.filter(r => r.difficulty === difficulty && r.id !== excludeId);
  return pool[Math.floor(Math.random() * pool.length)];
}

export function useGame() {
  const store = useGameStore();
  const distanceData = useRef<DistanceMap>({});
  const allRegions = useRef<Region[]>([]);

  const currentDailyState = store.dailyStates[store.difficulty] ?? {
    targetRegion: null, guesses: [], gameOver: false, won: false,
    showGhostBrain: false, lastPlayedDate: '',
  };

  useEffect(() => {
    let cancelled = false;
    async function init() {
      const [regions, distances] = await Promise.all([loadRegions(), loadDistances()]);
      if (cancelled) return;
      allRegions.current = regions;
      distanceData.current = distances;

      // Daily puzzle: only set if not already set for today
      const today = new Date().toDateString();
      if (store.mode === 'daily') {
        if (!currentDailyState.targetRegion || currentDailyState.lastPlayedDate !== today) {
          const target = getDailyRegion(regions, store.difficulty);
          store.setTargetRegion(target);
        }
      }

      // Training: always pick a new target for the current difficulty
      if (store.mode === 'training') {
        store.setTrainingTarget(getRandomRegion(regions, store.difficulty));
      }
    }
    init();
    return () => { cancelled = true; };
  }, [store.difficulty, store.mode]); // eslint-disable-line react-hooks/exhaustive-deps

  // When switching to training mode, ensure a target is set
  useEffect(() => {
    if (store.mode === 'training' && !store.trainingTarget && allRegions.current.length > 0) {
      store.setTrainingTarget(getRandomRegion(allRegions.current, store.difficulty));
    }
  }, [store.mode, store.trainingTarget, store.difficulty]); // eslint-disable-line react-hooks/exhaustive-deps

  const submitGuess = useCallback((region: Region) => {
    if (!store.trainingTarget && store.mode === 'training') return;

    if (store.mode === 'daily') {
      if (currentDailyState.gameOver || !currentDailyState.targetRegion) return;
      if (currentDailyState.guesses.some(g => g.region.id === region.id)) return;

      const result = getGuessResult(region, currentDailyState.targetRegion, distanceData.current);
      store.addGuess(result);

      if (result.isCorrect || currentDailyState.guesses.length + 1 >= 6) {
        store.updateStats(result.isCorrect, currentDailyState.guesses.length + 1);
      }
    } else {
      // Training mode
      if (!store.trainingTarget) return;
      if (store.trainingGuesses.some(g => g.region.id === region.id)) return;

      const result = getGuessResult(region, store.trainingTarget, distanceData.current);
      store.addTrainingGuess(result);

      // Advance to next region after correct guess
      if (result.isCorrect) {
        setTimeout(() => {
          const next = getRandomRegion(allRegions.current, store.difficulty, store.trainingTarget?.id);
          store.setTrainingTarget(next);
        }, 1500);
      }
    }
  }, [store, currentDailyState]); // eslint-disable-line react-hooks/exhaustive-deps

  const targetRegion = store.mode === 'daily'
    ? currentDailyState.targetRegion
    : store.trainingTarget;

  const guesses = store.mode === 'daily'
    ? currentDailyState.guesses
    : store.trainingGuesses;

  const gameOver = store.mode === 'daily' ? currentDailyState.gameOver : false;
  const won = store.mode === 'daily' ? currentDailyState.won : false;
  const showGhostBrain = store.mode === 'training'
    ? true
    : currentDailyState.showGhostBrain;

  return {
    difficulty: store.difficulty,
    mode: store.mode,
    targetRegion,
    guesses,
    gameOver,
    won,
    showGhostBrain,
    stats: store.stats,
    trainingScore: store.trainingScore,
    trainingGuesses: store.trainingGuesses,
    trainingWrongRegions: store.trainingWrongRegions,
    allRegions: allRegions.current,
    submitGuess,
  };
}
