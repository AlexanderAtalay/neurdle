'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useGame } from '@/hooks/useGame';
import { useGameStore } from '@/store/gameStore';
import Header from '@/components/Header';
import DifficultySelector from '@/components/DifficultySelector';
import GuessInput from '@/components/GuessInput';
import GuessHistory from '@/components/GuessHistory';
import WinModal from '@/components/WinModal';

const BrainViewer = dynamic(() => import('@/components/BrainViewer'), { ssr: false });

export default function Home() {
  const game = useGame();
  const { mode, setMode } = useGameStore();
  const [showWinModal, setShowWinModal] = useState(false);

  useEffect(() => {
    if (game.gameOver && mode === 'daily') {
      const timer = setTimeout(() => setShowWinModal(true), 1500);
      return () => clearTimeout(timer);
    }
  }, [game.gameOver, mode]);

  const usedIds = new Set(game.guesses.map(g => g.region.id));
  const isTraining = mode === 'training';
  const trainingRevealed = isTraining && game.trainingRevealed;

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Header />

      <main className="flex-1 flex flex-col overflow-y-auto p-3 gap-2.5">
        {/* Mode toggle + difficulty */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-center gap-1.5">
            {(['daily', 'training'] as const).map(m => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-4 py-1 rounded-full text-sm font-medium border transition-colors capitalize ${
                  mode === m
                    ? 'border-[#e94560] text-[#e94560] bg-[#e94560]/10'
                    : 'border-gray-600 text-gray-400 hover:border-gray-400'
                }`}
              >
                {m === 'training' ? '🧪 Training' : '📅 Daily'}
              </button>
            ))}
          </div>
          <DifficultySelector />
        </div>

        {/* Training score banner */}
        {isTraining && (
          <div className="text-center text-xs text-gray-400">
            Score: <span className="text-[#16c79a] font-bold text-sm">{game.trainingScore}</span>
            {game.targetRegion && (
              <span className="ml-3">
                Ghost brain always visible · Wrong guesses shown in orange
              </span>
            )}
          </div>
        )}

        {/* 3D Viewer */}
        <div className="h-72 sm:h-80 flex-shrink-0">
          {game.targetRegion ? (
            <BrainViewer
              targetRegion={game.targetRegion}
              showGhostBrain={game.showGhostBrain}
              wrongGuessRegions={isTraining ? game.trainingWrongRegions : []}
            />
          ) : (
            <div className="w-full h-full rounded-xl bg-[#0d0d1a] flex items-center justify-center">
              <div className="text-gray-500 text-sm">Loading region…</div>
            </div>
          )}
        </div>

        {/* Guess dots (daily only) */}
        {!isTraining && (
          <div className="flex justify-center gap-1.5 flex-shrink-0">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full ${
                  i < game.guesses.length
                    ? game.guesses[i].isCorrect ? 'bg-[#16c79a]' : 'bg-[#e94560]'
                    : 'bg-white/20'
                }`}
              />
            ))}
          </div>
        )}

        {/* Training reveal banner */}
        {trainingRevealed && game.targetRegion && (
          <div className="flex-shrink-0 text-center px-3 py-2 rounded-lg bg-[#e94560]/20 border border-[#e94560]/40 text-sm">
            <span className="text-gray-400">The answer was </span>
            <span className="font-bold text-[#e94560]">{game.targetRegion.name}</span>
            <span className="text-gray-400"> — next region loading…</span>
          </div>
        )}

        {/* Guess input */}
        <div className="flex-shrink-0">
          <GuessInput
            regions={game.allRegions}
            difficulty={game.difficulty}
            usedIds={isTraining ? new Set(game.trainingGuesses.map(g => g.region.id)) : usedIds}
            disabled={(!isTraining && game.gameOver) || trainingRevealed}
            onGuess={game.submitGuess}
          />
        </div>

        {/* Guess history */}
        <div className="flex-shrink-0 pb-4">
          <GuessHistory guesses={game.guesses} />
        </div>
      </main>

      {showWinModal && <WinModal onClose={() => setShowWinModal(false)} />}
    </div>
  );
}
