"""
extract_subcortical_meshes.py
Extracts subcortical structures from the aseg segmentation.
"""
import numpy as np
import nibabel as nib
from scipy import ndimage
import trimesh
from skimage import measure
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

# FreeSurfer aseg label IDs for subcortical structures
SUBCORTICAL_LABELS = {
    10: 'thalamus_L', 49: 'thalamus_R',
    11: 'caudate_L', 50: 'caudate_R',
    12: 'putamen_L', 51: 'putamen_R',
    13: 'pallidum_L', 52: 'pallidum_R',
    17: 'hippocampus_L', 53: 'hippocampus_R',
    18: 'amygdala_L', 54: 'amygdala_R',
    26: 'accumbens_L', 58: 'accumbens_R',
    16: 'brainstem',
    8: 'cerebellum_cortex_L', 47: 'cerebellum_cortex_R',
    7: 'cerebellum_wm_L', 46: 'cerebellum_wm_R',
    28: 'ventral_DC_L', 60: 'ventral_DC_R',
    4: 'lateral_ventricle_L', 43: 'lateral_ventricle_R',
}

def extract_subcortical_meshes(output_dir='meshes_raw/subcortical'):
    os.makedirs(output_dir, exist_ok=True)

    aseg_path = os.path.join(FSAVERAGE, 'mri', 'aseg.mgz')
    aseg_img = nib.load(aseg_path)
    aseg_data = aseg_img.get_fdata()
    affine = aseg_img.affine

    for label_id, name in SUBCORTICAL_LABELS.items():
        mask = (aseg_data == label_id).astype(np.float32)
        if mask.sum() == 0:
            print(f"Warning: {name} (label {label_id}) not found in aseg")
            continue

        mask = ndimage.gaussian_filter(mask, sigma=0.5)

        try:
            verts, faces, normals, values = measure.marching_cubes(
                mask, level=0.5, spacing=(1, 1, 1)
            )
        except ValueError:
            print(f"Warning: Could not extract mesh for {name}")
            continue

        verts_homogeneous = np.column_stack([verts, np.ones(len(verts))])
        verts_mni = (affine @ verts_homogeneous.T).T[:, :3]

        mesh = trimesh.Trimesh(vertices=verts_mni, faces=faces)
        trimesh.smoothing.filter_laplacian(mesh, iterations=10)
        if len(mesh.faces) > 2000:
            mesh = mesh.simplify_quadric_decimation(face_count=2000)
        mesh = mesh.subdivide()

        mesh.export(os.path.join(output_dir, f"{name}.obj"))
        print(f"Exported {name}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")

extract_subcortical_meshes()
