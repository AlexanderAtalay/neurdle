'use client';
import { useGameStore } from '@/store/gameStore';

const DIFFICULTIES = [
  { value: 'easy', label: 'Easy', color: 'text-blue-400' },
  { value: 'normal', label: 'Normal', color: 'text-yellow-400' },
  { value: 'hard', label: 'Hard', color: 'text-red-400' },
] as const;

export default function DifficultySelector() {
  const { difficulty, setDifficulty } = useGameStore();

  function handleChange(d: 'easy' | 'normal' | 'hard') {
    if (d === difficulty) return;
    setDifficulty(d);
    // Game state per-difficulty is preserved automatically in the store
  }

  return (
    <div className="flex gap-2 justify-center">
      {DIFFICULTIES.map(({ value, label, color }) => (
        <button
          key={value}
          onClick={() => handleChange(value)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            difficulty === value
              ? `border-current ${color} bg-white/10`
              : 'border-gray-600 text-gray-400 hover:border-gray-400'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
