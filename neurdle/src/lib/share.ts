import type { GameState } from '@/types';

export function generateShareText(state: GameState, puzzleNumber: number): string {
  const emoji = state.guesses.map(g => {
    if (g.isCorrect) return '🧠';
    if (g.proximity_pct >= 80) return '🟩';
    if (g.proximity_pct >= 60) return '🟨';
    if (g.proximity_pct >= 40) return '🟧';
    if (g.proximity_pct >= 20) return '🟥';
    return '⬛';
  });

  const result = state.won ? `${state.guesses.length}/6` : 'X/6';
  const diffEmoji = { easy: '🔵', medium: '🟡', hard: '🔴' }[state.difficulty];
  const diffName = { easy: 'Easy', medium: 'Medium', hard: 'Hard' }[state.difficulty];

  return `Neurdle #${puzzleNumber}\n${diffEmoji} ${diffName}\n${result}\n${emoji.join('')}\nneurdle.app`;
}
