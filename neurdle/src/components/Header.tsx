'use client';
import { useState } from 'react';
import HelpModal from './HelpModal';
import StatsModal from './StatsModal';

export default function Header() {
  const [showHelp, setShowHelp] = useState(false);
  const [showStats, setShowStats] = useState(false);

  return (
    <>
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
        <button onClick={() => setShowHelp(true)} className="text-gray-400 hover:text-white text-xl w-8">?</button>
        <h1 className="text-2xl font-bold tracking-wide text-white">
          Neur<span className="text-[#e94560]">dle</span>
        </h1>
        <button onClick={() => setShowStats(true)} className="text-gray-400 hover:text-white w-8 flex items-center justify-center" aria-label="Statistics">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="10" width="3" height="7" rx="1" fill="currentColor"/>
            <rect x="6" y="6" width="3" height="11" rx="1" fill="currentColor"/>
            <rect x="11" y="2" width="3" height="15" rx="1" fill="currentColor"/>
            <rect x="16" y="8" width="1" height="1" rx="0.5" fill="currentColor"/>
          </svg>
        </button>
      </header>
      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
      {showStats && <StatsModal onClose={() => setShowStats(false)} />}
    </>
  );
}
