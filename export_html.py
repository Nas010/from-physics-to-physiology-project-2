"""Export saved notebook outputs to HTML with a bundled, offline math renderer.

Run `python export_html.py` after saving the executed notebook. No kernel runs,
no data downloads and no network connection are needed for this export.
"""
from pathlib import Path
import re
import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent

def export_html() -> Path:
    """Render the saved notebook without clearing or re-executing its outputs."""
    notebook = nbformat.read(ROOT / 'FtP_Aorta_1D_Assumptions.ipynb', as_version=4)
    html, _ = HTMLExporter().from_notebook_node(notebook)
    math_renderer = r'''<!-- Offline MathJax 3.2.2; Apache-2.0 license in assets/mathjax/LICENSE. -->
<script>
window.MathJax = {
  tex: {inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$'], ['\\[', '\\]']], processEscapes: true},
  svg: {fontCache: 'local'},
  options: {enableMenu: false}
};
</script>
<script defer src="assets/mathjax/tex-svg-full.js"></script>'''
    html = re.sub(r'<!-- Load mathjax -->.*?<!-- End of mathjax configuration -->',
                  lambda _: math_renderer, html, count=1, flags=re.S)
    target = ROOT / 'notebook.html'
    target.write_text(html, encoding='utf-8')
    return target

if __name__ == '__main__':
    print(export_html())
