'use client';
import { useGameStore } from '@/store/gameStore';
import { generateShareText } from '@/lib/share';
import { getPuzzleNumber } from '@/lib/daily';

interface Props { onClose: () => void; }

export default function WinModal({ onClose }: Props) {
  const store = useGameStore();
  const puzzleNum = getPuzzleNumber();

  const dailyState = store.dailyStates[store.difficulty];
  const { targetRegion, guesses, gameOver, won, showGlassBrain } = dailyState ?? {};

  function handleShare() {
    const text = generateShareText(
      {
        difficulty: store.difficulty,
        targetRegion: targetRegion ?? null,
        guesses: guesses ?? [],
        gameOver: gameOver ?? false,
        won: won ?? false,
        showGlassBrain: showGlassBrain ?? false,
        maxGuesses: 6,
      },
      puzzleNum
    );
    navigator.clipboard.writeText(text).then(() => alert('Copied to clipboard!'));
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a2e] rounded-2xl p-6 max-w-sm w-full border border-white/20 shadow-2xl">
        <div className="text-center mb-4">
          <div className="text-5xl mb-2">{won ? '🧠' : '💔'}</div>
          <h2 className="text-2xl font-bold text-white">
            {won ? 'Correct!' : 'Game Over'}
          </h2>
          {targetRegion && (
            <p className="text-gray-300 mt-1">
              The answer was{' '}
              <span className="text-[#e94560] font-semibold">{targetRegion.name}</span>
            </p>
          )}
        </div>

        <div className="bg-white/5 rounded-lg p-4 mb-4 text-center">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-white">{store.stats.gamesPlayed}</div>
              <div className="text-xs text-gray-400">Played</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {store.stats.gamesPlayed
                  ? Math.round(store.stats.gamesWon / store.stats.gamesPlayed * 100)
                  : 0}%
              </div>
              <div className="text-xs text-gray-400">Win rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{store.stats.currentStreak}</div>
              <div className="text-xs text-gray-400">Streak</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{store.stats.maxStreak}</div>
              <div className="text-xs text-gray-400">Best streak</div>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleShare}
            className="flex-1 py-2.5 bg-[#e94560] text-white rounded-lg font-medium hover:bg-[#c73450] transition-colors"
          >
            Share
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
