# Figure guide — healthy aorta, 14 October 2026

All anatomy and actual simulation fields in this notebook belong to **0012_H_AO_H**, the selected healthy rigid aorta. The internal file name **0095_0001** is its legacy identifier. The public [model catalogue](https://www.vascularmodel.com/dataset/dataset-svprojects.csv) and [results catalogue](https://www.vascularmodel.com/dataset/dataset-svresults.csv) identify the same case. Healthy describes the supplied anatomy; it does not imply a straight vessel, a parabolic velocity profile or negligible secondary flow.

Some figures deliberately contain mathematical reference profiles. Those curves are comparisons with the selected aorta, and the standalone Womersley figure checks the calculation in a synthetic tube. They should be described that way in the presentation.

## Concepts used throughout

- **Actual** means geometry or fields from this case's 3D simulation. It does not mean an independent experiment or patient measurement.
- **Reference** means an analytical straight circular tube. **Comparison** puts actual fields and a reference together.
- **s** is distance along the main centreline, measured from the inlet. The maps use millimetres horizontally and cycle fraction, from 0 to 1, vertically.
- The archive contains 201 snapshots and 47 usable sections. Branch neighbourhoods and unsuitable sections are excluded. The prepared runs are approximately 15–39 mm and 103–259 mm. Spatial derivatives stay within each run, and residuals exclude its endpoints and the first/last time samples.
- The detailed example is station 46, approximately **199 mm** from the inlet in the descending aorta. Its peak-flow snapshot is at cycle fraction **0.10**. Quarter and half interval mean positions in the saved cycle; they have not been identified as particular physiological phases.
- White gaps mean an unavailable or excluded calculation. They do not mean zero error. All time snapshots exist, even where a derived quantity is masked.
- **α** here is the momentum profile correction, `(area-average axial velocity squared) / (mean axial velocity squared)`. It is a different quantity from the Womersley number, which some lecture notation also calls α.
- **f** is the signed wall-friction term after division by density, in m³/s². It is not wall shear stress in pascals. The actual estimate uses near-wall velocity probes and a no-slip derivative approximation.

## Every figure, in notebook order

### 1. Aorta and centreline — Actual

[Open figure](results/figures/aorta_geometry.png). Grey points show the supplied aortic wall; orange shows the selected main-vessel centreline. Coordinates are in mm, with equal physical scales on the three axes. The preview samples wall points, so its faint appearance is a rendering choice. The branches and arch are part of the healthy model. This figure identifies the anatomy; it does not show the locations where the 1D assumptions fail.

### 2. Inlet/outlet flows and global mass mismatch — Actual

[Open figure](results/figures/cap_flows_and_mass.png). The upper panel plots volume flow in mL/s through the inlet and each outlet over the cycle. The lower panel plots inlet flow minus the sum of outlet flows, divided by peak inlet flow and expressed as a percentage. Cap-normal sign conventions are converted to positive inflow/outflow for this comparison. The maximum mismatch is about **0.0000218% of peak inlet flow**, supporting global incompressible conservation in the supplied simulation. This alone cannot validate section measurements or momentum closure.

### 3. Section area, flow and mean pressure — Actual

[Open figure](results/figures/section_area_flow_pressure.png). Three panels show area in mm², flow in mL/s and section-average pressure in kPa against distance at the same selected peak-flow time. A smaller main-vessel flow after a branch is expected because flow has left through that branch. Pressure is an area-weighted section mean, not a centreline point value. Gaps are excluded sections. The area varies along the anatomy, while the rigid-wall model keeps each section's area constant over time.

### 4. Section flow minus cap-based continuity — Actual

[Open figure](results/figures/local_mass_balance.png). Colour shows directly integrated section flow minus inlet flow after subtracting upstream branch outflows, as a percentage of peak inlet flow. It tests whether the section extraction agrees with the cap measurements. The maximum absolute difference is **0.350%**. This is a local flow-consistency check, separate from the momentum residual and from physiological accuracy.

### 5. Reynolds and Womersley numbers — Derived from actual flow

[Open figure](results/figures/flow_regime_numbers.png). The upper panel plots `Re_D = |U| D / ν` at the selected peak-flow time. The lower plots `Wo = (D/2) sqrt(2π/(Tν))`, using the fundamental cycle frequency. Here `U = Q/A` and `D = 2 sqrt(A/π)` is the area-equivalent diameter. Reynolds uses diameter; Womersley uses radius. Wo is constant in time at each station because the model is rigid and T and ν are fixed.

At the 199 mm example, **Re_D ≈ 4,997** and **Wo ≈ 12.58**. Across usable sections, Wo ranges from about **12.35 to 17.65**. These numbers support significant inertia and pulsatility and help explain why a steady Poiseuille profile is an imperfect reference. A transient high Reynolds number does not establish turbulence, especially by applying a steady straight-pipe threshold to a curved pulsatile vessel. See `sources/course/dynamic_circulation.pdf`, pages 21–27, for the lecture conventions and regime discussion.

### 6. Womersley straight-tube check — Reference only

[Open figure](results/figures/womersley_check.png). This uses a **synthetic circular tube of radius 10 mm**, with prescribed mean velocity `0.2 + 0.08 cos(2πt/T)` m/s. Horizontal position is r/R; vertical position is axial velocity in m/s. Curves show four phases. The analytical checks recover bulk flow, zero wall velocity and the expected balance. The plot tests the reference calculation; it is not another aortic model or extracted aortic data. A slide must label it as a reference/check.

### 7. Aortic velocity profiles with Womersley overlays — Comparison

[Open figure](results/figures/aortic_velocity_profiles.png). Points are actual axial velocities from the 199 mm section at peak flow, quarter interval and half interval. Horizontal position is distance from the centreline divided by equivalent radius; the vertical axis is m/s. Points at the same radius retain their different angular locations, so their spread reveals asymmetry. Some points exceed r/R = 1 because the actual section is not perfectly circular or centred on the ideal circle.

Dashed curves use this section's mean-velocity history, equivalent radius, viscosity and matching phases in the Womersley reference. The spread and departures from those curves show what an axisymmetric straight-tube profile misses. The curves are not a second simulation of this aorta. Reverse axial velocity at some points can coexist with small forward net flow.

### 8. Section pressure and axial velocity at peak flow — Actual

[Open figure](results/figures/section_pressure_velocity.png). Both panels show the actual filled section in its local plane, in mm. The first colours pressure minus the area-weighted section mean, in Pa, so it reveals transverse pressure variation without the large baseline pressure. The second colours signed axial velocity in m/s. Uneven colours demonstrate nonuniform pressure/velocity. This example is in the descending aorta; it does not show arch Dean vortices.

### 9. Secondary-flow, pressure and profile maps — Actual derived metrics

[Open figure](results/figures/pressure_and_profile_maps.png). The four panels share distance and cycle axes:

| Panel | Meaning and interpretation |
|---|---|
| Secondary / axial RMS | Ratio of area-weighted RMS transverse velocity to RMS axial velocity. Small values support predominantly axial motion. Large values show secondary motion relative to axial motion, and can also reflect a smaller axial denominator. This uses RMS velocities, so cancellation in net Q does not directly cause the low-net-flow mask used below. |
| Pressure range / dynamic pressure | `(max P − min P)/(ρU²/2)`. Compares transverse pressure variation with a kinetic scale. Values can grow as bulk velocity decreases; they are not a percentage of absolute pressure. |
| Pressure range / axial drop | `(max P − min P)/(|dP̄/ds| Δs)`, with Δs about 4 mm. Tests transverse pressure variation against what the 1D model tracks over one section spacing. The comparison depends on spacing and the pressure gradient; a large value alone does not prove the model invalid. |
| Momentum correction α | Shape factor for the axial momentum flux. Uniform velocity gives 1 and a Poiseuille parabola gives 4/3. Larger values can arise from uneven profiles and opposing velocities with small net flow. It is not a disease indicator. |

Pressure ratios and α are masked below **5% of that section's peak absolute net flow**. The axial-pressure ratio also requires an axial drop above 0.01 Pa. Secondary RMS is only undefined where axial energy is effectively zero; it is not subject to that same net-flow mask. The last three panels use logarithmic colours.

### 10. Profile-factor comparison at 199 mm — Comparison

[Open figure](results/figures/profile_factor_comparison.png). This plots α over the cycle for the actual section, fixed Poiseuille α = 4/3, fixed ζ = 9 α = 1.1 and the local Womersley reference. The real peak-flow profile is relatively blunt, near the ζ = 9 value. Later low-net-flow phases do not have a displayed measured α. The Womersley curve uses the same bulk-flow history but assumes a straight circular tube, so agreement in α does not establish agreement in every local velocity.

### 11. Friction comparison at 199 mm — Comparison

[Open figure](results/figures/friction_comparison.png). Signed f in m³/s² is plotted over the cycle. References use `f = 8πνQ/A` for Poiseuille, `f = 22πνQ/A` for ζ = 9, and the unsteady local Womersley solution. The actual curve is estimated from near-wall probes. A pulsatile near-wall velocity gradient can differ in magnitude or sign from a steady law based on instantaneous bulk flow. Treat differences as closure/probe differences, not a direct measurement of clinical wall stress.

### 12. Profile factor and friction along the vessel — Comparison

[Open figure](results/figures/profile_and_friction_along_vessel.png). This repeats the α and f comparisons spatially at one common peak-flow time, over every usable station. A vertical marker identifies the 199 mm example. In the downstream run, measured α is approximately 1.06–1.09, close to the blunt ζ = 9 reference; proximal values are higher. Measured downstream friction exceeds both steady references at this time. The example reflects the downstream profile reasonably at this snapshot, while its friction does not describe all stations. This plot covers the available runs, not the excluded arch/branch region and not every station's separate local peak time.

### 13. Normalised momentum residual maps — Actual data with three closures

[Open figure](results/figures/momentum_residual_maps.png). **Poiseuille is the first title; “PSI” is not a pressure unit used here.** All three panels use exactly the same actual A, Q and mean P from this aorta. They change the momentum-profile correction α and friction f:

| Closure | α | f |
|---|---|---|
| Poiseuille | 4/3 | 8πνQ/A |
| ζ = 9 | 1.1 | 22πνQ/A |
| Measured α and f | Derived from the actual section profile | Near-wall probe estimate from the same simulation |

The calculation adds the four signed terms in the conservative 1D balance:

`R = ∂Q/∂t + ∂(α Q²/A)/∂s + (A/ρ) ∂P̄/∂s + f`.

Each term and R has units m³/s². The plotted number is dimensionless:

`|R| / max(|unsteady| + |convective| + |pressure| + |friction|, floor)`.

The floor is 0.001 times the maximum summed magnitude for that run and closure, with an absolute minimum of 10⁻¹² m³/s². It prevents tiny denominators from controlling the plot. Zero indicates cancellation of the terms; 0.1 is a remaining imbalance equal to one tenth of this term scale. It is **not a 10% error in blood flow, pressure or physiological prediction**.

Dark colours indicate smaller residuals and light colours larger ones. The colour scale stops at **0.5**, so values above 0.5 share the brightest colour. Full values remain in the CSVs. The reference panels contain 8,557 valid station–time pairs; the measured panel has 2,878 because masked α also affects its spatial derivative. Its white region after approximately 0.3 of the cycle is a methodological exclusion, not evidence of perfect balance or absent flow. Some values return near the end of the cycle.

For a fair comparison, the table below uses the **same 2,878 valid pairs for all five closures**:

| Closure | Median residual | 95th percentile |
|---|---:|---:|
| Poiseuille | 0.04559 | 0.49578 |
| ζ = 9 | 0.04362 | 0.45431 |
| Measured α and f | **0.01165** | **0.17512** |
| Measured α, Poiseuille f | 0.04720 | 0.25116 |
| Poiseuille α, measured f | 0.04676 | 0.41883 |

Using both measured quantities reduces the median residual on matched samples. Changing only one does not improve the median here, although it changes the upper tail. The effects cannot be added independently: signed terms cancel and the normalisation changes with the terms. These results do not justify a single universal ranking of “α matters more” or “friction matters more.” Measured quantities come from the same simulation used to form the balance, so a smaller residual shows greater computational consistency, not independent validation of a predictive 1D model.

### 14. Momentum-term budget — Derived from actual fields

[Open figure](results/figures/momentum_term_budget.png). At 199 mm, this plots the signed unsteady, convective, pressure and measured-friction terms against cycle fraction, with the resulting residual. The vertical units are m³/s². Individual terms can be large while their sum is small. Measured α masking makes the convective term and resulting residual unavailable at some times; other available terms can still be shown. This plot explains the balance behind the colour map.

### 15. Residual over the cycle — Five-closure comparison

[Open figure](results/figures/residual_over_cycle.png). The upper panel takes the median residual across the same available locations for all five closures at each time. The lower panel shows how many locations contribute. The locations can change between times, so a temporal change is not exclusively a change in flow physics. No curve is drawn where the common count is zero. The broad gap reflects measured-α masking; it does not mean the reference closures lack data there. The spike near cycle fraction 0.32 coincides with rapidly shrinking common coverage and should be read with the count panel.

### 16. Residual versus centreline curvature — Spatial comparison

[Open figure](results/figures/curvature_residual_comparison.png). Each point is one of **43 paired locations** at the same selected peak-flow time. The horizontal axis is curvature in 1/m and the vertical axis is the unclipped normalised residual. The three colours use the three main closures on those same locations. No consistent increasing trend appears across all closures: Spearman correlations are about −0.076, 0.170 and 0.254 for Poiseuille, ζ = 9 and measured respectively. These are descriptive values, not independent statistical samples or causal evidence. The excluded branch region contains important curvature and limits conclusions about the arch. Present this as a test of the curvature hypothesis, not confirmation that bending explains the residual.

### 17. Near-wall sampling sensitivity at 199 mm — Numerical sensitivity

[Open figure](results/figures/wall_probe_sensitivity.png). Two signed f estimates use velocity probes 0.30 and 0.15 mm from the wall. Their difference over the cycle shows sensitivity to the sampled near-wall gradient. Close agreement supports stability with respect to these two probe depths at this section; it does not establish the true wall force, spatial mesh convergence or accuracy everywhere.

### 18. Probe sensitivity across all usable sections — Numerical sensitivity

[Open figure](results/figures/probe_sensitivity_all_sections.png). The histogram contains **9,447 section–time samples**: 47 stations × 201 snapshots. The horizontal axis is `100 |f_0.15 − f_0.30| / max_cycle |f_0.30|`, with a separate peak-force denominator for each station. This avoids dividing by a force close to zero at an individual time. The median is **0.274%** and the 95th percentile **5.19%**; the largest difference is **50.69%** of the relevant section's peak force. Most differences are small, with a local tail that should not be hidden by the median. Samples are correlated in space/time, and this is a sensitivity measure, not independent accuracy.

## Presentation conclusions supported by these figures

The supplied healthy aorta has consistent global and local flow measurements. Its actual profiles, pressure differences and secondary motion provide reasons to test simple 1D closures. On matched samples, the measured α-plus-friction closure has a smaller momentum residual than the two fixed references. The peak-flow curvature scatter does not establish a common monotonic relation between curvature and residual. State explicitly that low-flow masking restricts the measured comparison and that wall-force estimates are approximate.

An arch quiver plot was not added: the prepared usable sections omit that region. A descending-section vector plot would not support a claim about arch Dean vortices. That addition requires appropriately extracted arch fields and a separately inspected section.

## Where the calculations and evidence live

The notebook contains the short calculations and figure cells. `aorta_functions.py` implements the section integrals, reference profiles, five closure combinations and `balance_terms()` normalisation. `results/` contains full CSV values; `results/figures/` contains all 18 plots as PNG and SVG. `results/validation.md` records the completed checks and their dates.

The 14 October audit matched model/source identifiers and geometry, checked 42 finite metrics by independent triangle integration on nine cached section–time pairs, and reconstructed the original residual arithmetic and figure. The update ran all 26 notebook code cells with no errors. The six original core CSVs remain byte-for-byte identical, while regression checks verify the new flow-number conventions, mixed terms and matched samples. Full extraction from the 5.55 GB raw volume was not repeated. These checks establish provenance and computational consistency; they do not establish physiological accuracy or mesh convergence.
