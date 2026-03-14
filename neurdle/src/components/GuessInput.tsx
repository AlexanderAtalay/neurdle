'use client';
import { useState, useEffect, useRef } from 'react';
import type { Region } from '@/types';

interface Props {
  regions: Region[];
  usedIds: Set<string>;
  disabled: boolean;
  onGuess: (region: Region) => void;
}

function matchesQuery(r: Region, q: string): boolean {
  if (!q) return true;
  const lower = q.toLowerCase();
  if (r.name.toLowerCase().includes(lower)) return true;
  if (r.id.toLowerCase().includes(lower)) return true;
  if (r.aliases.some(a => a.toLowerCase().includes(lower))) return true;
  return false;
}

export default function GuessInput({ regions, usedIds, disabled, onGuess }: Props) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [highlighted, setHighlighted] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const filtered = regions
    .filter(r => !usedIds.has(r.id))
    .filter(r => matchesQuery(r, query))
    .sort((a, b) => a.name.localeCompare(b.name));

  // Reset highlight when results change
  useEffect(() => { setHighlighted(0); }, [query]);

  // Scroll highlighted item into view
  useEffect(() => {
    if (!listRef.current) return;
    const item = listRef.current.children[highlighted] as HTMLElement | undefined;
    item?.scrollIntoView({ block: 'nearest' });
  }, [highlighted]);

  function selectRegion(region: Region) {
    onGuess(region);
    setQuery('');
    setOpen(false);
    inputRef.current?.focus();
  }

  function handleKey(e: React.KeyboardEvent) {
    if (!open) { if (e.key === 'ArrowDown' || e.key === 'Enter') setOpen(true); return; }
    if (e.key === 'ArrowDown') { setHighlighted(h => Math.min(h + 1, filtered.length - 1)); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { setHighlighted(h => Math.max(h - 1, 0)); e.preventDefault(); }
    else if (e.key === 'Enter') { if (filtered[highlighted]) selectRegion(filtered[highlighted]); }
    else if (e.key === 'Escape') { setOpen(false); }
  }

  const showDropdown = open && !disabled && filtered.length > 0;

  return (
    <div className="relative">
      <div className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onKeyDown={handleKey}
          disabled={disabled}
          placeholder={disabled ? 'Game over' : 'Type or browse brain regions…'}
          className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-[#e94560] disabled:opacity-40 disabled:cursor-not-allowed"
          autoComplete="off"
        />
        <button
          onMouseDown={e => e.preventDefault()}
          onClick={() => filtered[highlighted] && selectRegion(filtered[highlighted])}
          disabled={disabled || filtered.length === 0}
          className="px-5 py-2.5 bg-[#e94560] text-white rounded-lg font-medium hover:bg-[#c73450] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Guess
        </button>
      </div>

      {showDropdown && (
        <div className="absolute z-20 w-full mt-1 bg-[#1a1a2e] border border-white/20 rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-64">
          {query === '' && (
            <div className="px-3 py-1.5 text-xs text-gray-500 border-b border-white/10 flex-shrink-0">
              {filtered.length} regions: scroll or type to filter
            </div>
          )}
          <div ref={listRef} className="overflow-y-auto">
            {filtered.map((r, i) => (
              <button
                key={r.id}
                onMouseDown={e => e.preventDefault()}
                onClick={() => selectRegion(r)}
                className={`w-full text-left px-4 py-2.5 flex justify-between items-center transition-colors ${
                  i === highlighted ? 'bg-white/15' : 'hover:bg-white/10'
                }`}
              >
                <span className="text-white font-medium text-sm">
                  {r.name}
                  {r.hemisphere !== 'bilateral' && (
                    <span className="text-gray-400 text-xs ml-1">
                      ({r.hemisphere === 'left' ? 'L' : 'R'})
                    </span>
                  )}
                </span>
                <span className="text-gray-400 text-xs capitalize ml-2 shrink-0">
                  {r.lobe.replace(/_/g, ' ')}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
