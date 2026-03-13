interface Props {
  pct: number;
}

export default function ProximityBar({ pct }: Props) {
  const color =
    pct >= 80 ? '#16c79a' :
    pct >= 60 ? '#a8d672' :
    pct >= 40 ? '#f5c842' :
    pct >= 20 ? '#f58042' :
    '#e94560';

  return (
    <div className="flex items-center gap-2 min-w-[100px]">
      <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-xs font-mono text-gray-300 w-8 text-right">{pct}%</span>
    </div>
  );
}
