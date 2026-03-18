# Neurdle

A daily neuroanatomy guessing game. Identify a 3D brain region using feedback on distance, proximity, and anatomical direction after each guess.

**Live:** [neurdle.com](https://github.com/AlexanderAtalay/neurdle) · **Created by** Alexander Atalay (asatalay@stanford.edu)

---

## Gameplay

- A 3D brain region is shown in the context of a glass brain.
- Try to guess which region it is.
- After each wrong guess: **distance (mm)**, **proximity %**, and **directional arrows** (↑A/↓P · ↑S/↓I · →←M/←→L) tell you how close you are.
- Win in 6 guesses or fewer.
- **Three difficulty tiers:**
  - **Easy**: brain lobes, cerebellum, brainstem
  - **Medium**: 34 Desikan-Killiany cortical regions + major subcortical structures + brainstem subregions + ventricular system + corpus callosum + major white matter tracts
  - **Hard**: 74 Destrieux atlas regions (fine gyri and sulci)
- **Practice mode**: unlimited puzzles.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router, static export) |
| 3D rendering | Three.js · `@react-three/fiber` · `@react-three/drei` |
| Styling | Tailwind CSS |
| State | Zustand (persisted to localStorage) |

## Atlas & Data Sources

- **Brain atlas data:** [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) `fsaverage`
  - Desikan-Killiany atlas (Desikan et al., 2006)
  - Destrieux atlas (Destrieux et al., 2010)
  - Brainstem subregions: [FreeSurfer Brainstem Probabilistic Atlas](https://freesurfer.net/fswiki/BrainstemSubstructures) (Iglesias et al., 2015)
- **White matter tracts:** [HCP1065 population-averaged tractography](https://brain.labsolver.org/hcp_template.html) (Yeh et al., 2022)

---