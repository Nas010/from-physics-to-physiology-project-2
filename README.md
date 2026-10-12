# From Physics to Physiology — Project 2

Open `FtP_Aorta_1D_Assumptions.ipynb` for the analysis, or `notebook.html` to read the saved results without Python. Keep `assets/` beside the HTML so the equations work offline.

The notebook uses the allowed healthy aorta model, 0012_H_AO_H. It follows the three core Project 2 tasks:

1. Measure area, flow, mean pressure and velocity profiles in actual 3D sections; check conservation and a Womersley reference.
2. Map pressure variation and compare profile shape and friction with reference profiles.
3. Evaluate the 1D momentum residual along the curved vessel, excluding branch junctions from single-vessel derivatives.

## Run

Install [Git LFS](https://git-lfs.com/) before cloning so the two large data files download correctly. Use 64-bit Python 3.12.

```bash
git lfs install
git clone https://github.com/Nas010/from-physics-to-physiology-project-2.git
cd from-physics-to-physiology-project-2
```

Then install the Python environment and run the analysis:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
# Windows activation instead: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

`main.py` runs every notebook cell, saves the executed notebook and refreshes `notebook.html`. Alternatively, run `python -m jupyter lab`, open the notebook with this environment's kernel, and restart/run all cells. Save it before running `python export_html.py` to update the preview.

The default run uses the included data, with no downloads or credentials. Allow about 1–3 minutes and roughly 6 GB free RAM. The environment was tested on macOS ARM64; other platforms need wheels for the pinned packages. Package versions are saved quietly in `results/run_manifest.json`.

## Supporting scripts

The notebook has the short calculations, equations and plots. Longer functions are kept in these files, which are referenced in the notebook and included in this folder:

| File | Purpose |
|---|---|
| `aorta_functions.py` | Geometry, section integration, reference profiles and momentum calculations |
| `prepare_volume.py` | Optional preparation of section data from the original volume |
| `main.py` | Run the notebook and refresh its HTML preview |
| `export_html.py` | Refresh HTML after saving a notebook edited in Jupyter |
| `paraview_preview.py` | Optional ParaView view of the exported geometry and section |

Figures and CSV tables are in `results/`. The last cell also exports `aorta_wall.vtp`, `main_centerline.vtp` and `example_section.vtp`. Open those files in ParaView, or run `pvpython paraview_preview.py` using a separate ParaView installation.

## Data

`data/0012_H_AO_H/` preserves the supplied model. `sources/` contains the original project and teaching material. The surface results and prepared section fields cover 201 snapshots of one cycle.

`data/actual_volume_sections.npz` contains actual pressure and velocity values on filled sections from the matching 3D volume. The notebook recomputes the section measurements and balances from those fields. It checks that the model, sampling, units and viscosity match the preparation record in `data/actual_volume_sections.json`.

The raw volume is 5.55 GB and is excluded from the group ZIP. Its public retrieval URL and SHA-256 are recorded in the preparation record. It is only needed to repeat extraction. After obtaining and unzipping the original archive, run:

```bash
python prepare_volume.py /path/to/0012_H_AO_H_3D_RIGID.vtu
```

This replaces the prepared section data after extraction succeeds. Keep the default geometry and extraction settings for the normal analysis. Changing those settings requires editing the preparation and analysis together, then preparing the data again. The low-flow threshold can change without extraction.

## Interpretation and sharing

The healthy model meets the agreed project scope. Its rigid wall and single cycle limit the conclusions. Near-wall force uses velocity probes at 0.30 and 0.15 mm depth; their comparison helps assess sampling sensitivity. Small momentum residuals show consistency of the projected balance, not physiological accuracy or mesh convergence.

Share this repository with the group. After cloning, use `git pull` to receive updates; keep Git LFS installed. Share a complete folder when working offline, including the scripts, data, assets and sources. Preserve the model LICENSE and README-COPYRIGHT. `results/validation.md` records the checks and their dates.

## Presentation

The [`presentation/`](presentation/) folder contains the course presentation, with 12 main slides and two backups. It targets an 11-minute talk, followed by discussion. Rosalie presents slides 1–6 and Mark presents slides 7–12, with speaker notes embedded in every slide.

- [Editable PowerPoint](presentation/FtP_Project2_Aorta_Presentation.pptx)
- [Static PDF preview](presentation/FtP_Project2_Aorta_Presentation.pdf)
- [Speaker notes, timings and discussion guide](presentation/Speaker_Notes_and_Course_Guide.md)
- [Complete presentation package](presentation/FtP_Project2_Presentation_Package.zip)

The PDF is an image preview. Edit and rehearse the PowerPoint with the group. Model notices are included with the slides and in the package.

Notebook, supporting code and presentation drafting were assisted by AI. Review the work and record actual group contributions for submission. The group still needs to write and review its report.
