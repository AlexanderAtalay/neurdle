"""
compute_distances.py
Computes nearest-boundary distances and anatomical directions
between all region pairs within each difficulty tier.
"""
import numpy as np
import trimesh
import json
import os
from scipy.spatial import cKDTree


def load_meshes(directory):
    """Load all OBJ meshes from a directory, return dict of name -> mesh."""
    meshes = {}
    for f in os.listdir(directory):
        if f.endswith('.obj'):
            name = f.replace('.obj', '')
            meshes[name] = trimesh.load(os.path.join(directory, f))
    return meshes


def compute_nearest_distance_and_direction(mesh_a, mesh_b):
    """
    Compute nearest-boundary distance (mm) and anatomical direction
    from region A to region B.
    """
    tree_b = cKDTree(mesh_b.vertices)
    dists, indices = tree_b.query(mesh_a.vertices)
    min_dist = float(dists.min())

    centroid_a = mesh_a.centroid
    centroid_b = mesh_b.centroid
    delta = centroid_b - centroid_a  # [x, y, z] in MNI

    # MNI: X = left(-)/right(+), Y = posterior(-)/anterior(+), Z = inferior(-)/superior(+)
    directions = []
    if abs(delta[1]) > 3:
        directions.append('anterior' if delta[1] > 0 else 'posterior')
    if abs(delta[2]) > 3:
        directions.append('superior' if delta[2] > 0 else 'inferior')
    if abs(delta[0]) > 3:
        if abs(centroid_b[0]) > abs(centroid_a[0]):
            directions.append('lateral')
        else:
            directions.append('medial')

    axis_magnitudes = {
        'anterior': abs(delta[1]) if delta[1] > 0 else 0,
        'posterior': abs(delta[1]) if delta[1] < 0 else 0,
        'superior': abs(delta[2]) if delta[2] > 0 else 0,
        'inferior': abs(delta[2]) if delta[2] < 0 else 0,
        'lateral': abs(abs(centroid_b[0]) - abs(centroid_a[0])) if abs(centroid_b[0]) > abs(centroid_a[0]) else 0,
        'medial': abs(abs(centroid_a[0]) - abs(centroid_b[0])) if abs(centroid_a[0]) > abs(centroid_b[0]) else 0,
    }
    sorted_dirs = sorted(
        [d for d in directions if axis_magnitudes.get(d, 0) > 3],
        key=lambda d: axis_magnitudes.get(d, 0),
        reverse=True
    )

    return round(min_dist, 1), sorted_dirs[:2]


def compute_all_distances(mesh_dir, output_file):
    print(f"Loading meshes from {mesh_dir}...")
    meshes = load_meshes(mesh_dir)
    distances = {}

    names = list(meshes.keys())
    total = len(names) * (len(names) - 1)
    count = 0

    print(f"Computing {total} pairwise distances...")
    for name_a in names:
        distances[name_a] = {}
        for name_b in names:
            if name_a == name_b:
                continue
            count += 1
            if count % 100 == 0:
                print(f"  {count}/{total}...")

            dist, dirs = compute_nearest_distance_and_direction(
                meshes[name_a], meshes[name_b]
            )
            distances[name_a][name_b] = {
                'distance_mm': dist,
                'direction': dirs
            }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(distances, f, indent=2)
    print(f"Saved {output_file}")


compute_all_distances('meshes_raw/desikan_killiany', 'data/distances_medium.json')
compute_all_distances('meshes_raw/subcortical', 'data/distances_subcortical.json')
