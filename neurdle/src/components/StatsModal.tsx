'use client';
import { useGameStore } from '@/store/gameStore';

interface Props { onClose: () => void; }

export default function StatsModal({ onClose }: Props) {
  const { stats } = useGameStore();
  const winRate = stats.gamesPlayed ? Math.round(stats.gamesWon / stats.gamesPlayed * 100) : 0;
  const maxDist = Math.max(...stats.guessDistribution, 1);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a2e] rounded-2xl p-6 max-w-sm w-full border border-white/20 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Statistics</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
        </div>

        <div className="grid grid-cols-4 gap-3 mb-5 text-center">
          {[
            [stats.gamesPlayed, 'Played'],
            [winRate + '%', 'Win %'],
            [stats.currentStreak, 'Streak'],
            [stats.maxStreak, 'Best'],
          ].map(([val, label]) => (
            <div key={label as string}>
              <div className="text-2xl font-bold text-white">{val}</div>
              <div className="text-xs text-gray-400">{label}</div>
            </div>
          ))}
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-2">Guess Distribution</h3>
          <div className="space-y-1.5">
            {stats.guessDistribution.map((count, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-gray-400 w-4">{i + 1}</span>
                <div className="flex-1 h-5 bg-white/5 rounded overflow-hidden">
                  <div
                    className="h-full bg-[#e94560] rounded flex items-center justify-end pr-1.5 text-xs text-white font-medium transition-all"
                    style={{ width: count ? `${Math.max(10, (count / maxDist) * 100)}%` : '0%' }}
                  >
                    {count > 0 && count}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full py-2 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
