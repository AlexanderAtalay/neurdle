// Compact directional clues: arrow + 1–2 letter axis abbreviation
// Axes: A/P (anterior/posterior), S/I (superior/inferior), L/M (lateral/medial)
const DIR_CONFIG: Record<string, { arrow: string; abbr: string; label: string; color: string }> = {
  anterior:  { arrow: '↑', abbr: 'A',  label: 'Anterior',  color: 'text-blue-300   bg-blue-300/10   border-blue-300/30'   },
  posterior: { arrow: '↓', abbr: 'P',  label: 'Posterior', color: 'text-orange-300 bg-orange-300/10 border-orange-300/30' },
  superior:  { arrow: '↑', abbr: 'S',  label: 'Superior',  color: 'text-purple-300 bg-purple-300/10 border-purple-300/30' },
  inferior:  { arrow: '↓', abbr: 'I',  label: 'Inferior',  color: 'text-green-300  bg-green-300/10  border-green-300/30'  },
  lateral:   { arrow: '←→', abbr: 'L',  label: 'Lateral',   color: 'text-yellow-300 bg-yellow-300/10 border-yellow-300/30' },
  medial:    { arrow: '→←', abbr: 'M',  label: 'Medial',    color: 'text-pink-300   bg-pink-300/10   border-pink-300/30'   },
};

interface Props {
  directions: string[];
  distanceMm?: number;
}

export default function DirectionIndicator({ directions, distanceMm }: Props) {
  if (!directions.length) return null;

  return (
    <div className="flex gap-1 items-center flex-wrap">
      {directions.map(d => {
        const cfg = DIR_CONFIG[d];
        if (!cfg) return null;
        return (
          <span
            key={d}
            title={cfg.label}
            className={`inline-flex items-center gap-0.5 text-xs font-bold px-1.5 py-0.5 rounded border ${cfg.color}`}
          >
            <span>{cfg.arrow}</span>
            <span>{cfg.abbr}</span>
          </span>
        );
      })}
    </div>
  );
}
