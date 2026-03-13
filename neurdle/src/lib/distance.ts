import type { Region, GuessResult, DistanceMap } from '@/types';

const MAX_BRAIN_DISTANCE = 170;

export function getGuessResult(
  guessRegion: Region,
  targetRegion: Region,
  distanceData: DistanceMap
): GuessResult {
  const isCorrect = guessRegion.id === targetRegion.id;

  if (isCorrect) {
    return { region: guessRegion, distance_mm: 0, proximity_pct: 100, direction: [], isCorrect: true };
  }

  const entry = distanceData[guessRegion.id]?.[targetRegion.id];

  let distance_mm: number;
  let direction: string[];

  if (entry) {
    distance_mm = entry.distance_mm;
  } else {
    const dx = targetRegion.centroid_mni[0] - guessRegion.centroid_mni[0];
    const dy = targetRegion.centroid_mni[1] - guessRegion.centroid_mni[1];
    const dz = targetRegion.centroid_mni[2] - guessRegion.centroid_mni[2];
    distance_mm = Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
  // Always compute directions from centroids so all 3 axes are shown
  direction = computeDirectionFromCentroids(guessRegion, targetRegion);

  const proximity_pct = Math.max(0, Math.round((1 - distance_mm / MAX_BRAIN_DISTANCE) * 100));

  return {
    region: guessRegion,
    distance_mm: Math.round(distance_mm * 10) / 10,
    proximity_pct,
    direction,
    isCorrect: false
  };
}

function computeDirectionFromCentroids(from: Region, to: Region): string[] {
  const delta = [
    to.centroid_mni[0] - from.centroid_mni[0],
    to.centroid_mni[1] - from.centroid_mni[1],
    to.centroid_mni[2] - from.centroid_mni[2],
  ];

  const directions: string[] = [];
  if (Math.abs(delta[1]) > 3) directions.push(delta[1] > 0 ? 'anterior' : 'posterior');
  if (Math.abs(delta[2]) > 3) directions.push(delta[2] > 0 ? 'superior' : 'inferior');
  if (Math.abs(delta[0]) > 3) {
    const toAbs = Math.abs(to.centroid_mni[0]);
    const fromAbs = Math.abs(from.centroid_mni[0]);
    directions.push(toAbs > fromAbs ? 'lateral' : 'medial');
  }

  const magnitudes: Record<string, number> = {
    anterior: delta[1] > 0 ? Math.abs(delta[1]) : 0,
    posterior: delta[1] < 0 ? Math.abs(delta[1]) : 0,
    superior: delta[2] > 0 ? Math.abs(delta[2]) : 0,
    inferior: delta[2] < 0 ? Math.abs(delta[2]) : 0,
    lateral: Math.abs(Math.abs(to.centroid_mni[0]) - Math.abs(from.centroid_mni[0])),
    medial: Math.abs(Math.abs(from.centroid_mni[0]) - Math.abs(to.centroid_mni[0])),
  };

  return directions
    .sort((a, b) => (magnitudes[b] ?? 0) - (magnitudes[a] ?? 0));
}
