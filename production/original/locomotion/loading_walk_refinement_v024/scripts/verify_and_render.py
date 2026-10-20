from pathlib import Path
import runpy
P=Path(__file__).resolve().parent
runpy.run_path(str(P/'check_continuity_and_coat.py'),run_name='__main__')
runpy.run_path(str(P/'render_review.py'),run_name='__main__')
