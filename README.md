# Neurdle

A daily neuroanatomy guessing game. Identify a 3D brain region — receive feedback on distance, proximity, and anatomical direction after each guess.

**Live:** [neurdle.com](https://github.com/AlexanderAtalay/neurdle) · **Created by** [Alexander Atalay](https://alexanderatalay.com)

---

## Gameplay

- A 3D brain region is shown. Rotate it freely with your mouse or finger.
- Guess which region it is from the autocomplete list.
- After each wrong guess: **distance (mm)**, **proximity %**, and **directional arrows** (↑A/↓P · ↑S/↓I · →L/←M) tell you how close you are.
- After guess 3: a ghost brain outline appears for spatial context.
- Win in 6 guesses or fewer.
- **Three difficulty tiers:**
  - 🔵 **Easy** — brain lobes, cerebellum, brainstem
  - 🟡 **Medium** — 34 Desikan-Killiany cortical regions + major subcortical structures
  - 🔴 **Hard** — 74 Destrieux atlas regions (fine gyri and sulci)
- **Training mode** — unlimited play with ghost brain always visible and wrong guesses shown at low opacity.

---

## Project Structure

```
neurdle/
├── neurdle/              # Next.js web app (deployed to Netlify)
│   ├── public/
│   │   ├── meshes/       # 3D brain region meshes (.glb)
│   │   └── data/         # regions.json + distance maps
│   └── src/
│       ├── app/          # Next.js App Router pages
│       ├── components/   # React components
│       ├── hooks/        # Game logic hooks
│       ├── lib/          # Utility functions
│       ├── store/        # Zustand state
│       └── types/        # TypeScript types
├── pipeline/             # Mesh generation scripts (not deployed)
│   ├── extract_cortical_meshes.py
│   ├── extract_subcortical_meshes.py
│   ├── extract_whole_brain.py
│   ├── extract_brodmann_areas.py
│   ├── generate_lobe_meshes.py
│   ├── convert_to_glb_python.py
│   ├── compute_distances.py
│   ├── build_regions_json.py
│   ├── merge_bilateral_distances.py
│   └── neurdle-plan.md
├── data/                 # Generated data files (gitignored raw outputs)
│   └── distances_bilateral.json  # ← committed, used by the app
├── netlify.toml
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router, static export) |
| 3D rendering | Three.js · `@react-three/fiber` · `@react-three/drei` |
| Styling | Tailwind CSS |
| State | Zustand (persisted to localStorage) |
| Hosting | Netlify |

---

## Deployment (Netlify)

The app is configured for automatic deployment from this repo.

1. Connect this repo to Netlify.
2. Netlify reads `netlify.toml` — build runs from `neurdle/`, publishes `out/`.
3. No environment variables required.

For manual deployment:
```bash
cd neurdle
npm install
npm run build   # outputs to neurdle/out/
```

---

## Data Pipeline (for contributors / regenerating meshes)

Brain region meshes are derived from [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/)'s `fsaverage` subject using the Desikan-Killiany and Destrieux parcellation atlases.

### Prerequisites

```bash
# FreeSurfer (macOS/Linux)
export FREESURFER_HOME=/path/to/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# Python packages
pip install nibabel trimesh fast-simplification scikit-image scipy numpy
```

### Run order (from repo root)

```bash
python pipeline/extract_cortical_meshes.py      # Desikan-Killiany + Destrieux OBJs
python pipeline/extract_subcortical_meshes.py   # aseg subcortical OBJs
python pipeline/extract_whole_brain.py          # ghost brain OBJs
python pipeline/generate_lobe_meshes.py         # merged lobe GLBs (easy mode)
python pipeline/convert_to_glb_python.py        # all OBJ → GLB
python pipeline/build_regions_json.py           # master regions.json
python pipeline/compute_distances.py            # pairwise distance maps
python pipeline/merge_bilateral_distances.py    # merge L/R → bilateral

# Copy outputs to app
cp -r data/meshes/* neurdle/public/meshes/
cp data/regions.json data/distances_bilateral.json neurdle/public/data/
```

---

## Atlas & Data Credits

- **Brain atlas data:** [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) `fsaverage` subject
  - Desikan-Killiany atlas: Desikan et al. (2006), *NeuroImage*
  - Destrieux atlas: Destrieux et al. (2010), *NeuroImage*
- **Heavy Inspiration:** [Wordle](https://www.nytimes.com/games/wordle) (NYT) · [Worldle](https://worldle.teuteuf.fr) (teuteuf)

---