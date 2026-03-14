import type { Region } from '@/types';

export function getDailyRegion(
  regions: Region[],
  difficulty: 'easy' | 'normal' | 'hard'
): Region {
  const today = new Date();
  const dateStr = `${today.getFullYear()}-${today.getMonth()}-${today.getDate()}`;
  const seed = hashCode(dateStr + difficulty);
  const filtered = regions.filter(r => r.difficulty === difficulty);
  return filtered[Math.abs(seed) % filtered.length];
}

export function getPuzzleNumber(): number {
  const epoch = new Date('2026-03-12').getTime();
  const now = new Date().getTime();
  return Math.floor((now - epoch) / (1000 * 60 * 60 * 24));
}

function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return hash;
}
