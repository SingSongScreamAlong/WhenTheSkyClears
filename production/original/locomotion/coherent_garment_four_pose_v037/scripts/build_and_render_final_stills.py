import runpy
from pathlib import Path
P=Path(__file__).resolve().parent
runpy.run_path(str(P/'build_garment_study.py'),run_name='__main__')
runpy.run_path(str(P/'render_garment_stills.py'),run_name='__main__')
