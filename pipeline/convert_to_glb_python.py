"""
convert_to_glb_python.py
Converts OBJ meshes to GLB using trimesh (no external tools needed).
"""
import trimesh
import os

def convert(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    mesh = trimesh.load(src, force='mesh')
    mesh.export(dst)
    print(f"  {dst}")

# Desikan-Killiany cortical → medium
os.makedirs('data/meshes/medium', exist_ok=True)
for f in sorted(os.listdir('meshes_raw/desikan_killiany')):
    if f.endswith('.obj'):
        convert(f'meshes_raw/desikan_killiany/{f}', f'data/meshes/medium/{f.replace(".obj",".glb")}')

# Subcortical
SUBCORICAL_DIFF = {
    'brainstem': 'easy',
    'cerebellum_cortex_L': 'easy', 'cerebellum_cortex_R': 'easy',
    'cerebellum_wm_L': 'easy', 'cerebellum_wm_R': 'easy',
    'thalamus_L': 'medium', 'thalamus_R': 'medium',
    'caudate_L': 'medium', 'caudate_R': 'medium',
    'putamen_L': 'medium', 'putamen_R': 'medium',
    'pallidum_L': 'medium', 'pallidum_R': 'medium',
    'hippocampus_L': 'medium', 'hippocampus_R': 'medium',
    'amygdala_L': 'medium', 'amygdala_R': 'medium',
    'accumbens_L': 'medium', 'accumbens_R': 'medium',
    'ventral_DC_L': 'hard', 'ventral_DC_R': 'hard',
    'lateral_ventricle_L': 'medium', 'lateral_ventricle_R': 'medium',
}
for f in sorted(os.listdir('meshes_raw/subcortical')):
    if f.endswith('.obj'):
        name = f.replace('.obj', '')
        diff = SUBCORICAL_DIFF.get(name, 'medium')
        convert(f'meshes_raw/subcortical/{f}', f'data/meshes/{diff}/{f.replace(".obj",".glb")}')

# Brodmann areas → hard
if os.path.isdir('meshes_raw/brodmann'):
    os.makedirs('data/meshes/hard', exist_ok=True)
    for f in sorted(os.listdir('meshes_raw/brodmann')):
        if f.endswith('.obj'):
            convert(f'meshes_raw/brodmann/{f}', f'data/meshes/hard/{f.replace(".obj",".glb")}')

# Brainstem subfields + thalamic nuclei → hard (or medium for pons/medulla)
SUBFIELD_DIFF = {
    'midbrain': 'medium',
    'pons':     'medium',
    'medulla':  'medium',
}
if os.path.isdir('meshes_raw/subfields'):
    os.makedirs('data/meshes/medium', exist_ok=True)
    os.makedirs('data/meshes/hard', exist_ok=True)
    for f in sorted(os.listdir('meshes_raw/subfields')):
        if f.endswith('.obj'):
            name = f.replace('.obj', '')
            diff = SUBFIELD_DIFF.get(name, 'hard')
            convert(f'meshes_raw/subfields/{f}', f'data/meshes/{diff}/{f.replace(".obj",".glb")}')

# Lobe (easy) already written as GLB by generate_lobe_meshes.py
# Whole brain ghost
for hemi in ['L', 'R']:
    src = f'meshes_raw/whole_brain_{hemi}.obj'
    if os.path.exists(src):
        convert(src, f'data/meshes/whole_brain_ghost_{hemi}.glb')

print("Done.")
