import runpy
from pathlib import Path
P=Path(__file__).resolve().parent
runpy.run_path(str(P/'build_color_character.py'),run_name='__main__')
assert (P.parent/'native/WTSC_Boy_Full_Color_Readability_v038.blend').exists()
runpy.run_path(str(P/'render_color_stills.py'),run_name='__main__')
