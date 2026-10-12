"""Optional inspection: run with ParaView's pvpython, not normal Python."""

from pathlib import Path
from paraview.simple import (
    XMLPolyDataReader,
    GetActiveViewOrCreate,
    Show,
    ColorBy,
    ResetCamera,
    Render,
    SaveScreenshot,
)

root = Path(__file__).resolve().parent
wall = XMLPolyDataReader(FileName=[str(root / "results" / "aorta_wall.vtp")])
line = XMLPolyDataReader(FileName=[str(root / "results" / "main_centerline.vtp")])
section = XMLPolyDataReader(FileName=[str(root / "results" / "example_section.vtp")])
view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [1200, 800]

wall_display = Show(wall, view)
ColorBy(wall_display, None)
wall_display.DiffuseColor = [0.75, 0.75, 0.75]
wall_display.Opacity = 0.2
line_display = Show(line, view)
ColorBy(line_display, None)
line_display.DiffuseColor = [0.9, 0.5, 0.1]
line_display.LineWidth = 3
section_display = Show(section, view)
ColorBy(section_display, ("POINTS", "axial_velocity"))
section_display.RescaleTransferFunctionToDataRange(True, False)
section_display.SetScalarBarVisibility(view, True)
ResetCamera(view)
Render(view)
SaveScreenshot(str(root / "results" / "paraview_preview.png"), view)
