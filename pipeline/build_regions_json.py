"""
build_regions_json.py
- Easy:   Brain lobes + cerebellum + brainstem (bilateral)
- Medium: Desikan-Killiany cortical (bilateral) + major subcortical (bilateral)
- Hard:   Destrieux atlas cortical (bilateral) + extra subcortical
"""
import nibabel.freesurfer as fs
import numpy as np
import json
import os

FSAVERAGE = os.path.join(os.environ.get('FREESURFER_HOME', ''), 'subjects', 'fsaverage')

# ----------- Desikan-Killiany mappings (medium) -----------

DK_LOBE = {
    'superiorfrontal': 'frontal', 'rostralmiddlefrontal': 'frontal',
    'caudalmiddlefrontal': 'frontal', 'parsopercularis': 'frontal',
    'parstriangularis': 'frontal', 'parsorbitalis': 'frontal',
    'lateralorbitofrontal': 'frontal', 'medialorbitofrontal': 'frontal',
    'precentral': 'frontal', 'paracentral': 'frontal',
    'frontalpole': 'frontal', 'rostralanteriorcingulate': 'frontal',
    'caudalanteriorcingulate': 'frontal',
    'superiorparietal': 'parietal', 'inferiorparietal': 'parietal',
    'supramarginal': 'parietal', 'postcentral': 'parietal',
    'precuneus': 'parietal', 'posteriorcingulate': 'parietal',
    'isthmuscingulate': 'parietal',
    'superiortemporal': 'temporal', 'middletemporal': 'temporal',
    'inferiortemporal': 'temporal', 'bankssts': 'temporal',
    'fusiform': 'temporal', 'transversetemporal': 'temporal',
    'entorhinal': 'temporal', 'temporalpole': 'temporal',
    'parahippocampal': 'temporal',
    'lateraloccipital': 'occipital', 'lingual': 'occipital',
    'cuneus': 'occipital', 'pericalcarine': 'occipital',
    'insula': 'insula',
}

DK_NAMES = {
    'superiorfrontal': 'Superior Frontal Gyrus',
    'rostralmiddlefrontal': 'Middle Frontal Gyrus (Rostral)',
    'caudalmiddlefrontal': 'Middle Frontal Gyrus (Caudal)',
    'parsopercularis': "Broca's Area (Pars Opercularis)",
    'parstriangularis': "Broca's Area (Pars Triangularis)",
    'parsorbitalis': 'Orbitofrontal Cortex (Pars Orbitalis)',
    'lateralorbitofrontal': 'Lateral Orbitofrontal Cortex',
    'medialorbitofrontal': 'Medial Orbitofrontal Cortex',
    'precentral': 'Primary Motor Cortex',
    'paracentral': 'Paracentral Lobule',
    'frontalpole': 'Frontal Pole',
    'rostralanteriorcingulate': 'Anterior Cingulate Cortex (Rostral)',
    'caudalanteriorcingulate': 'Anterior Cingulate Cortex (Caudal)',
    'superiorparietal': 'Superior Parietal Lobule',
    'inferiorparietal': 'Inferior Parietal Lobule',
    'supramarginal': 'Supramarginal Gyrus',
    'postcentral': 'Primary Somatosensory Cortex',
    'precuneus': 'Precuneus',
    'posteriorcingulate': 'Posterior Cingulate Cortex',
    'isthmuscingulate': 'Isthmus Cingulate Cortex',
    'superiortemporal': 'Superior Temporal Gyrus',
    'middletemporal': 'Middle Temporal Gyrus',
    'inferiortemporal': 'Inferior Temporal Gyrus',
    'bankssts': 'Banks of the Superior Temporal Sulcus',
    'fusiform': 'Fusiform Gyrus',
    'transversetemporal': "Heschl's Gyrus",
    'entorhinal': 'Entorhinal Cortex',
    'temporalpole': 'Temporal Pole',
    'parahippocampal': 'Parahippocampal Gyrus',
    'lateraloccipital': 'Lateral Occipital Cortex',
    'lingual': 'Lingual Gyrus',
    'cuneus': 'Cuneus',
    'pericalcarine': 'Primary Visual Cortex',
    'insula': 'Insula',
}

DK_ALIASES = {
    'parsopercularis': ["Broca's area", 'BA44'],
    'parstriangularis': ["Broca's area", 'BA45'],
    'precentral': ['primary motor cortex', 'M1', 'BA4'],
    'postcentral': ['primary somatosensory cortex', 'S1', 'BA1', 'BA2', 'BA3'],
    'transversetemporal': ["Heschl's gyrus", 'primary auditory cortex', 'A1'],
    'pericalcarine': ['primary visual cortex', 'V1', 'BA17', 'striate cortex'],
    'superiortemporal': ["Wernicke's area", 'STG'],
    'entorhinal': ['BA28'],
    'fusiform': ['fusiform face area', 'FFA'],
    'insula': ['insular cortex'],
    'lateralorbitofrontal': ['OFC'],
}

# ----------- Destrieux mappings (hard) -----------

DESTRIEUX_NAMES = {
    'G_and_S_frontomargin': 'Frontomarginal Gyrus and Sulcus',
    'G_and_S_occipital_inf': 'Inferior Occipital Gyrus and Sulcus',
    'G_and_S_paracentral': 'Paracentral Lobule',
    'G_and_S_subcentral': 'Subcentral Gyrus and Sulci',
    'G_and_S_transv_frontopol': 'Transverse Frontopolar Gyri and Sulci',
    'G_and_S_cingul-Ant': 'Anterior Cingulate Gyrus and Sulcus',
    'G_and_S_cingul-Mid-Ant': 'Middle-Anterior Cingulate Gyrus and Sulcus',
    'G_and_S_cingul-Mid-Post': 'Middle-Posterior Cingulate Gyrus and Sulcus',
    'G_cingul-Post-dorsal': 'Posterior Cingulate Gyrus (Dorsal)',
    'G_cingul-Post-ventral': 'Posterior Cingulate Gyrus (Ventral)',
    'G_cuneus': 'Cuneus Gyrus',
    'G_front_inf-Opercular': 'Inferior Frontal Gyrus (Opercular)',
    'G_front_inf-Orbital': 'Inferior Frontal Gyrus (Orbital)',
    'G_front_inf-Triangul': 'Inferior Frontal Gyrus (Triangular)',
    'G_front_middle': 'Middle Frontal Gyrus',
    'G_front_sup': 'Superior Frontal Gyrus',
    'G_Ins_lg_and_S_cent_ins': 'Long Insular Gyrus and Central Insular Sulcus',
    'G_insular_short': 'Short Insular Gyri',
    'G_occipital_middle': 'Middle Occipital Gyrus',
    'G_occipital_sup': 'Superior Occipital Gyrus',
    'G_oc-temp_lat-fusifor': 'Fusiform Gyrus',
    'G_oc-temp_med-Lingual': 'Lingual Gyrus',
    'G_oc-temp_med-Parahip': 'Parahippocampal Gyrus',
    'G_orbital': 'Orbital Gyri',
    'G_pariet_inf-Angular': 'Angular Gyrus',
    'G_pariet_inf-Supramar': 'Supramarginal Gyrus',
    'G_parietal_sup': 'Superior Parietal Lobule',
    'G_postcentral': 'Postcentral Gyrus',
    'G_precentral': 'Precentral Gyrus',
    'G_precuneus': 'Precuneus',
    'G_rectus': 'Gyrus Rectus',
    'G_subcallosal': 'Subcallosal Gyrus',
    'G_temp_sup-G_T_transv': "Heschl's Gyrus",
    'G_temp_sup-Lateral': 'Superior Temporal Gyrus (Lateral)',
    'G_temp_sup-Plan_polar': 'Planum Polare',
    'G_temp_sup-Plan_tempo': 'Planum Temporale',
    'G_temporal_inf': 'Inferior Temporal Gyrus',
    'G_temporal_middle': 'Middle Temporal Gyrus',
    'Lat_Fis-ant-Horizont': 'Lateral Fissure (Anterior Horizontal)',
    'Lat_Fis-ant-Vertical': 'Lateral Fissure (Anterior Vertical)',
    'Lat_Fis-post': 'Posterior Lateral Fissure',
    'Pole_occipital': 'Occipital Pole',
    'Pole_temporal': 'Temporal Pole',
    'S_calcarine': 'Calcarine Sulcus',
    'S_central': 'Central Sulcus',
    'S_cingul-Marginalis': 'Marginal Cingulate Sulcus',
    'S_circular_insula_ant': 'Anterior Circular Sulcus of Insula',
    'S_circular_insula_inf': 'Inferior Circular Sulcus of Insula',
    'S_circular_insula_sup': 'Superior Circular Sulcus of Insula',
    'S_collat_transv_ant': 'Anterior Collateral Sulcus',
    'S_collat_transv_post': 'Posterior Collateral Sulcus',
    'S_front_inf': 'Inferior Frontal Sulcus',
    'S_front_middle': 'Middle Frontal Sulcus',
    'S_front_sup': 'Superior Frontal Sulcus',
    'S_interm_prim-Jensen': "Jensen's Sulcus",
    'S_intrapariet_and_P_trans': 'Intraparietal Sulcus',
    'S_oc_middle_and_Lunatus': 'Middle Occipital and Lunate Sulci',
    'S_oc_sup_and_transversal': 'Superior Occipital and Transverse Sulci',
    'S_occipital_ant': 'Anterior Occipital Sulcus',
    'S_oc-temp_lat': 'Lateral Occipito-temporal Sulcus',
    'S_oc-temp_med_and_Lingual': 'Medial Occipito-temporal and Lingual Sulci',
    'S_orbital_lateral': 'Lateral Orbital Sulcus',
    'S_orbital_med-olfact': 'Medial Orbital and Olfactory Sulci',
    'S_orbital-H_Shaped': 'H-Shaped Orbital Sulci',
    'S_parieto_occipital': 'Parieto-occipital Sulcus',
    'S_pericallosal': 'Pericallosal Sulcus',
    'S_postcentral': 'Postcentral Sulcus',
    'S_precentral-inf-part': 'Inferior Precentral Sulcus',
    'S_precentral-sup-part': 'Superior Precentral Sulcus',
    'S_suborbital': 'Suborbital Sulcus',
    'S_subparietal': 'Subparietal Sulcus',
    'S_temporal_inf': 'Inferior Temporal Sulcus',
    'S_temporal_sup': 'Superior Temporal Sulcus',
    'S_temporal_transverse': 'Transverse Temporal Sulcus',
}

DESTRIEUX_LOBE = {
    'G_and_S_frontomargin': 'frontal', 'G_and_S_paracentral': 'frontal',
    'G_and_S_subcentral': 'frontal', 'G_and_S_transv_frontopol': 'frontal',
    'G_and_S_cingul-Ant': 'frontal', 'G_and_S_cingul-Mid-Ant': 'frontal',
    'G_and_S_cingul-Mid-Post': 'parietal',
    'G_cingul-Post-dorsal': 'parietal', 'G_cingul-Post-ventral': 'parietal',
    'G_front_inf-Opercular': 'frontal', 'G_front_inf-Orbital': 'frontal',
    'G_front_inf-Triangul': 'frontal', 'G_front_middle': 'frontal',
    'G_front_sup': 'frontal', 'G_precentral': 'frontal',
    'G_rectus': 'frontal', 'G_subcallosal': 'frontal', 'G_orbital': 'frontal',
    'S_front_inf': 'frontal', 'S_front_middle': 'frontal', 'S_front_sup': 'frontal',
    'S_precentral-inf-part': 'frontal', 'S_precentral-sup-part': 'frontal',
    'S_suborbital': 'frontal', 'S_orbital_lateral': 'frontal',
    'S_orbital_med-olfact': 'frontal', 'S_orbital-H_Shaped': 'frontal',
    'S_central': 'frontal', 'S_pericallosal': 'frontal',
    'G_and_S_occipital_inf': 'occipital', 'G_cuneus': 'occipital',
    'G_occipital_middle': 'occipital', 'G_occipital_sup': 'occipital',
    'G_oc-temp_lat-fusifor': 'occipital', 'G_oc-temp_med-Lingual': 'occipital',
    'Pole_occipital': 'occipital', 'S_calcarine': 'occipital',
    'S_oc_middle_and_Lunatus': 'occipital', 'S_oc_sup_and_transversal': 'occipital',
    'S_occipital_ant': 'occipital', 'S_oc-temp_lat': 'occipital',
    'S_oc-temp_med_and_Lingual': 'occipital', 'S_parieto_occipital': 'occipital',
    'G_pariet_inf-Angular': 'parietal', 'G_pariet_inf-Supramar': 'parietal',
    'G_parietal_sup': 'parietal', 'G_postcentral': 'parietal', 'G_precuneus': 'parietal',
    'S_cingul-Marginalis': 'parietal', 'S_interm_prim-Jensen': 'parietal',
    'S_intrapariet_and_P_trans': 'parietal', 'S_postcentral': 'parietal',
    'S_subparietal': 'parietal',
    'G_oc-temp_med-Parahip': 'temporal', 'G_temp_sup-G_T_transv': 'temporal',
    'G_temp_sup-Lateral': 'temporal', 'G_temp_sup-Plan_polar': 'temporal',
    'G_temp_sup-Plan_tempo': 'temporal', 'G_temporal_inf': 'temporal',
    'G_temporal_middle': 'temporal', 'Lat_Fis-ant-Horizont': 'temporal',
    'Lat_Fis-ant-Vertical': 'temporal', 'Lat_Fis-post': 'temporal',
    'Pole_temporal': 'temporal', 'S_collat_transv_ant': 'temporal',
    'S_collat_transv_post': 'temporal', 'S_temporal_inf': 'temporal',
    'S_temporal_sup': 'temporal', 'S_temporal_transverse': 'temporal',
    'G_Ins_lg_and_S_cent_ins': 'insula', 'G_insular_short': 'insula',
    'S_circular_insula_ant': 'insula', 'S_circular_insula_inf': 'insula',
    'S_circular_insula_sup': 'insula',
}


def get_bilateral_centroid(coords_l, labels_l, coords_r, labels_r, idx):
    masks = [(labels_l == idx, coords_l), (labels_r == idx, coords_r)]
    pts = [c[m].mean(axis=0) for m, c in masks if m.sum() > 0]
    if not pts:
        return [0.0, 0.0, 0.0]
    avg = np.mean(pts, axis=0)
    avg[0] = 0.0
    return [round(float(v), 1) for v in avg]


def build_regions():
    regions = []

    # Load geometry + DK parcellation
    coords, labels_dk, names_dk = {}, {}, None
    for hemi in ['lh', 'rh']:
        c, _ = fs.read_geometry(os.path.join(FSAVERAGE, 'surf', f'{hemi}.pial'))
        coords[hemi] = c
        lbl, _, names = fs.read_annot(os.path.join(FSAVERAGE, 'label', f'{hemi}.aparc.annot'))
        labels_dk[hemi] = lbl
        if names_dk is None:
            names_dk = names

    # --- MEDIUM: Desikan-Killiany bilateral cortical ---
    for i, nb in enumerate(names_dk):
        name = nb.decode() if isinstance(nb, bytes) else nb
        if name in ('unknown', 'Unknown', 'corpuscallosum'):
            continue
        centroid = get_bilateral_centroid(
            coords['lh'], labels_dk['lh'], coords['rh'], labels_dk['rh'], i)
        regions.append({
            'id': name,
            'name': DK_NAMES.get(name, name.replace('_', ' ').title()),
            'hemisphere': 'bilateral',
            'difficulty': 'medium',
            'category': 'cortical',
            'lobe': DK_LOBE.get(name, 'unknown'),
            'centroid_mni': centroid,
            'mesh_file': f'medium/{name}_L.glb',
            'mesh_files': [f'medium/{name}_L.glb', f'medium/{name}_R.glb'],
            'aliases': DK_ALIASES.get(name, []),
        })

    # --- HARD: Destrieux bilateral cortical ---
    labels_ds = {}
    names_ds = None
    for hemi in ['lh', 'rh']:
        lbl, _, names = fs.read_annot(
            os.path.join(FSAVERAGE, 'label', f'{hemi}.aparc.a2009s.annot'))
        labels_ds[hemi] = lbl
        if names_ds is None:
            names_ds = names

    for i, nb in enumerate(names_ds):
        name = nb.decode() if isinstance(nb, bytes) else nb
        if name in ('Unknown', 'Medial_wall', 'unknown'):
            continue
        l_exists = (labels_ds['lh'] == i).sum() > 0
        r_exists = (labels_ds['rh'] == i).sum() > 0
        if not l_exists and not r_exists:
            continue

        centroid = get_bilateral_centroid(
            coords['lh'], labels_ds['lh'], coords['rh'], labels_ds['rh'], i)
        regions.append({
            'id': f'ds_{name}',
            'name': DESTRIEUX_NAMES.get(name, name.replace('_', ' ')),
            'hemisphere': 'bilateral',
            'difficulty': 'hard',
            'category': 'cortical',
            'lobe': DESTRIEUX_LOBE.get(name, 'unknown'),
            'centroid_mni': centroid,
            'mesh_file': f'hard/{name}_L.glb',
            'mesh_files': [f'hard/{name}_L.glb', f'hard/{name}_R.glb'],
            'aliases': [],
        })

    # --- EASY: Lobe-level bilateral ---
    easy = [
        ('frontal_lobe', 'Frontal Lobe', 'frontal', [0.0, 26.0, 22.0]),
        ('parietal_lobe', 'Parietal Lobe', 'parietal', [0.0, -40.0, 52.0]),
        ('temporal_lobe', 'Temporal Lobe', 'temporal', [0.0, -14.0, -14.0]),
        ('occipital_lobe', 'Occipital Lobe', 'occipital', [0.0, -84.0, 8.0]),
        ('insula_bilateral', 'Insula', 'insula', [0.0, 2.0, 2.0]),
    ]
    for sid, sname, lobe, centroid in easy:
        regions.append({
            'id': sid, 'name': sname, 'hemisphere': 'bilateral',
            'difficulty': 'easy', 'category': 'cortical', 'lobe': lobe,
            'centroid_mni': centroid,
            'mesh_file': f'easy/{sid.replace("_bilateral","")}_L.glb',
            'mesh_files': [f'easy/{sid.replace("_bilateral","")}_L.glb',
                           f'easy/{sid.replace("_bilateral","")}_R.glb'],
            'aliases': ['insular cortex'] if sid == 'insula_bilateral' else [],
        })

    # --- EASY/MEDIUM/HARD: Subcortical bilateral ---
    subcortical = [
        ('brainstem', 'Brainstem', 'easy', 'brainstem',
         [0.0, -26.0, -30.0], ['brain stem'],
         ['easy/brainstem.glb']),
        ('cerebellum_cortex', 'Cerebellum', 'easy', 'cerebellum',
         [0.0, -56.0, -30.0], ['cerebellar cortex'],
         ['easy/cerebellum_cortex_L.glb', 'easy/cerebellum_cortex_R.glb']),
        ('hippocampus', 'Hippocampus', 'medium', 'temporal',
         [0.0, -20.0, -12.0], ['hippocampal formation', 'cornu ammonis'],
         ['medium/hippocampus_L.glb', 'medium/hippocampus_R.glb']),
        ('amygdala', 'Amygdala', 'medium', 'temporal',
         [0.0, -2.0, -18.0], ['amygdaloid body'],
         ['medium/amygdala_L.glb', 'medium/amygdala_R.glb']),
        ('thalamus', 'Thalamus', 'medium', 'diencephalon',
         [0.0, -16.0, 8.0], ['dorsal thalamus'],
         ['medium/thalamus_L.glb', 'medium/thalamus_R.glb']),
        ('caudate', 'Caudate Nucleus', 'medium', 'basal_ganglia',
         [0.0, 6.0, 14.0], ['caudate'],
         ['medium/caudate_L.glb', 'medium/caudate_R.glb']),
        ('putamen', 'Putamen', 'medium', 'basal_ganglia',
         [0.0, 0.0, 4.0], [],
         ['medium/putamen_L.glb', 'medium/putamen_R.glb']),
        ('pallidum', 'Globus Pallidus', 'medium', 'basal_ganglia',
         [0.0, -4.0, 2.0], ['GP', 'globus pallidus'],
         ['medium/pallidum_L.glb', 'medium/pallidum_R.glb']),
        ('accumbens', 'Nucleus Accumbens', 'hard', 'basal_ganglia',
         [0.0, 12.0, -6.0], ['NAcc', 'ventral striatum'],
         ['hard/accumbens_L.glb', 'hard/accumbens_R.glb']),
    ]
    for sid, sname, diff, lobe, centroid, aliases, files in subcortical:
        regions.append({
            'id': sid, 'name': sname, 'hemisphere': 'bilateral',
            'difficulty': diff, 'category': 'subcortical', 'lobe': lobe,
            'centroid_mni': centroid,
            'mesh_file': files[0],
            'mesh_files': files,
            'aliases': aliases,
        })

    return {'regions': regions}


os.makedirs('data', exist_ok=True)
output = build_regions()
with open('data/regions.json', 'w') as f:
    json.dump(output, f, indent=2)

by_diff = {}
for r in output['regions']:
    by_diff.setdefault(r['difficulty'], []).append(r['id'])
for d, ids in sorted(by_diff.items()):
    print(f"  {d}: {len(ids)} regions")
print(f"Total: {len(output['regions'])} -> data/regions.json")
