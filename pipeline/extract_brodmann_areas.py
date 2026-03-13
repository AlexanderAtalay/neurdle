"""
extract_brodmann_areas.py
Extracts Brodmann area meshes from the PALS_B12_Brodmann annotation (mapped to fsaverage).
Also extracts individual exvivo BA label files for key named areas.
Outputs OBJ files to meshes_raw/brodmann/.
"""
import numpy as np
import nibabel.freesurfer as fs
import trimesh
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

# Named Brodmann areas to extract (combining both exvivo label files and PALS annot)
# These use the lh/rh.BA*_exvivo.label files
EXVIVO_LABELS = {
    'BA1': 'BA1_exvivo',
    'BA2': 'BA2_exvivo',
    'BA3a': 'BA3a_exvivo',
    'BA3b': 'BA3b_exvivo',
    'BA4a': 'BA4a_exvivo',
    'BA4p': 'BA4p_exvivo',
    'BA6': 'BA6_exvivo',
    'BA44': 'BA44_exvivo',
    'BA45': 'BA45_exvivo',
}

def smooth_and_decimate(mesh, smooth_iters=0, target_faces=2000):
    """Apply optional smoothing and decimate, then subdivide once."""
    if smooth_iters > 0:
        trimesh.smoothing.filter_laplacian(mesh, iterations=smooth_iters)
    if len(mesh.faces) > target_faces:
        mesh = mesh.simplify_quadric_decimation(face_count=target_faces)
    # Subdivide once for smoother appearance
    mesh = mesh.subdivide()
    return mesh


def extract_from_label_file(hemi, label_name, coords, faces):
    """Extract a mesh from a FreeSurfer .label file."""
    label_path = os.path.join(FSAVERAGE, 'label', f'{hemi}.{label_name}.label')
    if not os.path.exists(label_path):
        return None

    # Read label file: skip header line, then vertex indices are in column 0
    with open(label_path) as f:
        lines = f.readlines()
    # First line is comment, second is count, rest are vertex data
    vertex_indices = set()
    for line in lines[2:]:
        parts = line.strip().split()
        if parts:
            vertex_indices.add(int(parts[0]))

    if not vertex_indices:
        return None

    region_mask = np.zeros(len(coords), dtype=bool)
    for idx in vertex_indices:
        if idx < len(coords):
            region_mask[idx] = True

    face_mask = region_mask[faces].all(axis=1)
    region_faces = faces[face_mask]

    if len(region_faces) == 0:
        return None

    unique_verts = np.unique(region_faces)
    vert_map = {old: new for new, old in enumerate(unique_verts)}
    new_faces = np.vectorize(vert_map.get)(region_faces)
    new_coords = coords[unique_verts]

    return trimesh.Trimesh(vertices=new_coords, faces=new_faces)


def extract_brodmann_meshes(output_dir='meshes_raw/brodmann'):
    os.makedirs(output_dir, exist_ok=True)

    for hemi in ['lh', 'rh']:
        coords, faces = fs.read_geometry(
            os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial')
        )
        hemi_label = 'L' if hemi == 'lh' else 'R'

        for ba_name, label_name in EXVIVO_LABELS.items():
            mesh = extract_from_label_file(hemi, label_name, coords, faces)
            if mesh is None:
                print(f"  Skipping {ba_name}_{hemi_label}: label not found or empty")
                continue

            mesh = smooth_and_decimate(mesh, smooth_iters=0, target_faces=2000)
            filename = f"{ba_name}_{hemi_label}.obj"
            mesh.export(os.path.join(output_dir, filename))
            print(f"Exported {filename}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")

    # Also extract from PALS_B12_Brodmann annotation (has more areas)
    for hemi in ['lh', 'rh']:
        annot_path = os.path.join(FSAVERAGE, 'label', f'{hemi}.PALS_B12_Brodmann.annot')
        if not os.path.exists(annot_path):
            print(f"PALS annot not found for {hemi}, skipping")
            continue

        coords, faces = fs.read_geometry(
            os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial')
        )
        hemi_label = 'L' if hemi == 'lh' else 'R'

        labels, ctab, names = fs.read_annot(annot_path)

        for i, name_bytes in enumerate(names):
            name = name_bytes.decode('utf-8') if isinstance(name_bytes, bytes) else name_bytes
            # Skip non-Brodmann entries and ones we already have from exvivo
            if not name.startswith('Brodmann'):
                continue
            # Extract BA number: "Brodmann.1" -> "BA1"
            ba_num = name.split('.')[-1]
            ba_id = f'PALS_BA{ba_num}'

            region_mask = labels == i
            if region_mask.sum() < 50:
                continue

            face_mask = region_mask[faces].all(axis=1)
            region_faces = faces[face_mask]
            if len(region_faces) == 0:
                continue

            unique_verts = np.unique(region_faces)
            vert_map = {old: new for new, old in enumerate(unique_verts)}
            new_faces = np.vectorize(vert_map.get)(region_faces)
            new_coords = coords[unique_verts]

            mesh = trimesh.Trimesh(vertices=new_coords, faces=new_faces)
            mesh = smooth_and_decimate(mesh, smooth_iters=0, target_faces=2000)

            filename = f"{ba_id}_{hemi_label}.obj"
            mesh.export(os.path.join(output_dir, filename))
            print(f"Exported {filename}: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")


extract_brodmann_meshes()
