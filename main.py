"""Regenerate the notebook results: run `python main.py` from this folder."""

from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

from export_html import export_html


def main():
    """Run the analysis with the same Python environment as this script."""
    root = Path(__file__).resolve().parent
    path = root / "FtP_Aorta_1D_Assumptions.ipynb"
    notebook = nbformat.read(path, as_version=4)

    # Use this environment, even if another Jupyter kernel is installed.
    kernel = KernelManager(kernel_name="python3")
    kernel.kernel_spec.argv[0] = sys.executable
    client = NotebookClient(
        notebook, km=kernel, timeout=600, resources={"metadata": {"path": str(root)}}
    )
    print("Running the Project 2 notebook...")
    client.execute(cleanup_kc=True)

    # Save only after the complete run succeeds.
    nbformat.write(notebook, path)
    export_html()
    print("Done. Figures and tables are in results/; preview is notebook.html.")


if __name__ == "__main__":
    main()
