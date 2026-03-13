"""
generate_lobe_meshes.py
Merges individual cortical region meshes into lobe-level meshes for Easy mode.
Run after extract_cortical_meshes.py.
"""
import trimesh
import os

LOBE_REGIONS = {
    'frontal_lobe': [
        'superiorfrontal', 'rostralmiddlefrontal', 'caudalmiddlefrontal',
        'parsopercularis', 'parstriangularis', 'parsorbitalis',
        'lateralorbitofrontal', 'medialorbitofrontal', 'precentral',
        'paracentral', 'frontalpole', 'rostralanteriorcingulate',
        'caudalanteriorcingulate'
    ],
    'parietal_lobe': [
        'superiorparietal', 'inferiorparietal', 'supramarginal',
        'postcentral', 'precuneus', 'posteriorcingulate', 'isthmuscingulate'
    ],
    'temporal_lobe': [
        'superiortemporal', 'middletemporal', 'inferiortemporal',
        'bankssts', 'fusiform', 'transversetemporal', 'entorhinal',
        'temporalpole', 'parahippocampal'
    ],
    'occipital_lobe': [
        'lateraloccipital', 'lingual', 'cuneus', 'pericalcarine'
    ],
    'insula': ['insula'],
}

os.makedirs('data/meshes/easy', exist_ok=True)

for hemi_label in ['L', 'R']:
    for lobe_name, region_names in LOBE_REGIONS.items():
        meshes = []
        for region in region_names:
            path = f'meshes_raw/desikan_killiany/{region}_{hemi_label}.obj'
            if os.path.exists(path):
                meshes.append(trimesh.load(path))

        if meshes:
            combined = trimesh.util.concatenate(meshes)
            if len(combined.faces) > 4000:
                combined = combined.simplify_quadric_decimation(face_count=4000)
            combined = combined.subdivide()
            outpath = f'data/meshes/easy/{lobe_name}_{hemi_label}.glb'
            combined.export(outpath)
            print(f"Exported {outpath}: {len(combined.faces)} faces")
        else:
            print(f"Warning: no meshes found for {lobe_name}_{hemi_label}")
