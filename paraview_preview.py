"""Open exported wall metrics and centerline using ParaView's pvpython.

Run from bundle folder. Requires separate ParaView installation; it is not
imported by the normal notebook kernel. VTP coordinates and shear are SI.
"""
from pathlib import Path
from paraview.simple import (XMLPolyDataReader, GetActiveViewOrCreate, Show,
                            ColorBy, GetColorTransferFunction, ResetCamera,
                            Render, SaveScreenshot)

root = Path(__file__).resolve().parent
wall = XMLPolyDataReader(FileName=[str(root / 'results' / 'actual_wall_metrics.vtp')])
centerline = XMLPolyDataReader(FileName=[str(root / 'results' / 'main_centerline.vtp')])
view = GetActiveViewOrCreate('RenderView')
view.ViewSize = [1400, 900]
display = Show(wall, view)
ColorBy(display, ('POINTS', 'TAWSS_Pa'))
display.RescaleTransferFunctionToDataRange(True, False)
display.SetScalarBarVisibility(view, True)
line_display = Show(centerline, view)
ColorBy(line_display, None)
line_display.DiffuseColor = [0.9, 0.5, 0.1]
line_display.LineWidth = 4.0
ResetCamera(view)
Render(view)
SaveScreenshot(str(root / 'results' / 'paraview_preview.png'), view)
print('Saved results/paraview_preview.png')
