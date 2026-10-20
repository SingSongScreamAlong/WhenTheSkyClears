from pathlib import Path
import runpy
P=Path(__file__).resolve().parent
runpy.run_path(str(P/'refine_upper_loading_v025b.py'),run_name='__main__')
runpy.run_path(str(P/'build_pigment_study_v025b.py'),run_name='__main__')
