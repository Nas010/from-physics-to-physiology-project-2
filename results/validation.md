# Validation record — 2026-10-08

- Notebook schema validated. All **35 code cells** executed in order from a fresh kernel with **zero cell errors**. The revised notebook was executed again on 8 October after adding course explanations and correcting the physical surface-friction coefficient. The same correction reaches the conventional volume-manifest pathway.
- **Friction regression passed:** the old dimensionless coefficient fails an independently derived wall-shear/perimeter force check; multiplication by kinematic viscosity restores the correct force units. The notebook now executes this assertion.
- **8 local numerical checks passed on 6 October (unchanged methods):** exact triangle quadrature and zero-flow masking; profile constants; steady Poiseuille mass/momentum balance; pulsatile Womersley flow, no-slip and force balance; complete-cycle/missing-frame/mesh/input validation; selecting the correct vessel limb; linear tetrahedral interpolation and outside-domain rejection; signed inward wall derivative and Poiseuille friction.
- Notebook also executes a **filled 3D pulsatile-tube verification** and a clearly labelled **manufactured narrowing** balance check.
- **45 independent raw-VTU comparisons passed on 6 October (unchanged compact data/interpolation)** (three actual frames × three section stations × five metrics: Q, mean pressure, alpha, secondary velocity ratio and pressure range). See `validation_source_sections.csv` for values and tolerances. Source sections were cut directly from raw fields independently of compact cached stencils.
- Compact actual dataset covers **201 snapshots and 47 eligible stations**. Source SHA-256, parameter signatures, SI conversion and exclusions are recorded in `run_manifest.json` and `data/actual_volume_sections.json`. The downloaded ZIP CRC was verified while extracting the raw VTU.
- The earlier actual-flow, pressure, assumption-flag and momentum figures were visually inspected on 6 October. The revised teaching text and corrected surface-friction figures were visually inspected on 8 October. All 38 local source links and the hashes of five current Canvas teaching files were checked. HTML images load and equations render with bundled offline MathJax.
- ParaView script syntax passed. Native ParaView execution was not performed because ParaView is not installed here; its script is optional. The default notebook does not require ParaView.

## Scope

The default notebook reruns locally from bundled inputs without downloads. The original 5.55 GB volume remains outside this ZIP; download/re-extraction instructions are included for changed geometry or spacing. Actual interior metrics are recomputed from pressure/velocity fields, not stored scalar conclusions.

This is a healthy rigid aorta, with no documented anatomical stenosis. Manufactured narrowing validates code only. Branch/low-flow/derivative masks, near-wall probe sensitivity and single-cycle limitations remain material when interpreting residuals. These checks establish computational consistency; they do not establish clinical accuracy or universal validity of 1D models.
