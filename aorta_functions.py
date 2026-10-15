"""Supporting functions for the Project 2 aorta notebook.

The notebook shows the measurements, comparisons and plots. This file keeps
the longer mesh-reading and numerical routines together. All geometry and
fields returned to the notebook are in SI units.
"""

from pathlib import Path
from importlib.metadata import version
import hashlib
import json
import re
import warnings
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import pyvista as pv
import vtk
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from scipy.special import jv
from vmtk import vmtkscripts, vtkvmtk

SOURCE_UNITS = {"length": 0.01, "velocity": 0.01, "pressure": 0.1, "shear": 0.1}
CAP_IDS = {"inflow": 2, "btrunk": 3, "carotid": 5, "subclavian": 6, "outflow": 7}


def sha256_file(path):
    """Hash input bytes in bounded chunks; used for provenance and cache checks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sv_path(path, length_scale=0.01):
    """Read SimVascular sampled path positions, not its sparse control points."""
    text = Path(path).read_text()

    # Legacy files have multiple top-level XML elements, so use a wrapper.
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    root = ET.fromstring("<root>" + text + "</root>")
    points = [
        [float(p.attrib[k]) for k in ("x", "y", "z")]
        for p in root.findall(".//path_points/path_point/pos")
    ]
    points = np.asarray(points) * length_scale
    if len(points) < 4 or not np.all(np.isfinite(points)):
        raise ValueError(f"Invalid path: {path}")
    return points


def resample_path(points, spacing=0.004, trim=0.006):
    """Return uniform arc-length positions, unit tangents and curvature [1/m].

    Cubic interpolation is based on chord arc length; dense reparameterization
    then makes station distances nearly uniform. End trimming avoids cap cuts.
    """
    points = np.asarray(points, dtype=float)
    keep = np.r_[True, np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-10]
    points = points[keep]
    s0 = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    if spacing <= 0 or trim < 0 or s0[-1] <= 2 * trim + 2 * spacing:
        raise ValueError("Spacing/trim incompatible with path length.")

    # Smooth the path, then resample it by distance rather than point index.
    spline = CubicSpline(s0, points, axis=0)
    dense = spline(np.linspace(0, s0[-1], max(2000, len(points) * 5)))
    sd = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))]
    smooth = CubicSpline(sd, dense, axis=0)
    s = np.linspace(
        trim, sd[-1] - trim, int(np.ceil((sd[-1] - 2 * trim) / spacing)) + 1
    )

    # The first and second derivatives give tangent and curvature.
    xyz = smooth(s)
    d1, d2 = smooth(s, 1), smooth(s, 2)
    tangent = d1 / np.linalg.norm(d1, axis=1)[:, None]
    curvature = (
        np.linalg.norm(np.cross(d1, d2), axis=1) / np.linalg.norm(d1, axis=1) ** 3
    )
    return s, xyz, tangent, curvature


def triangle_rule(mesh):
    """Return triangle vertices, areas, degree-two barycentric quadrature.

    Three Gauss points integrate linear velocity and its quadratic square
    exactly on each planar triangle. No point-count weighting is used.
    """
    mesh = mesh.triangulate()
    faces = np.asarray(mesh.faces).reshape(-1, 4)
    if not np.all(faces[:, 0] == 3):
        raise ValueError("Expected a triangle-only surface.")
    tri = faces[:, 1:]
    p = mesh.points[tri]
    area = 0.5 * np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1)

    # Three barycentric points integrate squared linear velocity exactly.
    bary = np.array(
        [[2 / 3, 1 / 6, 1 / 6], [1 / 6, 2 / 3, 1 / 6], [1 / 6, 1 / 6, 2 / 3]]
    )
    return mesh, tri, area, bary


def integrate_linear(mesh, values):
    """Integrate nodal scalar or vector values on a triangulated surface."""
    _, tri, area, _ = triangle_rule(mesh)
    vals = np.asarray(values)[tri].mean(axis=1)
    return np.einsum("i,i...->...", area, vals)


def outward_cap_normal(cap, wall):
    """Area-weighted cap normal oriented away from a nearby interior wall point."""
    cap, tri, area, _ = triangle_rule(cap)
    p = cap.points[tri]
    normals = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    normal = normals.sum(axis=0)
    normal /= np.linalg.norm(normal)
    center = np.average(p.mean(axis=1), axis=0, weights=area)
    nearest = cKDTree(wall.points).query(center, k=min(500, wall.n_points))[1]
    inside_direction = wall.points[nearest].mean(axis=0) - center
    if normal @ inside_direction > 0:
        normal = -normal
    return normal, center


def extract_vmtk_path(wall, source, target, output_path):
    """Extract one inlet-to-descending-outlet centerline with noninteractive open-profile IDs.

    Surface is already open at caps. A modest decimation accelerates Voronoi
    construction; preserve topology. Cache is only valid for identical input.
    """

    # Reduce surface size while preserving the open vessel topology.
    reduced = wall.triangulate().clean().decimate_pro(0.8, preserve_topology=True)
    cl = vmtkscripts.vmtkCenterlines()
    cl.Surface = reduced
    capper = vtkvmtk.vtkvmtkCapPolyData()
    capper.SetInputData(reduced)
    capper.Update()
    ids = capper.GetCapCenterIds()
    centers = np.array(
        [capper.GetOutput().GetPoint(ids.GetId(i)) for i in range(ids.GetNumberOfIds())]
    )
    if len(centers) != 5:
        raise ValueError(f"Expected five open profiles; found {len(centers)}.")
    cl.SeedSelectorName = "profileidlist"
    cl.SourceIds = [int(np.argmin(np.linalg.norm(centers - source, axis=1)))]
    cl.TargetIds = [int(np.argmin(np.linalg.norm(centers - target, axis=1)))]
    cl.AppendEndPoints = 1
    cl.Execute()
    smoother = vmtkscripts.vmtkCenterlineSmoothing()
    smoother.Centerlines = cl.Centerlines
    smoother.NumberOfSmoothingIterations = 30
    smoother.SmoothingFactor = 0.1
    smoother.Execute()
    lines = pv.wrap(smoother.Centerlines)
    lines.save(output_path)
    if lines.n_cells < 1:
        raise ValueError("VMTK returned no centerline.")

    # A single target gives one polyline; explicitly read its connectivity.
    line = lines.get_cell(0).points
    if np.linalg.norm(line[0] - source) > np.linalg.norm(line[-1] - source):
        line = line[::-1]
    return line, lines


def section_from_volume(volume, origin, tangent):
    """Cut volume and keep connected section containing the centerline station.

    Plane can also cross a remote aortic limb. Select by nearest cell to origin;
    retain ambiguity checks in caller around ostia and non-circular sections.
    """

    # Cut with double-precision coordinates to avoid rounding small SI lengths.
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(tangent)
    cutter = vtk.vtkCutter()
    cutter.SetInputData(volume)
    cutter.SetCutFunction(plane)

    # Default cutter output may downcast SI coordinates to Float32.
    cutter.SetOutputPointsPrecision(vtk.vtkAlgorithm.DOUBLE_PRECISION)
    cutter.GenerateTrianglesOn()
    cutter.Update()
    section = pv.wrap(cutter.GetOutput()).triangulate().clean()
    if section.n_cells == 0:
        raise ValueError("Empty slice: centerline lies outside CFD volume.")
    regions = section.connectivity("all")
    closest = regions.find_closest_cell(origin)
    selected = int(regions.cell_data["RegionId"][closest])
    section = (
        regions.threshold(
            [selected - 0.1, selected + 0.1], scalars="RegionId", preference="cell"
        )
        .extract_surface(algorithm="dataset_surface")
        .triangulate()
    )
    return section


def wall_loop(wall, origin, tangent):
    """Cut open wall; choose nearest connected closed contour.

    Fail if curve is open. A branch ostium may merge contours; caller masks
    branch neighborhoods rather than pretending their sections are 1D tubes.
    """
    cut = wall.slice(normal=tangent, origin=origin).clean()
    if cut.n_cells == 0:
        raise ValueError("Empty wall contour.")
    con = cut.connectivity("all")
    cid = con.find_closest_cell(origin)
    rid = int(con.cell_data["RegionId"][cid])
    cut = (
        con.threshold([rid - 0.1, rid + 0.1], scalars="RegionId", preference="cell")
        .extract_surface(algorithm="dataset_surface")
        .clean()
    )
    pairs = []
    for i in range(cut.n_cells):
        ids = cut.get_cell(i).point_ids
        pairs.extend(zip(ids[:-1], ids[1:]))
    pairs = np.asarray(pairs, int)
    degree = np.bincount(pairs.ravel(), minlength=cut.n_points)
    if not np.all(degree == 2):
        raise ValueError("Open/branched wall contour; exclude this station.")

    # Orient connected contour consistently by following adjacent vertices.
    adjacency = [[] for _ in range(cut.n_points)]
    for a, b in pairs:
        adjacency[a].append(b)
        adjacency[b].append(a)
    order, prev, cur = [0], -1, 0
    while True:
        nxt = next(x for x in adjacency[cur] if x != prev)
        if nxt == 0:
            break
        if nxt in order:
            raise ValueError("Invalid contour topology.")
        order.append(nxt)
        prev, cur = cur, nxt
    pts = cut.points[order]
    edges = np.roll(pts, -1, axis=0) - pts
    lengths = np.linalg.norm(edges, axis=1)
    polygon_vector = np.sum(
        np.cross(pts - origin, np.roll(pts, -1, axis=0) - origin), axis=0
    )
    area = abs(polygon_vector @ tangent) / 2
    if area <= 0:
        raise ValueError("Degenerate contour.")
    return pts, lengths, area


def section_metrics(
    section, tangent, velocity="velocity", pressure="pressure", q_floor=1e-8
):
    """Area-integrate A1/A2/A3/A5 observables in SI on one filled section.

    Alpha is undefined near net flow zero and returns NaN. Secondary ratio
    uses RMS energies, so it does not divide by a sign-changing net velocity.
    """
    section, tri, area, bary = triangle_rule(section)
    vel = np.asarray(section.point_data[velocity])
    p = np.asarray(section.point_data[pressure])
    if vel.shape != (section.n_points, 3) or p.shape != (section.n_points,):
        raise ValueError("Velocity must be Nx3; pressure must be nodal scalar.")
    if not np.all(np.isfinite(vel)) or not np.all(np.isfinite(p)):
        raise ValueError("Non-finite CFD field.")

    # Interpolate velocity at quadrature points before projecting it.
    vq = np.einsum("gj,tjk->tgk", bary, vel[tri])
    axial = vq @ tangent
    secondary = vq - axial[..., None] * tangent

    # Weight each contribution by its triangle's physical area.
    A = area.sum()
    Q = np.sum(area * axial.mean(axis=1))
    axial_energy = np.sum(area * (axial**2).mean(axis=1))
    secondary_energy = np.sum(area * np.sum(secondary**2, axis=-1).mean(axis=1))
    P = np.sum(area * p[tri].mean(axis=1)) / A
    ratio = np.sqrt(secondary_energy / axial_energy) if axial_energy > 1e-18 else np.nan
    alpha = A * axial_energy / Q**2 if abs(Q) > q_floor else np.nan
    return dict(
        A=A,
        Q=Q,
        U=Q / A,
        P=P,
        alpha=alpha,
        secondary_ratio=ratio,
        pressure_range=float(np.ptp(p)),
        axial_energy=axial_energy,
    )


def signed_wall_force(gradient_volume, contour, tangent, viscosity):
    """Return axial resisting wall force / density [m³/s²] from velocity gradient.

    tau_on_fluid = mu (grad u + grad u.T) n_out. Signed friction term
    f = -integral(tau_on_fluid dot tangent) dl / rho. Use SI gradient.
    This requires resolved near-wall volume fields. It is not inferred from
    unsigned WSS magnitude. Invalid probes raise instead of becoming zeros.
    """
    pts, lengths, _ = contour
    midpoint = (pts + np.roll(pts, -1, axis=0)) / 2
    edge = np.roll(pts, -1, axis=0) - pts
    n = np.cross(edge, tangent)
    n /= np.linalg.norm(n, axis=1)[:, None]
    radial = midpoint - midpoint.mean(axis=0)
    if np.mean(np.sum(n * radial, axis=1)) < 0:
        n = -n

    # Probe slightly inside wall to avoid floating-point outside-domain cuts.
    epsilon = max(1e-7, np.median(lengths) * 0.02)
    probes = pv.PolyData(midpoint - epsilon * n).sample(gradient_volume)
    if not np.all(probes["vtkValidPointMask"]):
        raise ValueError(
            "Wall-gradient probes outside volume; refine/check wall mapping."
        )
    grad = np.asarray(probes["gradient"]).reshape(-1, 3, 3)

    # Project viscous traction onto the downstream direction.
    traction_over_rho = viscosity * np.einsum(
        "ijk,ik->ij", grad + grad.transpose(0, 2, 1), n
    )
    return -np.sum(lengths * (traction_over_rho @ tangent))


def profile_constants(zeta):
    """Return alpha and KR/nu for u/U=(zeta+2)/zeta * (1-(r/R)^zeta)."""
    if zeta <= 0:
        raise ValueError("zeta must be positive.")
    return (zeta + 2) / (zeta + 1), 2 * (zeta + 2) * np.pi


def womersley_reference(times, mean_speed, radius, nu, period, harmonics=12, nr=501):
    """Reconstruct fully developed rigid straight-tube Womersley reference.

    Input mean-speed history is resampled to uniform periodic phase. Output
    velocity and signed friction include DC Poiseuille and Fourier harmonics.
    e^(i omega t) convention, lambda=sqrt(-i)*Wo. No patient field is simulated.
    """
    times, mean_speed = np.asarray(times), np.asarray(mean_speed)

    # Express the waveform on a uniformly sampled periodic time grid.
    phase = np.mod(times - times[0], period)
    order = np.argsort(phase)
    unique, ids = np.unique(np.round(phase[order], 10), return_index=True)
    y = mean_speed[order][ids]
    if len(unique) < 8:
        raise ValueError("Need >=8 distinct cardiac phases.")
    N = max(128, len(unique))
    uniform = np.linspace(0, period, N, endpoint=False)
    yp = np.interp(
        uniform,
        np.r_[unique[-1] - period, unique, unique[0] + period],
        np.r_[y[-1], y, y[0]],
    )

    # Separate mean flow from the oscillating Fourier components.
    coeff = np.fft.rfft(yp) / N
    rr = np.linspace(0, 1, nr)
    velocity = np.full((len(times), nr), 0.0)
    velocity += coeff[0].real * 2 * (1 - rr**2)
    friction = np.full(len(times), 8 * np.pi * nu * coeff[0].real)
    # dP/dx / rho
    gradient = np.full(len(times), -8 * nu * coeff[0].real / radius**2)

    # Add each harmonic's radial velocity, force and pressure-gradient response.
    for h in range(1, min(harmonics + 1, len(coeff))):
        omega = 2 * np.pi * h / period
        lam = np.sqrt(-1j) * radius * np.sqrt(omega / nu)
        denominator = 1 - 2 * jv(1, lam) / (lam * jv(0, lam))
        shape = (1 - jv(0, lam * rr) / jv(0, lam)) / denominator
        wave = 2 * coeff[h] * np.exp(1j * omega * (times - times[0]))
        velocity += np.real(wave[:, None] * shape)
        friction += np.real(
            wave * (-2 * np.pi * nu * lam * jv(1, lam) / jv(0, lam) / denominator)
        )
        gradient += np.real(wave * (-1j * omega / denominator))

    # Integrate the reconstructed profiles to recover flow and momentum.
    actual_mean = 2 * np.trapezoid(velocity * rr, rr, axis=1)
    second = 2 * np.trapezoid(velocity**2 * rr, rr, axis=1)
    alpha = np.divide(
        second,
        actual_mean**2,
        out=np.full(len(times), np.nan),
        where=np.abs(actual_mean) > 0.01 * np.max(np.abs(actual_mean)),
    )
    return dict(
        r=rr * radius,
        velocity=velocity,
        U=actual_mean,
        alpha=alpha,
        friction=friction,
        pressure_gradient_over_rho=gradient,
    )


def balance_terms(times, s, A, Q, P, alpha, friction, rho):
    """Conservative 1D momentum: Qt + d(alpha Q²/A)/dx + A Px/rho + f = 0.

    Arrays are (time, station); friction is signed force/density per length.
    A mass residual is At + Qx [m²/s]. Spatial/time edges remain excluded.
    """
    times, s = np.asarray(times), np.asarray(s)
    if (
        len(times) < 3
        or len(s) < 3
        or np.any(np.diff(times) <= 0)
        or np.any(np.diff(s) <= 0)
    ):
        raise ValueError("Need >=3 strictly increasing times and stations.")
    if np.any(A <= 0):
        raise ValueError("Area must be positive.")
    if np.isscalar(alpha):
        alpha = np.full_like(Q, alpha, dtype=float)
    if np.shape(alpha) != np.shape(Q):
        raise ValueError("Alpha shape must match Q.")

    # Evaluate the four signed terms of the conservative momentum equation.
    inertial = np.gradient(Q, times, axis=0, edge_order=2)
    convective = np.gradient(alpha * Q**2 / A, s, axis=1, edge_order=2)
    pressure = A * np.gradient(P, s, axis=1, edge_order=2) / rho
    residual = inertial + convective + pressure + friction

    # Normalise by the sum of term magnitudes, with a small floor.
    scale = np.abs(inertial) + np.abs(convective) + np.abs(pressure) + np.abs(friction)
    floor = max(np.nanmax(scale) * 1e-3, 1e-12)
    normalized = np.abs(residual) / np.maximum(scale, floor)

    # Check mass separately and exclude derivative endpoints.
    mass = np.gradient(A, times, axis=0, edge_order=2) + np.gradient(
        Q, s, axis=1, edge_order=2
    )
    for arr in [residual, normalized, mass]:
        arr[[0, -1], :] = np.nan
        arr[:, [0, -1]] = np.nan
    return dict(
        inertial=inertial,
        convective=convective,
        pressure=pressure,
        friction=friction,
        residual=residual,
        normalized=normalized,
        mass=mass,
    )


def full_cycle_indices(steps, dt, period):
    """Choose last complete interval and verify expected sampling coverage."""
    steps = np.asarray(steps, dtype=int)
    if len(steps) < 3 or np.any(np.diff(steps) <= 0):
        raise ValueError("Timesteps must be unique/increasing.")
    times = steps * dt
    end = times[-1]
    start = end - period
    tolerance = 1e-8 * period
    if times[0] > start + tolerance:
        raise ValueError("Result archive does not cover a complete cardiac cycle.")
    keep = times >= start - tolerance
    chosen = times[keep]
    if np.max(np.diff(chosen)) > 1.5 * np.median(np.diff(chosen)):
        raise ValueError("Missing frames inside selected cardiac cycle.")
    return np.flatnonzero(keep), times[keep] - start


def analyse_sections(cache, s, tangents, rho, nu, export, low_fraction=0.05):
    """Recompute all cross-sectional metrics and closure residuals from real slices.

    Wall force is a two-depth, no-slip normal-derivative estimate, not supplied
    WSS magnitude. Derivative runs cannot cross branch/exclusion gaps. Pressure
    normalizations and alpha are masked near net zero flow.
    """
    times = np.asarray(cache["time_s"])
    ids = np.asarray(cache["section_ids"], int)
    if not np.allclose(np.asarray(cache["s_m"]), s):
        raise ValueError("Slice-cache station mismatch.")

    # Leave excluded stations as NaN rather than filling them with zeros.
    shape = (len(times), len(s))
    fields = {
        key: np.full(shape, np.nan)
        for key in ["A", "Q", "U", "P", "alpha", "secondary_ratio", "pressure_range"]
    }

    # Integrate pressure and velocity over each stored section.
    for k, i in enumerate(ids):
        mesh = pv.PolyData(cache[f"points_{i}"], cache[f"faces_{i}"])
        sl = slice(cache["offsets"][k], cache["offsets"][k + 1])
        for j in range(len(times)):
            mesh["velocity"] = np.asarray(cache["velocity_m_s"][j, sl], dtype=float)
            mesh["pressure"] = np.asarray(cache["pressure_Pa"][j, sl], dtype=float)
            metrics = section_metrics(mesh, tangents[i], q_floor=1e-10)
            for key in fields:
                fields[key][j, i] = metrics[key]

    # Keep both wall-probe depths for the later sensitivity comparison.
    fields["f_measured"] = np.asarray(cache["f_wall_probe_m3_s2"])
    fields["f_half_depth"] = np.asarray(cache["f_wall_probe_half_m3_s2"])

    # Mask profile factors and pressure ratios at low net flow.
    Q, A, P = fields["Q"], fields["A"], fields["P"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        peak = np.nanmax(np.abs(Q), axis=0)
    low = np.abs(Q) < low_fraction * peak[None, :]
    fields["alpha"][low] = np.nan
    dynamic = 0.5 * rho * (Q / A) ** 2
    fields["pressure_dynamic_ratio"] = np.divide(
        fields["pressure_range"],
        dynamic,
        out=np.full(shape, np.nan),
        where=(~low) & (dynamic > 1e-6),
    )
    fields["pressure_axial_ratio"] = np.full(shape, np.nan)

    # Prepare separate term arrays for the five closure comparisons.
    termsets = {
        name: {
            key: np.full(shape, np.nan)
            for key in [
                "inertial",
                "convective",
                "pressure",
                "friction",
                "residual",
                "normalized",
                "mass",
            ]
        }
        for name in [
            "poiseuille",
            "zeta9",
            "measured",
            "measured_alpha_poiseuille_f",
            "poiseuille_alpha_measured_f",
        ]
    }

    # Differentiate only within contiguous, unbranched station runs.
    for run in np.split(ids, np.where(np.diff(ids) > 1)[0] + 1):
        if len(run) < 3:
            continue
        local_drop = np.abs(np.gradient(P[:, run], s[run], axis=1)) * np.mean(
            np.diff(s[run])
        )
        fields["pressure_axial_ratio"][:, run] = np.divide(
            fields["pressure_range"][:, run],
            local_drop,
            out=np.full((len(times), len(run)), np.nan),
            where=(~low[:, run]) & (local_drop > 0.01),
        )
        for name, alpha, friction in [
            ("poiseuille", 4 / 3, 8 * np.pi * nu * Q / A),
            ("zeta9", 1.1, 22 * np.pi * nu * Q / A),
            ("measured", fields["alpha"], fields["f_measured"]),
            ("measured_alpha_poiseuille_f", fields["alpha"], 8 * np.pi * nu * Q / A),
            ("poiseuille_alpha_measured_f", 4 / 3, fields["f_measured"]),
        ]:
            a = alpha if np.isscalar(alpha) else alpha[:, run]
            terms = balance_terms(
                times, s[run], A[:, run], Q[:, run], P[:, run], a, friction[:, run], rho
            )
            for key, value in terms.items():
                termsets[name][key][:, run] = value

    # Export full numerical values for each section and time.
    table = pd.DataFrame(
        [
            {
                "time_s": times[j],
                "s_m": s[i],
                **{key: value[j, i] for key, value in fields.items()},
            }
            for j in range(len(times))
            for i in range(len(s))
        ]
    )
    table.to_csv(export / "actual_volume_section_metrics.csv", index=False)
    for name, terms in termsets.items():
        pd.DataFrame(
            [
                {
                    "time_s": times[j],
                    "s_m": s[i],
                    **{key: value[j, i] for key, value in terms.items()},
                }
                for j in range(len(times))
                for i in range(len(s))
            ]
        ).to_csv(export / f"actual_volume_momentum_{name}.csv", index=False)
    return times, fields, termsets, table


def load_geometry(project_folder, spacing=0.004, trim=0.015, branch_exclusion=0.018):
    """Read this model, identify its caps and sample its VMTK centreline.

    Returns a dictionary containing the wall, caps, centreline stations,
    tangents, section contours and a geometry table. Branch neighbourhoods
    and open contours are excluded from the one-dimensional balance.
    """
    root = Path(project_folder)
    data = root / "data" / "0012_H_AO_H"
    model_path = data / "Models" / "0095_0001.vtp"

    # Coordinates and surface velocities in the source are in centimetres.
    model = pv.read(model_path)
    model.points = np.asarray(model.points, dtype=float) * SOURCE_UNITS["length"]
    wall = (
        model.threshold([0.9, 1.1], scalars="ModelFaceID", preference="cell")
        .extract_surface(algorithm="dataset_surface")
        .clean()
    )
    surface_path = root / "data" / "results" / "0012_H_AO_H_3D_RIGID.vtp"
    surface = pv.read(surface_path)
    surface_geometry = pv.PolyData(
        np.asarray(surface.points, dtype=float) * SOURCE_UNITS["length"], surface.faces
    )
    surface_geometry["source_point_id"] = np.arange(surface_geometry.n_points)

    # Match anatomical labels by element ID, since triangle order can differ.
    face_lookup = dict(
        zip(
            model.cell_data["GlobalElementID"].astype(int),
            model.cell_data["ModelFaceID"].astype(int),
        )
    )
    result_ids = surface.cell_data["GlobalElementID"].astype(int)
    if len(set(result_ids)) != len(result_ids) or set(result_ids) != set(face_lookup):
        raise ValueError("Result/model element IDs do not match uniquely.")
    surface_geometry.cell_data["ModelFaceID"] = np.array(
        [face_lookup[x] for x in result_ids]
    )
    caps = {}
    for name, face_id in CAP_IDS.items():
        cap = surface_geometry.threshold(
            [face_id - 0.1, face_id + 0.1], scalars="ModelFaceID", preference="cell"
        ).extract_surface(algorithm="dataset_surface")
        normal, center = outward_cap_normal(cap, wall)
        caps[name] = {
            "mesh": cap,
            "normal": normal,
            "center": center,
            "indices": np.asarray(cap["source_point_id"], int),
        }

    # Reuse the included VMTK path only when its input and settings match.
    centerline_path = root / "data" / "centerline_vmtk.vtp"
    centerline_meta = centerline_path.with_suffix(".json")
    signature = {
        "surface_sha256": sha256_file(model_path),
        "length_scale": SOURCE_UNITS["length"],
        "decimation": 0.8,
        "smoothing_iterations": 30,
        "smoothing_factor": 0.1,
        "seed_method": "profileidlist",
    }
    if not centerline_path.exists() or not centerline_meta.exists():
        points, _ = extract_vmtk_path(
            wall, caps["inflow"]["center"], caps["outflow"]["center"], centerline_path
        )
        centerline_meta.write_text(json.dumps(signature, indent=2))
    else:
        if json.loads(centerline_meta.read_text()) != signature:
            raise ValueError("The saved centreline does not match this model/settings.")
        points = pv.read(centerline_path).get_cell(0).points
        inlet = caps["inflow"]["center"]
        if np.linalg.norm(points[0] - inlet) > np.linalg.norm(points[-1] - inlet):
            points = points[::-1]
    s, xyz, tangents, curvature = resample_path(points, spacing, trim)
    supplied_path = read_sv_path(data / "Paths" / "aorta.pth")
    path_distance = cKDTree(supplied_path).query(xyz)[0]

    # Locate the three side branches along the main path.
    branch_locations = {}
    for name in ["btrunk", "carotid", "subclavian"]:
        branch_path = read_sv_path(data / "Paths" / f"{name}.pth")
        distances, indices = cKDTree(xyz).query(branch_path)
        branch_locations[name] = float(s[indices[np.argmin(distances)]])
    branch_mask = np.zeros(len(s), dtype=bool)
    for branch_s in branch_locations.values():
        branch_mask |= np.abs(s - branch_s) < branch_exclusion

    # Closed wall contours give area and perimeter at each station.
    contours = []
    area = np.full(len(s), np.nan)
    perimeter = np.full(len(s), np.nan)
    for i, (origin, tangent) in enumerate(zip(xyz, tangents)):
        try:
            contour = wall_loop(wall, origin, tangent)
            contours.append(contour)
            area[i], perimeter[i] = contour[2], contour[1].sum()
        except ValueError:
            contours.append(None)
    valid = np.isfinite(area) & ~branch_mask
    radius = np.sqrt(area / np.pi)
    table = pd.DataFrame(
        {
            "s_m": s,
            "A_m2": area,
            "perimeter_m": perimeter,
            "diameter_m": 2 * radius,
            "hydraulic_diameter_m": 4 * area / perimeter,
            "curvature_per_m": curvature,
            "circularity": 4 * np.pi * area / perimeter**2,
            "branch_excluded": branch_mask,
            "usable": valid,
            "path_difference_m": path_distance,
        }
    )
    return {
        "wall": wall,
        "caps": caps,
        "surface": surface,
        "s_m": s,
        "points": xyz,
        "tangents": tangents,
        "curvature": curvature,
        "contours": contours,
        "area_m2": area,
        "radius_m": radius,
        "valid": valid,
        "branch_locations": branch_locations,
        "table": table,
        "centerline_path": centerline_path,
        "model_path": model_path,
        "surface_path": surface_path,
        "settings": {
            "spacing_m": spacing,
            "trim_m": trim,
            "branch_exclusion_m": branch_exclusion,
        },
    }


def read_cap_flows(geometry, dt, period):
    """Integrate cap fluxes for the last complete cycle; positive inlet is inflow."""
    surface = geometry["surface"]
    all_steps = np.array(
        sorted(
            int(re.fullmatch(r"velocity_(\d+)", name).group(1))
            for name in surface.point_data
            if re.fullmatch(r"velocity_(\d+)", name)
        )
    )
    chosen, times = full_cycle_indices(all_steps, dt, period)
    steps = all_steps[chosen]
    flows = {}
    for name, cap in geometry["caps"].items():
        values = []
        for step in steps:
            velocity = (
                np.asarray(surface[f"velocity_{step}"])[cap["indices"]]
                * SOURCE_UNITS["velocity"]
            )
            flux = integrate_linear(cap["mesh"], velocity @ cap["normal"])
            values.append(-flux if name == "inflow" else flux)
        flows[name] = np.array(values)
    table = pd.DataFrame(
        {"time_s": times, "source_time_s": steps * dt, "solver_step": steps, **flows}
    )
    return times, steps, table


def load_sections(project_folder, geometry, nu, dt, period):
    """Load actual section fields after checking model, sampling, units and viscosity."""
    root = Path(project_folder)
    path = root / "data" / "actual_volume_sections.npz"
    metadata = json.loads(path.with_suffix(".json").read_text())
    expected = {
        "model_sha256": sha256_file(geometry["model_path"]),
        "centerline_sha256": sha256_file(geometry["centerline_path"]),
        **geometry["settings"],
        "source_dt_s": dt,
        "period_s": period,
        "kinematic_viscosity_m2_s": nu,
        "units": SOURCE_UNITS,
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(
                f"Section data {key} differs. See prepare_volume.py before changing extraction settings."
            )
    with np.load(path, allow_pickle=False) as stored:
        cache = {key: stored[key] for key in stored.files}
    if json.loads(str(cache["signature_json"])) != metadata:
        raise ValueError("Section data metadata signature mismatch.")
    if not np.allclose(cache["s_m"], geometry["s_m"]):
        raise ValueError("Section station positions differ from the centreline.")
    if not np.array_equal(cache["section_ids"], np.flatnonzero(geometry["valid"])):
        raise ValueError("Section station eligibility differs from the geometry.")
    if np.any(np.diff(cache["time_s"]) <= 0) or not np.isclose(
        np.ptp(cache["time_s"]), period
    ):
        raise ValueError("Section data must cover one complete, ordered cycle.")
    return cache, metadata


def get_section(cache, geometry, station, frame):
    """Return one filled section with pressure, velocity and local plotting coordinates."""
    ids = np.flatnonzero(cache["section_ids"] == station)
    if len(ids) != 1:
        raise ValueError("Choose one of the valid section stations.")
    k = int(ids[0])
    selection = slice(cache["offsets"][k], cache["offsets"][k + 1])
    mesh = pv.PolyData(cache[f"points_{station}"], cache[f"faces_{station}"])
    mesh["velocity"] = np.asarray(cache["velocity_m_s"][frame, selection], dtype=float)
    mesh["pressure"] = np.asarray(cache["pressure_Pa"][frame, selection], dtype=float)
    normal = geometry["tangents"][station]
    mesh["axial_velocity"] = mesh["velocity"] @ normal

    # A pair of in-plane axes is needed to show the cut as a two-dimensional map.
    reference_axis = (
        np.array([1.0, 0, 0]) if abs(normal[0]) < 0.9 else np.array([0, 1.0, 0])
    )
    axis_1 = np.cross(normal, reference_axis)
    axis_1 /= np.linalg.norm(axis_1)
    axis_2 = np.cross(normal, axis_1)
    relative = mesh.points - geometry["points"][station]
    x, y = relative @ axis_1, relative @ axis_2
    mesh["plot_x_mm"] = x * 1000
    mesh["plot_y_mm"] = y * 1000
    mesh["normalised_radius"] = np.sqrt(x * x + y * y) / geometry["radius_m"][station]
    return mesh


def check_analytical_cases(rho, mu, period):
    """Check triangle integration, steady Poiseuille and pulsatile Womersley cases.

    Returns the straight-tube reference and a small table of numerical errors.
    These checks verify the calculations, not the patient's boundary conditions.
    """
    nu = mu / rho
    triangle = pv.PolyData(
        np.array([[0.0, 0, 0], [1.0, 0, 0], [0.0, 1, 0]]), [3, 0, 1, 2]
    )
    triangle["velocity"] = np.c_[np.zeros((3, 2)), [0.0, 1, 0]]
    triangle["pressure"] = np.array([10.0, 20, 30])
    check = section_metrics(triangle, np.array([0.0, 0, 1.0]))
    assert np.isclose(check["Q"], 1 / 6) and np.isclose(check["alpha"], 1.5)
    assert np.isclose(check["P"], 20)
    triangle["velocity"] = np.zeros((3, 3))
    assert np.isnan(section_metrics(triangle, np.array([0.0, 0, 1.0]))["alpha"])

    times = np.linspace(0, period, 201)
    positions = np.linspace(0, 0.2, 41)
    radius, mean_speed = 0.01, 0.2
    area = np.full((len(times), len(positions)), np.pi * radius**2)
    flow = area * mean_speed
    pressure = np.broadcast_to(
        10000 - 8 * mu * mean_speed / radius**2 * positions, area.shape
    )
    friction = np.full_like(flow, 8 * np.pi * nu * mean_speed)
    terms = balance_terms(times, positions, area, flow, pressure, 4 / 3, friction, rho)
    assert np.nanmax(terms["normalized"]) < 1e-10
    assert np.nanmax(np.abs(terms["mass"])) < 1e-15

    waveform = 0.2 + 0.08 * np.cos(2 * np.pi * times / period)
    reference = womersley_reference(
        times, waveform, radius, nu, period, harmonics=1, nr=1001
    )
    flow_error = np.max(np.abs(reference["U"] - waveform))
    wall_error = np.max(np.abs(reference["velocity"][:, -1]))
    exact_Qt = (
        np.pi
        * radius**2
        * (-0.08 * 2 * np.pi / period * np.sin(2 * np.pi * times / period))
    )
    residual = (
        exact_Qt
        + np.pi * radius**2 * reference["pressure_gradient_over_rho"]
        + reference["friction"]
    )
    assert flow_error < 2e-6 and wall_error < 1e-12
    assert np.max(np.abs(residual)) < 1e-12
    reference["time_s"] = times
    reference["radius_m"] = radius
    errors = pd.DataFrame(
        [
            {"check": "Mean velocity recovery", "error": flow_error, "units": "m/s"},
            {"check": "Wall no-slip", "error": wall_error, "units": "m/s"},
            {
                "check": "Womersley momentum balance",
                "error": np.max(np.abs(residual)),
                "units": "m³/s²",
            },
        ]
    )
    return reference, errors


def save_run_info(project_folder, parameters, volume_metadata):
    """Save input/script identifiers and versions without printing them in the notebook."""
    root = Path(project_folder)
    files = [
        root / "data" / "0012_H_AO_H" / "Models" / "0095_0001.vtp",
        root / "data" / "centerline_vmtk.vtp",
        root / "data" / "results" / "0012_H_AO_H_3D_RIGID.vtp",
        root / "data" / "actual_volume_sections.npz",
        root / "aorta_functions.py",
        root / "prepare_volume.py",
        root / "main.py",
    ]
    record = {
        "inputs_and_scripts": [
            {"file": str(p.relative_to(root)), "sha256": sha256_file(p)} for p in files
        ],
        "parameters": parameters,
        "volume_source": volume_metadata,
        "packages": {
            p: version(p)
            for p in [
                "numpy",
                "scipy",
                "pandas",
                "matplotlib",
                "pyvista",
                "vtk",
                "vmtk",
            ]
        },
        "study_scope": "healthy rigid aorta; approved healthy-model scope",
    }
    (root / "results" / "run_manifest.json").write_text(json.dumps(record, indent=2))


def plot_alpha_time(history, distance_m, low_fraction=0.05):
    """Plot the existing measured alpha against seconds, retaining masked gaps."""
    import matplotlib.pyplot as plt

    time = history["time_s"].to_numpy()
    alpha = history["alpha"].to_numpy()
    flow = history["Q"].to_numpy()
    low = np.abs(flow) < low_fraction * np.max(np.abs(flow))
    frames = [int(np.argmax(flow)), len(history) // 4, 3 * (len(history) - 1) // 10]
    points = history.iloc[frames]
    ymax = max(6.3, np.nanmax(alpha) * 1.05)

    with plt.rc_context({"font.family": "Arial", "font.size": 14}):
        fig, ax = plt.subplots(figsize=(10.4, 5.3))
        ax.fill_between(
            time,
            0,
            1,
            where=low,
            step="mid",
            transform=ax.get_xaxis_transform(),
            color="#EFF2F4",
            zorder=0,
        )
        ax.plot(time, alpha, color="#2166A8", lw=2.8, label="Measured α")
        ax.axhline(4 / 3, color="#D57A19", ls="--", lw=1.8, label="Poiseuille α = 1.33")
        ax.scatter(points.time_s, points.alpha, color="#2166A8", s=42, zorder=4)
        label_positions = [(0.025, 1.85), (0.34, 1.95), (0.34, 3.85)]
        for (_, row), position in zip(points.iterrows(), label_positions):
            ax.annotate(
                f"α = {row.alpha:.2f}\nt = {row.time_s:.3f} s",
                xy=(row.time_s, row.alpha),
                xytext=position,
                fontsize=12,
                color="#16446A",
                arrowprops={"arrowstyle": "-", "color": "#66717C", "lw": 0.8},
            )
        if np.any(low):
            ax.text(
                0.65 * time[-1],
                0.75 * ymax,
                f"Low net flow\nα omitted below {100 * low_fraction:g}%\nof local peak |Q|",
                ha="center",
                va="center",
                color="#66717C",
                fontsize=13,
            )
        ax.set(
            xlim=(0, time[-1]),
            ylim=(0.85, ymax),
            xlabel="Time within the cycle (s)",
            ylabel="Momentum coefficient α",
            title=f"Measured α over time at s = {distance_m * 1000:.0f} mm",
        )
        ticks = [0, 0.2, 0.4, 0.6, 0.8, time[-1]]
        ax.set_xticks(ticks, ["0", "0.2", "0.4", "0.6", "0.8", f"{time[-1]:.3f}"])
        ax.set_yticks(np.arange(1, int(ymax) + 1))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#D7DEE4", alpha=0.7, zorder=0)
        ax.legend(loc="upper right", frameon=False, fontsize=12)
        return fig, ax
