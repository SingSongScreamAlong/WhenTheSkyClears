import bpy,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Performance_Library_v003.blend'),load_ui=False)
runpy.run_path(str(P/'scripts/configure_performance.py'))['configure']('WEARY_STUMBLE_RECOVER',root_motion=False)
s=bpy.context.scene;s.objects['LOCO | clip label'].data.body='WEARY STUMBLE / v003 cleanup proof'
for f in [19,29,31,35,41,49,65]:
    s.frame_set(f);s.render.filepath=str(P/f'previews/stumble_proof_{f:03d}.png');bpy.ops.render.render(write_still=True)
