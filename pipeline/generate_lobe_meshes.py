"""
generate_lobe_meshes.py
Extracts lobe-level meshes directly from the FreeSurfer pial surface using
the Desikan-Killiany parcellation. This produces seamless meshes with no
internal region-boundary edges.

Run from repo root:
    python pipeline/generate_lobe_meshes.py
"""
import nibabel.freesurfer as fs
import numpy as np
import trimesh
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

# Which DK regions belong to each lobe
LOBE_REGIONS = {
    'frontal_lobe': [
        'superiorfrontal', 'rostralmiddlefrontal', 'caudalmiddlefrontal',
        'parsopercularis', 'parstriangularis', 'parsorbitalis',
        'lateralorbitofrontal', 'medialorbitofrontal', 'precentral',
        'paracentral', 'frontalpole', 'rostralanteriorcingulate',
        'caudalanteriorcingulate',
    ],
    'parietal_lobe': [
        'superiorparietal', 'inferiorparietal', 'supramarginal',
        'postcentral', 'precuneus', 'posteriorcingulate', 'isthmuscingulate',
    ],
    'temporal_lobe': [
        'superiortemporal', 'middletemporal', 'inferiortemporal',
        'bankssts', 'fusiform', 'transversetemporal', 'entorhinal',
        'temporalpole', 'parahippocampal',
    ],
    'occipital_lobe': [
        'lateraloccipital', 'lingual', 'cuneus', 'pericalcarine',
    ],
    'insula': ['insula'],
}

os.makedirs('data/meshes/easy', exist_ok=True)

for hemi in ['lh', 'rh']:
    hemi_label = 'L' if hemi == 'lh' else 'R'

    # Load pial surface and annotation
    coords, faces = fs.read_geometry(
        os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial'))
    labels, ctab, names = fs.read_annot(
        os.path.join(FSAVERAGE, 'label', f'{hemi}.aparc.annot'))

    # Build name → label-index lookup
    name_to_idx = {
        (n.decode() if isinstance(n, bytes) else n): i
        for i, n in enumerate(names)
    }

    for lobe_name, region_names in LOBE_REGIONS.items():
        # Collect all vertex indices belonging to this lobe's regions
        lobe_label_ids = {
            name_to_idx[r] for r in region_names if r in name_to_idx
        }
        vertex_mask = np.isin(labels, list(lobe_label_ids))

        # Keep only triangles whose three vertices are all in the lobe
        face_mask = vertex_mask[faces].all(axis=1)
        lobe_faces = faces[face_mask]

        if lobe_faces.shape[0] == 0:
            print(f'Warning: no faces for {lobe_name}_{hemi_label}')
            continue

        # Compact vertex indices
        used_verts, inv = np.unique(lobe_faces, return_inverse=True)
        new_faces = inv.reshape(lobe_faces.shape)
        new_verts = coords[used_verts]

        mesh = trimesh.Trimesh(vertices=new_verts, faces=new_faces, process=True)

        # Smooth and decimate
        trimesh.smoothing.filter_laplacian(mesh, iterations=3)
        if len(mesh.faces) > 6000:
            mesh = mesh.simplify_quadric_decimation(face_count=6000)
        mesh = mesh.subdivide()

        outpath = f'data/meshes/easy/{lobe_name}_{hemi_label}.glb'
        mesh.export(outpath)
        print(f'Exported {outpath}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces')
