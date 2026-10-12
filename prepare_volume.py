"""Optional raw-volume preparation for the aorta notebook.

The supplied section archive is already prepared. This script is included so
the interpolation and near-wall sampling can be inspected and repeated.
It is not needed for the normal notebook run.
"""

from pathlib import Path
import argparse
import json
import numpy as np
import pyvista as pv
import vtk
from scipy.sparse import csr_matrix, vstack
import aorta_functions as af

section_from_volume = af.section_from_volume


def tetra_probe_matrix(volume, points, locator=None, interior_target=None):
    """Linear-tetra interpolation matrix, with positive in-domain barycentric weights.

    Cache geometry once for rigid meshes. Do not use nearest-node interpolation
    for pressure/velocity. Every probe must belong to a tetrahedron.
    """
    if not np.all(volume.celltypes == int(pv.CellType.TETRA)):
        raise ValueError("Packed extractor currently requires a linear-tetra mesh.")
    if locator is None:
        locator = vtk.vtkStaticCellLocator()
        locator.SetDataSet(volume)
        locator.BuildLocator()

    # Find the containing tetrahedron for each requested sample.
    sample_points = np.asarray(points, float)
    if interior_target is not None:
        # Submicrometre inward shift handles roundoff at cut-wall endpoints.
        sample_points = sample_points + 1e-7 * (
            np.asarray(interior_target) - sample_points
        )
    generic = vtk.vtkGenericCell()
    pcoords = [0.0, 0.0, 0.0]
    vtkweights = [0.0] * 4
    cellids = np.array(
        [
            locator.FindCell(point, 1e-18, generic, pcoords, vtkweights)
            for point in sample_points
        ]
    )
    if np.any(cellids < 0):
        raise ValueError(
            f"{np.count_nonzero(cellids<0)} interpolation probes outside lumen."
        )

    # Calculate the four vertex weights from the sample coordinates.
    tetra = np.asarray(volume.cell_connectivity).reshape(-1, 4)[cellids]
    vertices = volume.points[tetra]
    matrix = (vertices[:, 1:] - vertices[:, 0, None, :]).transpose(0, 2, 1)
    weights3 = np.linalg.solve(matrix, (sample_points - vertices[:, 0])[..., None])[
        ..., 0
    ]
    weights = np.c_[1 - weights3.sum(axis=1), weights3]
    bad = np.flatnonzero(
        (weights.min(axis=1) < -1e-7) | (weights.max(axis=1) > 1 + 1e-7)
    )
    connectivity = np.asarray(volume.cell_connectivity).reshape(-1, 4)
    for row in bad:
        # VTK accepts parametric tolerance and may return a neighboring sliver.
        # Inspect candidate bounding boxes, then select by actual barycentric fit.
        point = sample_points[row]
        candidates = vtk.vtkIdList()
        pad = 1e-8
        bounds = np.column_stack([point - pad, point + pad]).ravel().tolist()
        locator.FindCellsWithinBounds(bounds, candidates)
        cell_candidates = np.array(
            [candidates.GetId(k) for k in range(candidates.GetNumberOfIds())], int
        )
        vertex_ids = connectivity[cell_candidates]
        vv = volume.points[vertex_ids]
        matrices = (vv[:, 1:] - vv[:, 0, None, :]).transpose(0, 2, 1)
        ww3 = np.linalg.solve(matrices, (point - vv[:, 0])[..., None])[..., 0]
        ww = np.c_[1 - ww3.sum(axis=1), ww3]
        score = np.maximum(-ww.min(axis=1), ww.max(axis=1) - 1)
        best = int(np.argmin(score))
        tetra[row] = vertex_ids[best]
        weights[row] = ww[best]
    if np.min(weights) < -1e-5 or np.max(weights) > 1 + 1e-5:
        raise ValueError(
            f"Invalid barycentric weights after candidate search: {weights.min():.3g}, {weights.max():.3g}."
        )

    # Remove tiny roundoff errors and assemble the sparse interpolation matrix.
    weights = np.clip(weights, 0, 1)
    weights /= weights.sum(axis=1)[:, None]
    rows = np.repeat(np.arange(len(points)), 4)
    return csr_matrix(
        (weights.ravel(), (rows, tetra.ravel())), shape=(len(points), volume.n_points)
    )


def contour_inward_probes(contour, tangent, depth):
    """Wall midpoints displaced inward at depth and 2*depth, with length weights."""
    pts, lengths, _ = contour
    edge = np.roll(pts, -1, axis=0) - pts
    midpoint = (pts + np.roll(pts, -1, axis=0)) / 2
    normal = np.cross(edge, tangent)
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    if np.mean(np.sum(normal * (midpoint - midpoint.mean(axis=0)), axis=1)) < 0:
        normal = -normal
    return np.r_[midpoint - depth * normal, midpoint - 2 * depth * normal], lengths


def extract_packed_volume(
    path,
    s,
    origins,
    tangents,
    valid,
    contours,
    times,
    steps,
    units,
    output,
    signature,
    nu,
    depth=0.0003,
):
    """Reduce packed VMR volume into actual filled sections and wall probes.

    Read only pressure/velocity for each step. Precompute slice and probe
    stencils for rigid geometry. Results stay tied to source hash and geometry.
    No 3D field is fabricated from the surface result. Archive average_pressure
    arrays are not used: actual pressure_STEP fields are selected explicitly.
    """

    # Read geometry first, without loading every time-dependent field.
    reader = pv.get_reader(path)
    reader.disable_all_point_arrays()
    reader.disable_all_cell_arrays()
    geometry = reader.read()
    geometry.points = np.asarray(geometry.points, float) * units["length"]
    if geometry.n_points != 608192 or geometry.n_cells != 3268267:
        raise ValueError("Unexpected model volume topology; verify dataset identity.")
    locator = vtk.vtkStaticCellLocator()
    locator.SetDataSet(geometry)
    locator.BuildLocator()
    cache = {}
    stencils = []
    probe_stencils = []
    section_ids = []
    counts = []
    probe_counts = []

    # Precompute section and near-wall interpolation for the fixed mesh.
    for i in np.flatnonzero(valid):
        section = section_from_volume(geometry, origins[i], tangents[i])
        if abs(section.area / contours[i][2] - 1) > 0.03:
            raise ValueError(f"Section {i} area differs >3% from wall contour.")
        section_ids.append(i)
        counts.append(section.n_points)
        cache[f"points_{i}"] = np.asarray(section.points)
        cache[f"faces_{i}"] = np.asarray(section.faces)
        stencils.append(
            tetra_probe_matrix(geometry, section.points, locator, origins[i])
        )
        probe, lengths = contour_inward_probes(contours[i], tangents[i], depth)
        probe_half, _ = contour_inward_probes(contours[i], tangents[i], depth / 2)
        probe_stencils.append(
            (
                tetra_probe_matrix(geometry, probe, locator),
                tetra_probe_matrix(geometry, probe_half, locator),
            )
        )
        cache[f"wall_lengths_{i}"] = lengths
        probe_counts.append(len(lengths))
        print(
            f"Volume geometry stencil {len(section_ids)}/{np.count_nonzero(valid)}",
            flush=True,
        )
    section_ids = np.array(section_ids, int)
    offsets = np.r_[0, np.cumsum(counts)]

    # Assemble sparse matrices once; each frame requires only matrix products.
    section_matrix = vstack(stencils, format="csr")
    probe_matrix = vstack([x[0] for x in probe_stencils], format="csr")
    probe_half_matrix = vstack([x[1] for x in probe_stencils], format="csr")

    # Allocate the compact arrays, then read one frame at a time.
    velocity = np.empty((len(steps), offsets[-1], 3), dtype=np.float32)
    pressure = np.empty((len(steps), offsets[-1]), dtype=np.float32)
    f = np.full((len(steps), len(s)), np.nan)
    f_half = np.full_like(f, np.nan)
    probe_offsets = np.r_[0, np.cumsum(np.array(probe_counts) * 2)]
    for j, step in enumerate(steps):
        reader.disable_all_point_arrays()
        reader.enable_point_array(f"velocity_{step}")
        reader.enable_point_array(f"pressure_{step}")
        data = reader.read()
        vel = np.asarray(data[f"velocity_{step}"]) * units["velocity"]
        pre = np.asarray(data[f"pressure_{step}"]) * units["pressure"]
        if vel.shape != (geometry.n_points, 3) or pre.shape != (geometry.n_points,):
            raise ValueError("Packed volume field shape mismatch.")
        if not np.all(np.isfinite(vel)) or not np.all(np.isfinite(pre)):
            raise ValueError("Nonfinite packed volume fields.")
        velocity[j] = section_matrix @ vel
        pressure[j] = section_matrix @ pre
        probe_velocity = probe_matrix @ vel
        probe_half_velocity = probe_half_matrix @ vel
        for k, i in enumerate(section_ids):
            n = probe_counts[k]
            sl = slice(probe_offsets[k], probe_offsets[k + 1])
            lengths = cache[f"wall_lengths_{i}"]
            v = probe_velocity[sl]
            vh = probe_half_velocity[sl]

            # Second-order inward derivative with no-slip u_wall=0.
            derivative = (4 * v[:n] - v[n:]) / (2 * depth)
            derivative_half = (4 * vh[:n] - vh[n:]) / depth
            f[j, i] = nu * np.sum(lengths * (derivative @ tangents[i]))
            f_half[j, i] = nu * np.sum(lengths * (derivative_half @ tangents[i]))
        if j % 10 == 0 or j == len(steps) - 1:
            print(f"Volume fields {j+1}/{len(steps)}", flush=True)

    # Save geometry, fields and the extraction signature together.
    cache.update(
        {
            "section_ids": section_ids,
            "offsets": offsets,
            "velocity_m_s": velocity,
            "pressure_Pa": pressure,
            "f_wall_probe_m3_s2": f,
            "f_wall_probe_half_m3_s2": f_half,
            "time_s": np.asarray(times),
            "steps": np.asarray(steps),
            "s_m": np.asarray(s),
            "wall_probe_depth_m": np.array(depth),
            "signature_json": np.array(json.dumps(signature, sort_keys=True)),
        }
    )
    np.savez_compressed(output, **cache)
    return cache


def main():
    """Re-extract sections only when given the original volume file explicitly."""
    parser = argparse.ArgumentParser(
        description="Prepare actual sections from the original model VTU."
    )
    parser.add_argument(
        "volume", type=Path, help="Path to the original 5.55 GB packed volume VTU"
    )
    args = parser.parse_args()
    if not args.volume.is_file():
        parser.error("The volume file does not exist.")
    root = Path(__file__).resolve().parent
    geometry = af.load_geometry(root)
    nu, dt, period = 0.004 / 1060.0, 0.000937, 0.937
    times, steps, _ = af.read_cap_flows(geometry, dt, period)
    output = root / "data" / "actual_volume_sections.npz"
    metadata_path = output.with_suffix(".json")
    metadata = json.loads(metadata_path.read_text())
    metadata.update(
        {
            "model_sha256": af.sha256_file(geometry["model_path"]),
            "centerline_sha256": af.sha256_file(geometry["centerline_path"]),
            **geometry["settings"],
            "source_dt_s": dt,
            "period_s": period,
            "kinematic_viscosity_m2_s": nu,
            "units": af.SOURCE_UNITS,
            "volume_sha256": af.sha256_file(args.volume),
        }
    )
    temporary = output.with_name("actual_volume_sections.preparing.npz")
    extract_packed_volume(
        args.volume,
        geometry["s_m"],
        geometry["points"],
        geometry["tangents"],
        geometry["valid"],
        geometry["contours"],
        times,
        steps,
        af.SOURCE_UNITS,
        temporary,
        metadata,
        nu,
    )
    # Keep the supplied archive until the new extraction has completed.
    temporary.replace(output)
    metadata_path.write_text(json.dumps(metadata, indent=2))
    print("Prepared data/actual_volume_sections.npz")


if __name__ == "__main__":
    main()
