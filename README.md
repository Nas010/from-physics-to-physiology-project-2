# From Physics to Physiology — Project 2

Start with `FtP_Aorta_1D_Assumptions.ipynb`. Read saved outputs without Python in `notebook.html`; equations render offline using the bundled `assets/` folder. To refresh the HTML after a rerun, save the notebook and run `python export_html.py`. This bundle covers Project 2 core work from `FP2P_projects_Simone.pptx`, slide 2, plus the group's A1–A6 working plan.

## Read and understand

The 8 October revision adds a short introduction, the physical reasoning behind each method, code walkthroughs and guides to every major figure. Course citations link to the bundled originals in `sources/course/`; exact Canvas file IDs and hashes are in `sources/course_sources.json`.

Read the introduction, then Physics and conventions. Run the methods-library cells to define the functions; Sections 3–8 apply them. Each main calculation now explains why it is needed and how to interpret its output. Saved numerical observations describe the default run; update the prose if you change data or parameters.

A surface-friction reference bug was also corrected: the dimensionless value `KR/nu` is now multiplied by kinematic viscosity before use. An independent Poiseuille shear-to-force check guards the conversion. The same corrected coefficient is used by the conventional volume-manifest pathway; the packed actual-volume momentum calculations already used the physical coefficient.

## Run

1. Install [Git LFS](https://git-lfs.com/) once, then clone this repository. Keep the notebook beside `data/`, `sources/`, and `requirements.txt`.

```bash
git lfs install
git clone https://github.com/Nas010/from-physics-to-physiology-project-2.git
cd from-physics-to-physiology-project-2
```

The two largest data files use Git LFS. Without Git LFS, cloning retrieves only small pointer files for them. The [complete ZIP release](https://github.com/Nas010/from-physics-to-physiology-project-2/releases/tag/v1.0) is an alternative that needs no Git LFS.
2. Install Python 3.12 (64-bit). In this folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
# Windows activation instead: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m ipykernel install --prefix .venv --name ftp-aorta --display-name "FtP aorta (Python 3.12)"
python -m jupyter lab
```

3. Select FtP aorta kernel. Restart Kernel and Run All Cells.

Default run uses local inputs only, no downloads or credentials. Expect roughly 2–5 minutes, with initial VTK import and 3D verification possibly slower on first run. Recommend 6 GB free RAM and several GB disk. Tested on macOS ARM64; exact environment is recorded in `results/run_manifest.json`. Other supported platforms need matching Python wheels. If installation fails, verify Python 3.12 and 64-bit architecture before changing package versions.

## Core work

- Actual filled 3D sections: A, Q, mean P, axial/secondary velocity, profiles, local/global mass checks, Wo/Re/Dean.
- Actual pressure non-uniformity maps, measured alpha, Poiseuille/ζ=9/Womersley reference comparisons, wall-friction reconstruction.
- Actual conservative momentum residual, closure ablations, threshold and numerical sensitivity, branch exclusion masks.
- Verified filled 3D Womersley tube and manufactured variable-area narrowing. Synthetic/reference cases are explicitly labelled.

The chosen model is a documented healthy aorta. It tests bends and branch/area variation, with no documented anatomical stenosis. Manufactured narrowing checks code only; ask instructor whether a second stenotic anatomy is required for the stated geometry scope. No extra 0D/1D solver or closure fitting was added.

## Data and provenance

`data/0012_H_AO_H/` preserves supplied model folder. `sources/` preserves supplied PDFs, summary, project slides and public metadata. Supplied surface VTP has velocity and WSS for steps 10040–11040 every five solver steps.

Matching volume archive was obtained from the public model repository:
https://www.vascularmodel.com/svresults/0012_H_AO_H/0012_H_AO_H_3D_RIGID_VTU.zip

The extracted raw VTU is 5.55 GB. To keep group sharing practical, this bundle contains `data/actual_volume_sections.npz`: actual nodal pressure/velocity on filled sections for every supplied snapshot, with source hash, geometry and interpolation provenance. Notebook recomputes all metrics from these fields, not cached claims. Raw volume remains outside the share bundle; its retrieval URL and SHA-256 are recorded. Geometry, spacing, viscosity or branch-mask changes require re-extraction using embedded notebook code and the raw archive. Low-flow thresholds can change without re-extraction.

Near-wall signed friction uses no-slip normal derivatives at 0.30 and 0.15 mm probe depth; inspect their sensitivity before treating residual as physical model error. Supplied WSS sign convention is not independently documented; surface comparisons use magnitudes. Rigid walls cannot assess compliance. Single cycle cannot prove cycle-to-cycle convergence. Masks identify unavailable derivative regions.

## Share

Share this repository link with the group. After the initial clone, use `git pull` to receive updates. Keep Git LFS installed so large data files download with the rest of the project. Notebook contains all analysis functions, comments, docstrings and explanations. `results/` holds CSV, PNG/SVG, findings, validation and provenance. Preserve model LICENSE and README-COPYRIGHT in every copy containing model-derived data. The repository and release ZIP are public.

ParaView: install separately, open `results/actual_wall_metrics.vtp`, `main_centerline.vtp` or `cap_velocity_cycle.pvd`. Optional `paraview_preview.py` runs under ParaView's pvpython; ordinary notebook Python does not import paraview. Script syntax is checked; native ParaView execution depends on its installation.

Group should review methods, rerun, interpret results and record actual contributions. AI-assisted drafting is disclosed in notebook; follow course authorship requirements.
