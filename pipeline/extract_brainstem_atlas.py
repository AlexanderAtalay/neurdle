"""
extract_brainstem_atlas.py
Extracts brainstem subregion meshes (Midbrain, Pons, Medulla) by:
  1. Resampling the probabilistic brainstem atlas into fsaverage T1 space
  2. Constraining all voxels to the FreeSurfer aseg brainstem mask
     (label 16 = Brain-Stem; labels 28+60 = VentralDC included for midbrain)
  3. Assigning each constrained voxel to whichever structure has the highest
     probability (argmax), so the three meshes cleanly partition the brainstem
  4. Running marching cubes on each binary assignment mask

Run from repo root:
    python pipeline/extract_brainstem_atlas.py
"""
import nibabel as nib
import nibabel.processing as nip
import numpy as np
from scipy import ndimage
from skimage import measure
import trimesh
import os
import shutil

ATLAS_PATH = 'brainstem/Brainstem/BrainstemProbs.MNIsymSpace.nii.gz'
T1_PATH    = 'brainstem/fsaverage/mri/T1.mgz'
ASEG_PATH  = 'brainstem/fsaverage/mri/aseg.mgz'
OUT_DIR    = 'data/meshes/medium'
PUBLIC_DIR = 'neurdle/public/meshes/medium'

# Atlas volume index → (id, display name, max_faces)
STRUCTURES = [
    (4, 'midbrain', 'Midbrain',          4000),
    (2, 'pons',     'Pons',              5000),
    (1, 'medulla',  'Medulla Oblongata', 4000),
]

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

atlas     = nib.load(ATLAS_PATH)
t1        = nib.load(T1_PATH)
aseg_data = np.round(nib.load(ASEG_PATH).get_fdata()).astype(int)

# ── Build anatomy masks ──────────────────────────────────────────────────────
# Brainstem (label 16) for pons + medulla
# Brainstem + VentralDC (28 = left, 60 = right) for midbrain
# (VentralDC contains substantia nigra and red nucleus, both midbrain structures)
bs_mask      = aseg_data == 16
ventral_mask = (aseg_data == 28) | (aseg_data == 60)
midbrain_roi = bs_mask | ventral_mask          # extended ROI for midbrain
full_roi     = bs_mask | ventral_mask          # all candidate voxels

print(f'Brainstem voxels: {bs_mask.sum()}')
print(f'VentralDC voxels: {ventral_mask.sum()}')
print(f'Combined ROI:     {full_roi.sum()}')

# ── Resample all probability volumes into T1 space ───────────────────────────
print('\nResampling atlas volumes into fsaverage space...')
prob_vols = {}
for vol_idx, sid, name, _ in STRUCTURES:
    img = nib.Nifti1Image(atlas.slicer[..., vol_idx].get_fdata(), atlas.affine)
    prob_vols[sid] = nip.resample_from_to(img, t1, order=1).get_fdata()
    print(f'  {name}: max prob = {prob_vols[sid][full_roi].max():.3f}')

# ── Argmax assignment constrained to the combined ROI ────────────────────────
# Shape: (X, Y, Z, 3)  — channels: medulla, pons, midbrain
stacked = np.stack([prob_vols['medulla'],
                    prob_vols['pons'],
                    prob_vols['midbrain']], axis=-1)

# argmax: 0=medulla, 1=pons, 2=midbrain
argmax_vol = np.argmax(stacked, axis=-1)

# ── Extract mesh for each structure ──────────────────────────────────────────
idx_map = {'medulla': 0, 'pons': 1, 'midbrain': 2}

for vol_idx, sid, name, max_faces in STRUCTURES:
    print(f'\nProcessing {name}...')

    # Build the per-structure ROI
    if sid == 'midbrain':
        roi = full_roi
    else:
        roi = bs_mask

    # Binary assignment mask: voxels in ROI assigned to this structure
    assign_mask = roi & (argmax_vol == idx_map[sid])
    print(f'  Assigned voxels: {assign_mask.sum()}')

    if assign_mask.sum() < 100:
        print(f'  Too few voxels, skipping.')
        continue

    # Light smoothing to clean up jagged boundaries before marching cubes
    smoothed = ndimage.gaussian_filter(assign_mask.astype(np.float32), sigma=0.8)

    try:
        verts_vox, faces, _, _ = measure.marching_cubes(
            smoothed, level=0.5, spacing=(1, 1, 1))
    except ValueError as e:
        print(f'  Marching cubes failed: {e}. Skipping.')
        continue

    # Voxel coords → FreeSurfer RAS
    verts_h   = np.column_stack([verts_vox, np.ones(len(verts_vox))])
    verts_ras = (t1.affine @ verts_h.T).T[:, :3]

    mesh = trimesh.Trimesh(vertices=verts_ras, faces=faces, process=True)
    trimesh.smoothing.filter_laplacian(mesh, iterations=8)

    if len(mesh.faces) > max_faces:
        mesh = mesh.simplify_quadric_decimation(face_count=max_faces)

    mesh = mesh.subdivide()

    print(f'  Centroid (FS RAS): {mesh.centroid.round(1)}')
    print(f'  Mesh: {len(mesh.vertices)} verts, {len(mesh.faces)} faces')

    glb_path = os.path.join(OUT_DIR, f'{sid}.glb')
    mesh.export(glb_path)
    print(f'  Saved {glb_path}')

    pub_path = os.path.join(PUBLIC_DIR, f'{sid}.glb')
    shutil.copy2(glb_path, pub_path)
    print(f'  Copied to {pub_path}')

print('\nDone. Next: run python pipeline/build_regions_json.py')
