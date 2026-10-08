
### Executed findings for supplied healthy rigid aorta
- **Actual A5 global cap balance:** maximum mismatch / peak inlet flow = **2.18e-05%**; integrated signed mismatch = **-2.92e-07%** over **0.937 s**.
- **Actual inlet flow:** mean **96.67 mL/s**, peak **501.96 mL/s**.
- **Actual wall shear:** area-weighted mean TAWSS **2.138 Pa**; nodal OSI median **0.102**.
- **Geometry:** **47** usable main-vessel stations out of **62** after open-contour and branch exclusions. No stenosis diagnosis inferred.
- **A4 exploratory comparison:** wall-shear magnitude and circular-profile friction estimates are compared with low-flow masks; this is not a signed-force residual.
- **Actual A1/A2/A3/A6:** volume results analysed; inspect exported maps and residual term budgets.
- **Actual measured-closure residual:** median **0.012**, 95th percentile **0.175**, with excluded edges/branches/low flow. Poiseuille median **0.046** on the same finite station/phase pairs.
- **Actual local mass:** maximum section-vs-cap mismatch / peak inlet Q **0.350%**.
- **Verified reference:** Poiseuille mass/momentum closure and pulsatile Womersley flux, wall no-slip and analytic momentum closure.

All Project 2 core computations now use actual interior velocity/pressure from the matching volume source. Residual interpretation remains limited by 1D pressure reduction, near-wall reconstruction, centerline/derivative choices and branch exclusions. This healthy geometry does not test an anatomical stenosis; the manufactured narrowing is only a code check.
