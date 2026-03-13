"""
merge_bilateral_distances.py
Converts the L/R hemisphere distance maps into bilateral region maps
to match the bilateral region IDs in regions.json.
For each bilateral pair A→B, takes the minimum distance from {A_L,A_R} to {B_L,B_R}.
"""
import json
import os

def strip_hemi(name):
    """'hippocampus_L' -> 'hippocampus', 'precentral_R' -> 'precentral'"""
    if name.endswith('_L') or name.endswith('_R'):
        return name[:-2]
    return name

def merge_distances(input_files, output_file):
    # Load and merge all input distance maps
    raw = {}
    for f in input_files:
        if os.path.exists(f):
            data = json.load(open(f))
            raw.update(data)

    # Get all unique bilateral IDs
    bilateral_ids = set(strip_hemi(k) for k in raw.keys())

    bilateral = {}
    for id_a in bilateral_ids:
        # Get all L/R variants of A
        variants_a = [k for k in raw if strip_hemi(k) == id_a]
        bilateral[id_a] = {}

        for id_b in bilateral_ids:
            if id_a == id_b:
                continue
            variants_b = [k for k in raw if strip_hemi(k) == id_b]

            # Collect all distances between any variant of A and any variant of B
            candidates = []
            for va in variants_a:
                for vb in variants_b:
                    entry = raw.get(va, {}).get(vb)
                    if entry:
                        candidates.append(entry)

            if not candidates:
                continue

            # Use the minimum distance pair
            best = min(candidates, key=lambda e: e['distance_mm'])
            bilateral[id_a][id_b] = best

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(bilateral, f, indent=2)
    print(f"Saved {output_file} ({len(bilateral)} regions)")


# Medium: cortical + subcortical combined
merge_distances(
    ['data/distances_medium.json', 'data/distances_subcortical.json'],
    'data/distances_bilateral.json'
)
