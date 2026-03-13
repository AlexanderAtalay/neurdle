import type { GuessResult } from '@/types';
import ProximityBar from './ProximityBar';
import DirectionIndicator from './DirectionIndicator';

interface Props {
  guesses: GuessResult[];
}

export default function GuessHistory({ guesses }: Props) {
  if (!guesses.length) return null;

  return (
    <div className="space-y-1.5">
      <div className="grid grid-cols-[1fr_auto_auto_auto] gap-2 px-2 text-xs text-gray-500 font-medium uppercase tracking-wide">
        <span>Region</span>
        <span>Distance</span>
        <span>Proximity</span>
        <span>Direction</span>
      </div>
      {guesses.map((g, i) => (
        <div
          key={i}
          className={`grid grid-cols-[1fr_auto_auto_auto] gap-2 items-center px-3 py-2 rounded-lg border transition-all ${
            g.isCorrect
              ? 'bg-[#16c79a]/20 border-[#16c79a]/50 text-[#16c79a]'
              : 'bg-white/5 border-white/10 text-white'
          }`}
        >
          <span className="font-medium text-sm truncate">
            {g.isCorrect && '✓ '}{g.region.name}
            {g.region.hemisphere !== 'bilateral' && (
              <span className="text-gray-400 text-xs ml-1">
                ({g.region.hemisphere === 'left' ? 'L' : 'R'})
              </span>
            )}
          </span>
          <span className="text-xs font-mono text-gray-300 whitespace-nowrap">
            {g.isCorrect ? '0 mm' : `${g.distance_mm} mm`}
          </span>
          <ProximityBar pct={g.proximity_pct} />
          <DirectionIndicator directions={g.direction} />
        </div>
      ))}
    </div>
  );
}
