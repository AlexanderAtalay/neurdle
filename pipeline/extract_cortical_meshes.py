"""
extract_cortical_meshes.py
Extracts individual cortical region meshes from fsaverage parcellations.
Outputs OBJ files for each region.
"""
import numpy as np
import nibabel.freesurfer as fs
import trimesh
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

def extract_parcellation_meshes(atlas='aparc', output_dir='meshes_raw'):
    """
    atlas options: 'aparc' (Desikan-Killiany), 'aparc.a2009s' (Destrieux),
                   'aparc.DKTatlas' (DKT)
    """
    os.makedirs(output_dir, exist_ok=True)

    for hemi in ['lh', 'rh']:
        # Load surface mesh
        coords, faces = fs.read_geometry(
            os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial')
        )

        # Load parcellation annotation
        labels, ctab, names = fs.read_annot(
            os.path.join(FSAVERAGE, 'label', f'{hemi}.{atlas}.annot')
        )

        # Extract each region as a separate mesh
        for i, name in enumerate(names):
            name_str = name.decode('utf-8') if isinstance(name, bytes) else name
            if name_str in ('unknown', 'Unknown', 'corpuscallosum', 'Medial_wall'):
                continue

            # Get vertices belonging to this region
            region_mask = labels == i
            if region_mask.sum() == 0:
                continue

            # Get faces where ALL three vertices are in the region
            face_mask = region_mask[faces].all(axis=1)
            region_faces = faces[face_mask]

            # Remap vertex indices
            unique_verts = np.unique(region_faces)
            vert_map = {old: new for new, old in enumerate(unique_verts)}
            new_faces = np.vectorize(vert_map.get)(region_faces)
            new_coords = coords[unique_verts]

            # Create and save mesh
            mesh = trimesh.Trimesh(vertices=new_coords, faces=new_faces)

            # Decimate then subdivide for smooth web mesh (~8k faces)
            if len(mesh.faces) > 2000:
                mesh = mesh.simplify_quadric_decimation(face_count=2000)
            mesh = mesh.subdivide()

            hemi_label = 'L' if hemi == 'lh' else 'R'
            filename = f"{name_str}_{hemi_label}.obj"
            mesh.export(os.path.join(output_dir, filename))
            print(f"Exported {filename}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")

# Run for different atlases
extract_parcellation_meshes('aparc', 'meshes_raw/desikan_killiany')
extract_parcellation_meshes('aparc.a2009s', 'meshes_raw/destrieux')

