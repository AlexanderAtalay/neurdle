"""
extract_whole_brain.py
Creates a low-poly transparent reference brain for spatial context hints.
"""
import nibabel.freesurfer as fs
import trimesh
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

os.makedirs('meshes_raw', exist_ok=True)

for hemi in ['lh', 'rh']:
    coords, faces = fs.read_geometry(
        os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial')
    )
    mesh = trimesh.Trimesh(vertices=coords, faces=faces)
    mesh = mesh.simplify_quadric_decimation(face_count=5000)

    hemi_label = 'L' if hemi == 'lh' else 'R'
    mesh.export(f'meshes_raw/whole_brain_{hemi_label}.obj')
    print(f"Whole brain {hemi}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")
