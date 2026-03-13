#!/bin/bash
# convert_to_glb.sh
# Converts all OBJ meshes to GLB (binary glTF) for efficient web loading.
# Requires: npm install -g obj2gltf

set -e

# Check for obj2gltf
if ! command -v obj2gltf &> /dev/null; then
    echo "obj2gltf not found. Installing..."
    npm install -g obj2gltf
fi

mkdir -p data/meshes/easy data/meshes/medium data/meshes/hard

# Convert subcortical meshes -> easy/medium/hard based on known names
declare -A DIFFICULTY_MAP=(
    ["brainstem"]="easy"
    ["cerebellum_cortex_L"]="easy" ["cerebellum_cortex_R"]="easy"
    ["cerebellum_wm_L"]="easy" ["cerebellum_wm_R"]="easy"
    ["thalamus_L"]="medium" ["thalamus_R"]="medium"
    ["caudate_L"]="medium" ["caudate_R"]="medium"
    ["putamen_L"]="medium" ["putamen_R"]="medium"
    ["pallidum_L"]="medium" ["pallidum_R"]="medium"
    ["hippocampus_L"]="medium" ["hippocampus_R"]="medium"
    ["amygdala_L"]="medium" ["amygdala_R"]="medium"
    ["accumbens_L"]="hard" ["accumbens_R"]="hard"
    ["ventral_DC_L"]="hard" ["ventral_DC_R"]="hard"
)

echo "Converting whole brain ghost meshes..."
for hemi in L R; do
    obj_file="meshes_raw/whole_brain_${hemi}.obj"
    if [ -f "$obj_file" ]; then
        obj2gltf -i "$obj_file" -o "data/meshes/whole_brain_ghost_${hemi}.glb"
        echo "  -> data/meshes/whole_brain_ghost_${hemi}.glb"
    fi
done

echo "Converting Desikan-Killiany (medium) meshes..."
for obj_file in meshes_raw/desikan_killiany/*.obj; do
    base=$(basename "$obj_file" .obj)
    out="data/meshes/medium/${base}.glb"
    obj2gltf -i "$obj_file" -o "$out"
    echo "  -> $out"
done

echo "Converting lobe (easy) meshes..."
for obj_file in data/meshes/easy/*.obj 2>/dev/null; do
    [ -f "$obj_file" ] || continue
    base=$(basename "$obj_file" .obj)
    out="data/meshes/easy/${base}.glb"
    obj2gltf -i "$obj_file" -o "$out"
    echo "  -> $out"
done

echo "Converting subcortical meshes..."
for obj_file in meshes_raw/subcortical/*.obj; do
    base=$(basename "$obj_file" .obj)
    difficulty="${DIFFICULTY_MAP[$base]:-medium}"
    out="data/meshes/${difficulty}/${base}.glb"
    obj2gltf -i "$obj_file" -o "$out"
    echo "  -> $out"
done

echo "Done. All OBJ files converted to GLB."
