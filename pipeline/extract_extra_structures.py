"""
extract_extra_structures.py
Extracts corpus callosum and ventricular system from FreeSurfer aseg segmentation.
Outputs GLB meshes directly to the public meshes/medium directory.

New structures:
  - Corpus Callosum        (aseg labels 251–255 combined)
  - Lateral Ventricles     (aseg labels 4 / 43, bilateral)
  - 3rd Ventricle          (aseg label 14)
  - 4th Ventricle          (aseg label 15)

Run from the pipeline/ directory:
  python extract_extra_structures.py

Prints per-structure centroid MNI coordinates to paste into build_regions_json.py.
"""

import numpy as np
import nibabel as nib
from scipy import ndimage
import trimesh
from skimage import measure
import os
import json

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')
OUTPUT_DIR = 'neurdle/public/meshes/medium'   # run from repo root

# aseg label definitions
CORPUS_CALLOSUM_LABELS = [251, 252, 253, 254, 255]   # posterior → anterior
STRUCTURES = {
    # name → (label_id_or_list_of_ids, max_faces, sigma, smooth_iters)
    'corpus_callosum':       (CORPUS_CALLOSUM_LABELS, 4000, 1.0, 10),
    'lateral_ventricle_L':   (4,  3000, 0.8, 8),
    'lateral_ventricle_R':   (43, 3000, 0.8, 8),
    'third_ventricle':       (14, 2000, 0.8, 8),
    'fourth_ventricle':      (15, 2000, 0.8, 8),
}


def build_mask(aseg_data, label_ids):
    """Binary mask for one or more aseg label IDs."""
    if isinstance(label_ids, int):
        return aseg_data == label_ids
    mask = np.zeros_like(aseg_data, dtype=bool)
    for lbl in label_ids:
        mask |= (aseg_data == lbl)
    return mask


def extract_mesh(mask_bool, affine, name, max_faces, sigma, smooth_iters):
    """Smooth → marching cubes → RAS transform → Laplacian smooth → decimate → subdivide."""
    mask_f = ndimage.gaussian_filter(mask_bool.astype(np.float32), sigma=sigma)

    try:
        verts, faces, _, _ = measure.marching_cubes(mask_f, level=0.5, spacing=(1, 1, 1))
    except ValueError:
        print(f"  Warning: marching_cubes failed for {name}")
        return None

    # Voxel indices → FreeSurfer RAS (MNI for fsaverage)
    verts_h = np.column_stack([verts, np.ones(len(verts))])
    verts_ras = (affine @ verts_h.T).T[:, :3]

    mesh = trimesh.Trimesh(vertices=verts_ras, faces=faces)
    trimesh.smoothing.filter_laplacian(mesh, iterations=smooth_iters)

    if len(mesh.faces) > max_faces:
        mesh = mesh.simplify_quadric_decimation(face_count=max_faces)
    mesh = mesh.subdivide()

    return mesh


def compute_centroid(mesh):
    c = mesh.vertices.mean(axis=0)
    c[0] = 0.0   # force X=0 for bilateral/midline structures
    return [round(float(v), 1) for v in c]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    aseg_path = os.path.join(FSAVERAGE, 'mri', 'aseg.mgz')
    print(f"Loading {aseg_path} ...")
    aseg_img = nib.load(aseg_path)
    aseg_data = aseg_img.get_fdata()
    affine = aseg_img.affine

    metadata = {}

    for name, (label_ids, max_faces, sigma, smooth_iters) in STRUCTURES.items():
        mask = build_mask(aseg_data, label_ids)
        nvox = int(mask.sum())
        if nvox == 0:
            print(f"\nSkipping {name}: no voxels found in aseg")
            continue

        print(f"\nExtracting {name}  ({nvox} voxels) ...")
        mesh = extract_mesh(mask, affine, name, max_faces, sigma, smooth_iters)
        if mesh is None:
            continue

        out_path = os.path.join(OUTPUT_DIR, f'{name}.glb')
        mesh.export(out_path)

        centroid = compute_centroid(mesh)
        metadata[name] = {
            'centroid_mni': centroid,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
        }
        print(f"  → {out_path}")
        print(f"     centroid_mni = {centroid}")
        print(f"     mesh: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")

    print("\n" + "=" * 60)
    print("Paste these centroid_mni values into build_regions_json.py:")
    print(json.dumps({k: v['centroid_mni'] for k, v in metadata.items()}, indent=2))


if __name__ == '__main__':
    main()
