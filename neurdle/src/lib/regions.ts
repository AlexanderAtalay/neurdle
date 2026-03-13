import type { Region } from '@/types';

let cachedRegions: Region[] | null = null;

export async function loadRegions(): Promise<Region[]> {
  if (cachedRegions) return cachedRegions;
  const res = await fetch('/data/regions.json');
  const data = await res.json();
  cachedRegions = data.regions as Region[];
  return cachedRegions;
}

export function searchRegions(query: string, regions: Region[]): Region[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];

  return regions.filter(r => {
    if (r.name.toLowerCase().includes(q)) return true;
    if (r.id.toLowerCase().includes(q)) return true;
    if (r.aliases.some(a => a.toLowerCase().includes(q))) return true;
    return false;
  }).slice(0, 8);
}
