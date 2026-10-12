# Course presentation and speaker notes

The presentation has 12 main slides, timed for an 11-minute talk, followed by approximately 3 minutes of discussion. Slides 13–14 are backups.

Rosalie Post presents slides 1–6 (4 min 55 s). Mark Bongers presents slides 7–12 (6 min 5 s). This split follows the presenter names in the attached plan and can be changed during rehearsal.

## Course requirements found

- Current Simone guidelines, page 2, and Ed guidelines, page 1: follow the report structure, with 11 minutes of presentation plus 3 minutes of discussion. The presentation contributes 20% of the grade.
- Current syllabus: the presentation takes place on 16 October within a 15-minute slot including discussion. Submit the presentation and report by 15:00 that day. The group plan sets 14 October as its internal finishing date and 15 October for rehearsal.
- No dedicated presentation template or detailed scoring rubric appeared in accessible course files, pages or assignment rubrics checked on 12 October 2026. The older 2023 manual gives different timing and was not used for the current talk length.
- The attached PDF is a group working plan. The deck follows its question and report flow, while using the simplified notebook’s completed results and the allowed healthy model.
- Group number 2a was not confirmed, so the deck does not assert that group number. The author names come from the attached plan.

The PPTX contains these notes inside every slide. The PDF is a static image preview of the final slides and includes the model notices as file attachments. Use the PowerPoint for editing and embedded speaker notes. Rehearse the notes and pointing cues together to confirm the timing.

## Before presenting

Review the names and scientific interpretation together. Keep the comparison percentages tied to their stated denominators. Treat the near-wall force as an estimate. Use backup slides only when helpful. Do not infer individual coding contributions or author approval from the slide author list.

## Slide timings

| Slide | Topic | Speaker | Target |
|---|---|---|---|
| 1 | 1D flow assumptions in a healthy aorta | Rosalie Post | 30 s |
| 2 | The question and the 1D assumptions | Rosalie Post | 50 s |
| 3 | Measurements from the 3D simulation | Rosalie Post | 50 s |
| 4 | The flow measurements conserve mass | Rosalie Post | 60 s |
| 5 | A Womersley case checks the calculations | Rosalie Post | 50 s |
| 6 | Pressure varies across the section | Rosalie Post | 55 s |
| 7 | The velocity profile changes with phase | Mark Bongers | 65 s |
| 8 | Reference profiles predict different friction | Mark Bongers | 65 s |
| 9 | The projected momentum balance | Mark Bongers | 65 s |
| 10 | The closure comparison | Mark Bongers | 65 s |
| 11 | Limits of the analysis | Mark Bongers | 50 s |
| 12 | Conclusions | Mark Bongers | 55 s |
| 13 | Backup: profile correction over the cycle | Either presenter | 0 s |
| 14 | Sources and reproducibility | Either presenter | 0 s |

## Slide 1: 1D flow assumptions in a healthy aorta

Rosalie Post. Target: 30 seconds.

We use a healthy aorta to investigate how well a one-dimensional description represents a more detailed three-dimensional flow. Our case contains bends and side branches, with a rigid vessel wall. We work with an existing simulation and test the assumptions using its pressure and velocity fields. We will first explain the measurements, then compare the reference profiles, and finish with the momentum balance.

**Cue:** Introduce Rosalie and Mark. The picture shows the actual model wall and the sampled main-aorta centreline.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- Vascular Model Repository, model 0012_H_AO_H and matching rigid-wall 3D results. Actual prepared section fields and extraction record in data/actual_volume_sections.npz and .json.
- User-provided FtP Project (1).pdf, page 1: planned presenters and model; page 2: group members.

## Slide 2: The question and the 1D assumptions

Rosalie Post. Target: 50 seconds.

The question is how well a 1D model can represent flow in this realistic vessel. A 1D model describes each cross-section using its area, flow rate and mean pressure. This saves detail, but it needs assumptions about the flow within a section. We examine whether flow is mainly axial and pressure is uniform. We also test how a fixed velocity profile and its friction law affect the balance. Finally, we check conservation and calculate a momentum residual. We use the allowed healthy model, so our conclusions concern its bends and branches.

**Cue:** Define A, Q and mean P. Explain that alpha represents the velocity-profile correction and f represents signed friction.

**Sources:**
- Simone Saitta, FP2P_projects_Simone.pptx, Project 2, slide 2. Canvas course 89400, file 10917250.
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- User-provided project plan, page 3: A1–A6 working hypotheses. Healthy-model scope confirmed by the project group in this conversation.

## Slide 3: Measurements from the 3D simulation

Rosalie Post. Target: 50 seconds.

Our input is an existing rigid-wall simulation from the Vascular Model Repository. We follow the centreline and place sections perpendicular to its local direction. The prepared data contain actual pressure and velocity values on those filled sections. We calculate flow by integrating the downstream velocity and mean pressure by weighting pressure with triangle area. Weighting matters because mesh points are unevenly spaced. We analyse 201 snapshots of one complete cycle and 47 usable sections. We exclude branch neighbourhoods from derivatives because a single-vessel balance does not include their side outlets. The cap conservation check includes those outlets.

**Cue:** Distinguish analysing existing 3D results from running a new CFD solver. Mention SI conversion and one cardiac period of 0.937 s.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- Vascular Model Repository, model 0012_H_AO_H and matching rigid-wall 3D results. Actual prepared section fields and extraction record in data/actual_volume_sections.npz and .json.
- results/geometry.csv, cap_flows_m3_s.csv and actual_volume_section_metrics.csv; aorta_functions.py section_metrics and load_sections.

## Slide 4: The flow measurements conserve mass

Rosalie Post. Target: 60 seconds.

For incompressible flow in a rigid domain, inlet flow should equal the sum of outlet flows. The two curves almost overlap. The maximum global mismatch is about 0.000022 percent of peak inlet flow. This is a computational conservation check. We then make a stricter local comparison: section flow versus inlet flow minus the upstream branch flows. Its maximum difference is 0.35 percent of peak inlet flow. This supports consistent section measurements. We use peak inlet flow as the denominator, so the percentage remains interpretable when instantaneous flow is small. These checks establish consistency of the flow measurements rather than accuracy against a patient experiment.

**Cue:** Point out the overlapping curves. Keep global and local errors distinct. Both percentages use peak inlet flow.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/cap_flows_m3_s.csv and findings.csv; notebook code cells 5, 6 and 9.

## Slide 5: A Womersley case checks the calculations

Rosalie Post. Target: 50 seconds.

Before interpreting the aorta, we use a known solution for pulsatile flow in a straight circular tube. Womersley flow changes profile with phase, whereas a Poiseuille profile has a fixed parabolic shape. Our check recovers the imposed mean speed with an error of about four times ten to the minus seven metres per second. It also satisfies no-slip at the wall and the analytical momentum balance. The plot shows four phases of that controlled case. This checks the reference calculation and balance conventions. The aorta has more complex geometry, so the known case cannot by itself validate the physiological behaviour of our model.

**Cue:** The known case uses radius 10 mm and mean speed 0.2 + 0.08 cos(2πt/T) m/s. Use the phase legend, then point to the wall at r/R = 1.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- aorta_functions.py check_analytical_cases and womersley_reference; notebook code cell 10. Controlled analytical reference, not a patient measurement.

## Slide 6: Pressure varies across the section

Rosalie Post. Target: 55 seconds.

These maps show one descending-aorta section, about 199 millimetres from the inlet, at its peak section flow. On the left, colour shows pressure relative to the area-weighted section mean. The pressure range is about 126 pascals. That is only 0.8 percent of the mean pressure, but about 24 percent of the dynamic pressure based on the mean speed. Those denominators answer different questions. A small fraction of absolute pressure does not automatically make a transverse pressure gradient irrelevant. The right map shows axial velocity and its spatial variation. Mark will now look more closely at the velocity profiles and friction comparisons.

**Cue:** This is cycle fraction 0.10. Mean pressure is 15.6 kPa. The pressure comparison uses this example only and does not establish uniformity throughout the vessel.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/figures/section_pressure_velocity.png; actual_volume_section_metrics.csv at s = 0.1989983727 m and cycle fraction 0.10.

## Slide 7: The velocity profile changes with phase

Mark Bongers. Target: 65 seconds.

The scatter plot keeps all the section points rather than reducing them to a single smooth curve. At a given radius, the spread shows variation around the section. The peak-flow profile is relatively flat through much of the interior. Its measured momentum correction is about 1.06, compared with 1.33 for Poiseuille and 1.10 for the blunt reference. At this peak-flow example, the in-plane RMS velocity is 7.1 percent of the axial RMS velocity. That supports mostly axial flow for this particular section and phase. The profiles change across the saved cycle, so we should not extend that conclusion to every phase. The radius is area-equivalent, and the actual boundary is not perfectly circular.

**Cue:** Quarter and half interval mean fractions 0.25 and 0.50 of the saved cycle, not named physiological phases. The backup slide compares alpha over the cycle.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- data/actual_volume_sections.npz, station 46, frames 20, 50 and 100; results/example_section.vtp; actual_volume_section_metrics.csv.

## Slide 8: Reference profiles predict different friction

Mark Bongers. Target: 65 seconds.

We next compare signed friction at the same section. The Poiseuille and blunt profiles use different friction coefficients. The Womersley reference also changes force with the pulsatile flow. All three references use the same measured bulk-flow history. The near-wall curve estimates force using velocity gradients and the no-slip condition. It does not use the magnitude of the supplied surface wall-shear field as a signed force. The curves differ in magnitude and phase, which changes their contribution to the momentum balance. We preserve their signs because friction during changing or reversing flow cannot be interpreted from magnitude alone. The estimate still depends on how we sample close to the wall.

**Cue:** f = K_R U. K_R = 8πν for Poiseuille and 22πν for ζ = 9. The Womersley reference uses a straight tube with the area-equivalent radius.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/actual_volume_section_metrics.csv f_measured and U; aorta_functions.py womersley_reference; data/actual_volume_sections.json: probe depth and viscosity.

## Slide 9: The projected momentum balance

Mark Bongers. Target: 65 seconds.

The equation combines local acceleration, convective transport, the mean-pressure gradient and signed friction. Their sum is the residual. We normalise its absolute value by the sum of term magnitudes, with the small numerical floor defined in the notebook. Dark regions on the map show relatively small residuals. Larger values occur at particular positions and phases, so a single average hides variation. White regions have no available result, including branch exclusions and low-flow masking. We compute spatial derivatives separately within continuous usable section runs. This avoids differentiating across a branch gap. We interpret the residual as consistency of this projected balance, while remembering that sampling, geometry and numerical derivatives also affect it.

**Cue:** The displayed map uses measured alpha and near-wall force. Colour saturates at 0.5. Endpoints remain excluded. The next slide compares common samples fairly.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/figures/momentum_residual_maps.png, lower measured panel; actual_volume_momentum_measured.csv; aorta_functions.py balance_terms and analyse_sections.

## Slide 10: The closure comparison

Mark Bongers. Target: 65 seconds.

This table compares three ways to close the same momentum balance. We use the same 2,878 available station-time pairs for every row. That matters because the measured correction becomes unstable near zero net flow and therefore has more missing values. The median normalised residual is 4.6 percent for Poiseuille, 4.4 percent for the blunt profile and 1.2 percent when we use the measured profile correction and near-wall force estimate. The measured closure also has a lower 95th percentile, but that value is still 17.5 percent. This suggests the choice of closure matters. Because we change alpha and friction together, this comparison does not isolate how much each one contributes.

**Cue:** Percentages are relative to the sum of momentum-term magnitudes. They are not percentages of clinical accuracy. Keep the median and 95th percentile distinct.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/closure_residual_statistics.csv, all three rows; notebook code cell 18.

## Slide 11: Limits of the analysis

Mark Bongers. Target: 50 seconds.

The wall-force estimate requires a derivative close to the wall. The plot compares probes at 0.30 and 0.15 millimetres. Their differences show that the sampling choice can affect the result. This is a sensitivity check and does not establish mesh convergence. The model also has rigid walls, one anatomy and one available cycle. We therefore cannot assess compliance, generalise across different anatomies, or demonstrate cycle-to-cycle convergence. Branch masking and derivative choices further restrict the available region. These limits do not cancel the consistency checks, but they control how confidently we can interpret the remaining residual as a limitation of a 1D description.

**Cue:** Avoid claiming the healthy model covers stenotic flow. Anatomical stenosis is not required for this agreed project case.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/actual_volume_section_metrics.csv f_measured and f_half_depth; data/actual_volume_sections.json; original model metadata and model specification.

## Slide 12: Conclusions

Mark Bongers. Target: 55 seconds.

For this healthy aorta, the conservation checks support consistent flow measurements. The section maps and profiles show details that a few 1D quantities cannot retain. Using measured profile and friction information reduces the typical projected momentum residual compared with the fixed references. However, the residual still varies with position and phase, and our numerical limits remain relevant. Our conclusion is that a 1D description can summarise the bulk transport, while its closures and the region of application need careful interpretation. We would next test additional geometries and numerical resolution before making broader claims. We are happy to discuss where the 1D description is useful and which checks should come next.

**Cue:** Finish the main talk here. Allow about 3 minutes for questions. Open a backup slide only if it answers a question.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/findings.csv and closure_residual_statistics.csv; scope limitations documented in results/validation.md.

## Slide 13: Backup: profile correction over the cycle

Either presenter. Target: 0 seconds.

This backup compares the measured profile correction with Poiseuille, the blunt reference and Womersley over the cycle. The logarithmic axis makes the wide positive range visible. Alpha divides a velocity-squared integral by net flow squared, so counterflow or near-zero net flow can make it large. We mask the actual section below five percent of local peak flow. The Womersley helper uses a one-percent cutoff, so the gaps are not identical. This is a reference comparison rather than a fitted local closure.

**Cue:** Use this only if asked about fixed alpha, the logarithmic scale or low-flow gaps.

**Sources:**
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.
- results/figures/profile_factor_comparison.png; aorta_functions.py womersley_reference and analyse_sections.

## Slide 14: Sources and reproducibility

Either presenter. Target: 0 seconds.

The input simulation comes from the Vascular Model Repository. We preserve its model notices and cite the repository publication. The Project 2 brief and course lectures provide the modelling context. Our notebook and included supporting scripts contain the calculations behind these slides. Running main.py regenerates the notebook figures and tables from the included actual section fields. Drafting and code organisation used AI assistance. The group should review the interpretation and speaking text before presenting.

**Cue:** Course instructions: current Simone and Ed guidelines specify 11 minutes plus 3 minutes discussion and 20% presentation weight. No dedicated template or detailed scoring rubric was found in accessible material checked on 12 October.

**Sources:**
- Simone Saitta, FP2P_projects_Simone.pptx, Project 2, slide 2. Canvas course 89400, file 10917250.
- Simone guidelines, rules_projects_Simone.pdf, page 2, Canvas file 10928253. Ed guidelines, page 1, Canvas file 10939851. Current Canvas syllabus, course 89400.
- Wilson, Ortiz and Johnson (2013). The Vascular Model Repository: A Public Resource of Medical Imaging Data and Blood Flow Simulation Results. Journal of Medical Devices 7(4), 040923. doi:10.1115/1.4025983.
- FtP_Aorta_1D_Assumptions.ipynb, completed student version of 12 October 2026.

## Discussion preparation

**Why a healthy model?** The teacher allowed it. The case still has realistic curvature and branches, so it tests the 1D assumptions within that scope.

**Does the low residual prove accuracy?** It shows consistency of the projected balance for available samples. It does not establish physiological accuracy, mesh convergence or general validity.

**Why do blank regions differ between closures?** The measured alpha becomes unstable near small net flow, and derivatives/branch masks remove other samples. The summary therefore uses the same 2,878 pairs for all closures.

**Which assumption causes the residual?** Changing alpha and friction together does not isolate their separate contributions. The measured quantities improve this comparison, but geometry and numerical derivatives also affect the residual.

**Why are some profile radii above one?** The radius is based on section area. The actual section and its offset relative to the centreline are not perfectly circular.

**What would you do next?** Repeat across different geometries and numerical resolutions, and test profile/friction changes separately before making wider claims.

AI assisted the notebook, supporting code and presentation drafting. Record actual group contributions separately.

## Model data notice

# Copyright (c) Stanford University, the Regents of the University of California,
# Open Source Medical Software Corporation, and other parties.
#
# All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this data to use the data for research and development
# purposes subject to the following conditions:
#
# The above copyright notice and this README-COPYRIGHT file shall be
# included in all copies of any portion of this data.
#
# Whenever reasonable and possible in publications and presentations
# when this data is used in whole or part, please include an
# acknowledgement similar to the following:
#
# "The data used herein was provided in whole or in part with
# Federal funds from the National Library of Medicine under Grant
# No. R01LM013120, and the National Heart, Lung, and Blood Institute,
# National Institutes of Health, Department of Health and Human Services,
# under Contract No. HHSN268201100035C"
#
# AND/OR
#
# N.M. Wilson, A.K. Ortiz, and A.B. Johnson, “The Vascular Model Repository:
# A Public Resource of Medical Imaging Data and Blood Flow Simulation Results,”
# J. Med. Devices 7(4), 040923 (Dec 05, 2013) doi:10.1115/1.4025983.
#
# AND/OR
#
# Reference the official website for this data: www.vascularmodel.com
#
#
# THE DATA IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# DATA OR THE USE OR OTHER DEALINGS IN THE DATA.

