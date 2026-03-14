"""
extract_subfield_meshes.py
Extracts brainstem subfield and thalamic nuclei meshes from FreeSurfer
segment_subregions output.

Prerequisites:
    segment_subregions brainstem --cross fsaverage
    segment_subregions thalamus  --cross fsaverage

Run from repo root:
    python pipeline/extract_subfield_meshes.py
"""
import numpy as np
import nibabel as nib
from scipy import ndimage
import trimesh
from skimage import measure
import os
import glob

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')
MRI_DIR   = os.path.join(FSAVERAGE, 'mri')

# ---------------------------------------------------------------------------
# Brainstem subfield label IDs (FreeSurfer 7/8 brainstemSsLabels.mgz)
# ---------------------------------------------------------------------------
BRAINSTEM_LABELS = {
    173: 'midbrain',
    174: 'pons',
    175: 'medulla',
    176: 'scp',          # Superior Cerebellar Peduncle — skip if mesh too small
}

# Brainstem structures to actually include (scp tends to be very small)
BRAINSTEM_INCLUDE = {173, 174, 175}

# ---------------------------------------------------------------------------
# Thalamic nuclei label IDs (FreeSurfer 7/8 ThalamicNuclei.mgz)
# Left hemisphere; right hemisphere = left + 100
# ---------------------------------------------------------------------------
THALAMIC_NUCLEI_L = {
    8109: 'ld',          # Lateral Dorsal
    8110: 'mdl',         # Mediodorsal lateral
    8111: 'mdm',         # Mediodorsal medial
    8118: 'lgn',         # Lateral Geniculate Nucleus
    8119: 'mgn',         # Medial Geniculate Nucleus
    8120: 'cm',          # Centromedian
    8125: 'va',          # Ventral Anterior
    8128: 'vpla',        # Ventral Posterior Lateral (anterior)
    8129: 'vplp',        # Ventral Posterior Lateral (posterior)
    8130: 'vpm',         # Ventral Posterior Medial
    8132: 'pul_a',       # Pulvinar Anterior
    8133: 'pul_m',       # Pulvinar Medial
    8134: 'pul_l',       # Pulvinar Lateral
    8135: 'pul_i',       # Pulvinar Inferior
    8136: 'vla',         # Ventral Lateral anterior
    8137: 'vlp',         # Ventral Lateral posterior
}


def _find_mgz(pattern):
    """Find the latest versioned MGZ matching a glob pattern."""
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise FileNotFoundError(f'No file found matching: {pattern}')
    path = matches[-1]
    print(f'  Using: {path}')
    return path


def _extract_mesh(vol_data, affine, label_id, name, output_dir,
                  sigma=0.5, max_faces=3000):
    mask = (vol_data == label_id).astype(np.float32)
    if mask.sum() == 0:
        print(f'  Warning: label {label_id} ({name}) not found — skipping')
        return False

    mask = ndimage.gaussian_filter(mask, sigma=sigma)
    try:
        verts, faces, _, _ = measure.marching_cubes(mask, level=0.5, spacing=(1, 1, 1))
    except ValueError:
        print(f'  Warning: marching cubes failed for {name} — skipping')
        return False

    # Voxel → MNI
    verts_h = np.column_stack([verts, np.ones(len(verts))])
    verts_mni = (affine @ verts_h.T).T[:, :3]

    mesh = trimesh.Trimesh(vertices=verts_mni, faces=faces)
    trimesh.smoothing.filter_laplacian(mesh, iterations=10)
    if len(mesh.faces) > max_faces:
        mesh = mesh.simplify_quadric_decimation(face_count=max_faces)
    mesh = mesh.subdivide()

    out_path = os.path.join(output_dir, f'{name}.obj')
    mesh.export(out_path)
    print(f'  Exported {name}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces')
    return True


def extract_brainstem_subfields(output_dir='meshes_raw/subfields'):
    os.makedirs(output_dir, exist_ok=True)
    pat = os.path.join(MRI_DIR, 'brainstemSsLabels.v*.FSvoxelSpace.mgz')
    path = _find_mgz(pat)

    img = nib.load(path)
    data = np.round(img.get_fdata()).astype(int)
    affine = img.affine

    print('Brainstem subfields present:', sorted(set(data.flat) - {0}))

    for label_id, name in BRAINSTEM_LABELS.items():
        if label_id not in BRAINSTEM_INCLUDE:
            continue
        _extract_mesh(data, affine, label_id, name, output_dir)


def extract_thalamic_nuclei(output_dir='meshes_raw/subfields'):
    os.makedirs(output_dir, exist_ok=True)
    pat = os.path.join(MRI_DIR, 'ThalamicNuclei.v*.T1.FSvoxelSpace.mgz')
    path = _find_mgz(pat)

    img = nib.load(path)
    data = np.round(img.get_fdata()).astype(int)
    affine = img.affine

    print('Thalamic nuclei labels present:', sorted(set(data.flat) - {0}))

    # Merge left (label) + right (label+100) into one bilateral mesh per nucleus
    for label_l, name in THALAMIC_NUCLEI_L.items():
        label_r = label_l + 100
        mask = ((data == label_l) | (data == label_r)).astype(np.float32)
        if mask.sum() == 0:
            print(f'  Warning: {name} (L:{label_l} R:{label_r}) not found — skipping')
            continue

        mask = ndimage.gaussian_filter(mask, sigma=0.5)
        try:
            verts, faces, _, _ = measure.marching_cubes(mask, level=0.5, spacing=(1, 1, 1))
        except ValueError:
            print(f'  Warning: marching cubes failed for {name} — skipping')
            continue

        verts_h = np.column_stack([verts, np.ones(len(verts))])
        verts_mni = (affine @ verts_h.T).T[:, :3]

        mesh = trimesh.Trimesh(vertices=verts_mni, faces=faces)
        trimesh.smoothing.filter_laplacian(mesh, iterations=10)
        if len(mesh.faces) > 3000:
            mesh = mesh.simplify_quadric_decimation(face_count=3000)
        mesh = mesh.subdivide()

        out_path = os.path.join(output_dir, f'thal_{name}.obj')
        mesh.export(out_path)
        print(f'  Exported thal_{name}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces')


if __name__ == '__main__':
    print('\n=== Brainstem subfields ===')
    extract_brainstem_subfields()

    print('\n=== Thalamic nuclei ===')
    extract_thalamic_nuclei()

    print('\nDone. Next steps:')
    print('  1. python pipeline/convert_to_glb_python.py')
    print('  2. python pipeline/build_regions_json.py')
    print('  3. python pipeline/compute_distances.py')
    print('  4. python pipeline/merge_bilateral_distances.py')
