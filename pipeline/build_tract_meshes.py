"""
build_tract_meshes.py

Converts HCP1065 average tractography TRK files into GLB tube meshes for Neurdle.

Pipeline per tract:
  1. Load streamlines (nibabel)
  2. QuickBundles clustering → representative streamlines
  3. Resample each representative to uniform point count
  4. Build tube mesh (parallel-transport framing, end-capped)
  5. Combine L+R hemispheres into one mesh scene
  6. Export as GLB → neurdle/public/meshes/tracts/

Run from the pipeline/ directory:
  python build_tract_meshes.py

Prints JSON region entries to stdout for appending to regions.json.
"""

import json
import os
import sys

import nibabel as nib
import numpy as np
import trimesh
from dipy.segment.clustering import QuickBundles
from dipy.segment.featurespeed import ResampleFeature
from dipy.segment.metric import AveragePointwiseEuclideanMetric

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
TRACTS_DIR = "../tractography_tmp/hcp1065_avg_tracts/trk"
OUT_DIR = "../neurdle/public/meshes/tracts"

# ---------------------------------------------------------------------------
# Tract definitions
# ---------------------------------------------------------------------------
# Each entry:
#   id, name, difficulty, lobe,
#   files: list of (subdir, stem) — L before R where applicable
#   aliases, description, fun_fact
#
# Commissural tracts are treated as a single bilateral object (one file).
# Association/projection tracts produce separate _L/_R GLBs (mesh_files pattern).
# ---------------------------------------------------------------------------
TRACTS = [
    # ── Commissural ──────────────────────────────────────────────────────────
    dict(
        id="corpus_callosum",
        name="Corpus Callosum",
        difficulty="medium",
        lobe="commissural",
        files=[("commissural", "CC")],
        bilateral_single=True,  # one GLB, no L/R split
        n_reps=80,  # complex fan needs many spatially diverse reps
        cc_sampling=True,  # use midpoint-FPS instead of top-N-by-size
        aliases=["CC", "callosum"],
        description="The largest white matter commissure, connecting homologous regions across both cerebral hemispheres.",
        fun_fact="The corpus callosum contains ~200 million axons — more than any other white matter tract.",
    ),
    dict(
        id="anterior_commissure",
        name="Anterior Commissure",
        difficulty="hard",
        lobe="commissural",
        files=[("commissural", "AC")],
        bilateral_single=True,
        n_reps=40,
        aliases=["AC"],
        description="A small commissure crossing the midline, connecting the olfactory regions and anterior temporal lobes.",
        fun_fact="The anterior commissure is phylogenetically ancient and present in all mammalian brains.",
    ),
    # ── Association ──────────────────────────────────────────────────────────
    dict(
        id="arcuate_fasciculus",
        name="Arcuate Fasciculus",
        difficulty="medium",
        lobe="association",
        files=[("association", "AF_L"), ("association", "AF_R")],
        bilateral_single=False,
        n_reps=70,
        aliases=["AF", "superior longitudinal fasciculus (language)"],
        description="Connects Broca's area in the frontal lobe to Wernicke's area in the temporal lobe, forming the core language circuit.",
        fun_fact="Damage to the arcuate fasciculus causes conduction aphasia — the inability to repeat words despite intact comprehension and production.",
    ),
    dict(
        id="slf",
        name="Superior Longitudinal Fasciculus",
        difficulty="medium",
        lobe="association",
        files=[("association", "SLF2_L"), ("association", "SLF2_R")],
        bilateral_single=False,
        n_reps=65,
        aliases=["SLF", "SLF II", "SLF2"],
        description="Connects parietal and frontal lobes, running along the dorsolateral convexity. Key for spatial attention and working memory.",
        fun_fact="There are three distinct SLF branches (I, II, III) that connect different parietal and frontal regions.",
    ),
    dict(
        id="ifof",
        name="Inferior Fronto-Occipital Fasciculus",
        difficulty="hard",
        lobe="association",
        files=[("association", "IFOF_L"), ("association", "IFOF_R")],
        bilateral_single=False,
        n_reps=65,
        aliases=["IFOF", "fronto-occipital fasciculus"],
        description="A long tract running beneath the insula, connecting frontal lobe to occipital and temporal regions.",
        fun_fact="The IFOF is thought to be involved in semantic processing and visual attention.",
    ),
    dict(
        id="ilf",
        name="Inferior Longitudinal Fasciculus",
        difficulty="hard",
        lobe="association",
        files=[("association", "ILF_L"), ("association", "ILF_R")],
        bilateral_single=False,
        n_reps=65,
        aliases=["ILF"],
        description="Connects temporal pole to occipital cortex along the ventral stream, supporting visual recognition and memory.",
        fun_fact="The ILF is a key tract for face recognition — damage causes prosopagnosia.",
    ),
    dict(
        id="uncinate_fasciculus",
        name="Uncinate Fasciculus",
        difficulty="hard",
        lobe="association",
        files=[("association", "UF_L"), ("association", "UF_R")],
        bilateral_single=False,
        n_reps=50,
        aliases=["UF", "uncinate"],
        description="Hooks around the Sylvian fissure, connecting orbitofrontal cortex to anterior temporal lobe.",
        fun_fact="The uncinate fasciculus is one of the last tracts to mature — development continues into the third decade of life.",
    ),
    dict(
        id="vof",
        name="Vertical Occipital Fasciculus",
        difficulty="hard",
        lobe="association",
        files=[("association", "VOF_L"), ("association", "VOF_R")],
        bilateral_single=False,
        n_reps=25,
        aliases=["VOF", "Wernicke's perpendicular fasciculus"],
        description="A short vertical tract in the posterior brain connecting dorsal and ventral occipital cortex.",
        fun_fact="First described by Wernicke in 1881, the VOF was largely forgotten for over a century before being rediscovered by diffusion MRI.",
    ),
    # ── Projection ───────────────────────────────────────────────────────────
    dict(
        id="corticospinal_tract",
        name="Corticospinal Tract",
        difficulty="medium",
        lobe="projection",
        files=[("projection", "CST_L"), ("projection", "CST_R")],
        bilateral_single=False,
        n_reps=50,
        aliases=["CST", "pyramidal tract"],
        description="Descends from motor cortex through the internal capsule and brainstem to the spinal cord, carrying voluntary motor commands.",
        fun_fact="The CST decussates (crosses) in the medullary pyramids — the left motor cortex controls the right side of the body.",
    ),
    dict(
        id="optic_radiation",
        name="Optic Radiation",
        difficulty="hard",
        lobe="projection",
        files=[("projection", "OR_L"), ("projection", "OR_R")],
        bilateral_single=False,
        n_reps=30,
        aliases=["OR", "optic radiations", "geniculocalcarine tract"],
        description="Carries visual signals from the lateral geniculate nucleus of the thalamus to primary visual cortex.",
        fun_fact="Meyer's loop — the anterior bend of the optic radiation — sweeps through the temporal lobe. Temporal lobe surgery can cause a 'pie-in-the-sky' visual field defect.",
    ),
]


# ---------------------------------------------------------------------------
# Geometry utilities
# ---------------------------------------------------------------------------

def resample_streamline(pts: np.ndarray, n: int) -> np.ndarray:
    """Resample a streamline to exactly n equidistant points."""
    pts = np.asarray(pts, dtype=float)
    diffs = np.diff(pts, axis=0)
    seg_lens = np.linalg.norm(diffs, axis=1)
    cumdist = np.concatenate([[0.0], np.cumsum(seg_lens)])
    total = cumdist[-1]
    if total < 1e-6:
        return np.tile(pts[0], (n, 1))
    targets = np.linspace(0.0, total, n)
    return np.column_stack([
        np.interp(targets, cumdist, pts[:, dim]) for dim in range(3)
    ])


def streamline_to_tube(
    pts: np.ndarray,
    radius: float = 2.0,
    n_sides: int = 6,
) -> trimesh.Trimesh:
    """
    Convert an Nx3 polyline to a capped tube mesh using parallel transport.
    n_sides=6 (hexagonal cross-section) keeps poly count low.
    """
    pts = np.asarray(pts, dtype=float)
    n = len(pts)

    # Tangent vectors (central differences, forward/backward at endpoints)
    tangents = np.empty_like(pts)
    tangents[1:-1] = pts[2:] - pts[:-2]
    tangents[0] = pts[1] - pts[0]
    tangents[-1] = pts[-1] - pts[-2]
    norms = np.linalg.norm(tangents, axis=1, keepdims=True)
    norms[norms < 1e-8] = 1.0
    tangents /= norms

    # Initial normal (Gram-Schmidt against first tangent)
    t0 = tangents[0]
    helper = np.array([1.0, 0.0, 0.0]) if abs(t0[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    normal = helper - np.dot(helper, t0) * t0
    normal /= np.linalg.norm(normal)
    binormal = np.cross(t0, normal)
    binormal /= np.linalg.norm(binormal)

    ring_angles = np.linspace(0.0, 2.0 * np.pi, n_sides, endpoint=False)

    all_rings = []
    for i in range(n):
        t = tangents[i]
        if i > 0:
            # Parallel-transport the frame
            axis = np.cross(tangents[i - 1], t)
            axis_len = np.linalg.norm(axis)
            if axis_len > 1e-6:
                axis /= axis_len
                cos_a = np.clip(np.dot(tangents[i - 1], t), -1.0, 1.0)
                sin_a = np.sqrt(max(0.0, 1.0 - cos_a * cos_a))
                # Rodrigues rotation of normal and binormal
                def rodrigues(v, k, c, s):
                    return v * c + np.cross(k, v) * s + k * np.dot(k, v) * (1.0 - c)
                normal = rodrigues(normal, axis, cos_a, sin_a)
                normal /= np.linalg.norm(normal)
                binormal = np.cross(t, normal)
                binormal /= np.linalg.norm(binormal)

        ring = pts[i] + radius * (
            np.outer(np.cos(ring_angles), normal) +
            np.outer(np.sin(ring_angles), binormal)
        )
        all_rings.append(ring)

    # Flatten vertex array: shape (n * n_sides, 3)
    verts = np.array(all_rings).reshape(-1, 3)
    faces = []

    # Side quads → 2 triangles each
    for i in range(n - 1):
        for j in range(n_sides):
            j2 = (j + 1) % n_sides
            a = i * n_sides + j
            b = i * n_sides + j2
            c = (i + 1) * n_sides + j
            d = (i + 1) * n_sides + j2
            faces.append([a, c, b])
            faces.append([b, c, d])

    return trimesh.Trimesh(
        vertices=verts,
        faces=np.array(faces, dtype=np.int32),
        process=False,
    )


# ---------------------------------------------------------------------------
# Tractography utilities
# ---------------------------------------------------------------------------

def load_streamlines(category: str, stem: str) -> list:
    path = os.path.join(TRACTS_DIR, category, f"{stem}.trk.gz")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Not found: {path}")
    trk = nib.streamlines.load(path)
    return list(trk.streamlines)


def _fps(positions: np.ndarray, n: int) -> list[int]:
    """Greedy farthest-point sampling — returns n indices into positions."""
    if len(positions) <= n:
        return list(range(len(positions)))
    chosen = [int(np.argmin(np.linalg.norm(positions - positions.mean(axis=0), axis=1)))]
    dists = np.linalg.norm(positions - positions[chosen[0]], axis=1)
    for _ in range(n - 1):
        nxt = int(np.argmax(dists))
        chosen.append(nxt)
        dists = np.minimum(dists, np.linalg.norm(positions - positions[nxt], axis=1))
    return chosen


def get_representatives(
    streamlines: list,
    n_reps: int,
    n_points: int = 25,
    cc_sampling: bool = False,
) -> list:
    """
    QuickBundles clustering (5mm threshold) → n_reps representative streamlines.

    For most tracts: top-N clusters by size.
    For CC (cc_sampling=True): farthest-point sampling on cluster midpoints,
    which captures the full callosal fan rather than biasing toward the dense trunk.
    """
    if len(streamlines) > 5000:
        idx = np.random.default_rng(42).choice(len(streamlines), 5000, replace=False)
        streamlines = [streamlines[i] for i in idx]

    feature = ResampleFeature(nb_points=n_points)
    metric = AveragePointwiseEuclideanMetric(feature)
    qb = QuickBundles(threshold=3.0, metric=metric)
    clusters = qb.cluster(streamlines)

    centroids = [np.array(c.centroid) for c in clusters]

    if cc_sampling:
        # FPS on YZ midpoints — where callosal fibers cross the midline.
        # This ensures coverage of the full anterior-posterior and
        # superior-inferior extent of the fan, not just the dense trunk.
        midpoints = np.array([c[len(c) // 2, 1:] for c in centroids])  # (N, 2) YZ only
        chosen_idx = _fps(midpoints, n_reps)
    else:
        # Top-N by cluster size — works well for non-commissural tracts
        order = sorted(range(len(clusters)), key=lambda i: len(clusters[i]), reverse=True)
        chosen_idx = order[:n_reps]

    return [resample_streamline(centroids[i], n_points) for i in chosen_idx]


def compute_centroid_mni(all_streamlines: list) -> list[float]:
    """Mean position across all streamline points (sampled for speed)."""
    sample = all_streamlines[::max(1, len(all_streamlines) // 500)]
    pts = np.concatenate([np.array(s) for s in sample])
    mean = pts.mean(axis=0)
    # Zero X for bilateral centroid (matches convention in build_regions_json.py)
    return [0.0, round(float(mean[1]), 1), round(float(mean[2]), 1)]


def compute_lateral_extent(all_streamlines: list) -> float:
    """Mean absolute X across all streamline points."""
    sample = all_streamlines[::max(1, len(all_streamlines) // 500)]
    pts = np.concatenate([np.array(s) for s in sample])
    return round(float(np.abs(pts[:, 0]).mean()), 1)


# ---------------------------------------------------------------------------
# Main build loop
# ---------------------------------------------------------------------------

def build_tract(tract: dict) -> dict | None:
    tid = tract["id"]
    tname = tract["name"]
    bilateral_single = tract.get("bilateral_single", False)
    n_reps = tract.get("n_reps", 12)
    files = tract["files"]  # list of (subdir, stem)

    print(f"\n{'─'*60}")
    print(f"  {tname}")

    tube_radius = 0.35  # mm — thin fiber strands, dense enough to form a bundle
    tube_sides = 5      # pentagonal — slightly lower poly, barely noticeable at this radius
    n_pts = 25          # points per representative streamline

    os.makedirs(OUT_DIR, exist_ok=True)

    all_meshes_per_file = {}  # stem → trimesh.Trimesh

    all_streamlines_combined = []

    for subdir, stem in files:
        print(f"    loading {stem}...", end=" ", flush=True)
        streamlines = load_streamlines(subdir, stem)
        print(f"{len(streamlines)} streamlines")
        all_streamlines_combined.extend(streamlines)

        reps = get_representatives(streamlines, n_reps=n_reps, n_points=n_pts,
                                   cc_sampling=tract.get("cc_sampling", False))
        print(f"    → {len(reps)} representatives")

        tubes = [streamline_to_tube(r, radius=tube_radius, n_sides=tube_sides) for r in reps]
        merged = trimesh.util.concatenate(tubes)
        all_meshes_per_file[stem] = merged

    # Centroid and lateral extent (computed from all streamlines)
    centroid_mni = compute_centroid_mni(all_streamlines_combined)
    lat_ext = compute_lateral_extent(all_streamlines_combined)

    if bilateral_single:
        # Single GLB combining all files (e.g., CC, AC which have no L/R split)
        combined = trimesh.util.concatenate(list(all_meshes_per_file.values()))
        glb_name = f"{tid}.glb"
        out_path = os.path.join(OUT_DIR, glb_name)
        combined.export(out_path)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"    → tracts/{glb_name}  ({size_kb:.1f} KB, {len(combined.faces)} faces)")

        mesh_file = f"tracts/{glb_name}"
        mesh_files = [mesh_file]
    else:
        # Separate L and R GLBs (AF_L / AF_R, etc.) — mirrors existing mesh_files pattern
        mesh_files = []
        mesh_file = None
        for subdir, stem in files:
            glb_name = f"{stem}.glb"
            out_path = os.path.join(OUT_DIR, glb_name)
            all_meshes_per_file[stem].export(out_path)
            size_kb = os.path.getsize(out_path) / 1024
            print(f"    → tracts/{glb_name}  ({size_kb:.1f} KB, {len(all_meshes_per_file[stem].faces)} faces)")
            mesh_files.append(f"tracts/{glb_name}")
        mesh_file = mesh_files[0]

    region_entry = {
        "id": tid,
        "name": tname,
        "hemisphere": "bilateral",
        "difficulty": tract["difficulty"],
        "category": "tract",
        "lobe": tract["lobe"],
        "centroid_mni": centroid_mni,
        "lateral_extent_mm": lat_ext,
        "mesh_file": mesh_file,
        "mesh_files": mesh_files,
        "aliases": tract["aliases"],
        "description": tract["description"],
        "fun_fact": tract["fun_fact"],
    }
    return region_entry


def main():
    print(f"Output directory: {OUT_DIR}")
    os.makedirs(OUT_DIR, exist_ok=True)

    region_entries = []
    failed = []

    for tract in TRACTS:
        try:
            entry = build_tract(tract)
            if entry:
                region_entries.append(entry)
        except Exception as e:
            print(f"  ERROR on {tract['id']}: {e}", file=sys.stderr)
            failed.append(tract["id"])

    print(f"\n{'='*60}")
    print(f"Built {len(region_entries)} tracts, {len(failed)} failed")
    if failed:
        print(f"  Failed: {failed}")

    # Print JSON entries for manual append to regions.json
    print(f"\n{'─'*60}")
    print("Region JSON entries (append to regions.json):")
    print("─" * 60)
    print(json.dumps(region_entries, indent=2))

    # Summary by difficulty
    by_diff = {}
    for e in region_entries:
        by_diff.setdefault(e["difficulty"], []).append(e["id"])
    for d, ids in sorted(by_diff.items()):
        print(f"\n  {d}: {ids}")


if __name__ == "__main__":
    main()
