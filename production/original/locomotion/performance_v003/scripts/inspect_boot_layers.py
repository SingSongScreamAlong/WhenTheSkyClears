import bpy,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Performance_Library_v003.blend'),load_ui=False)
runpy.run_path(str(P/'scripts/configure_performance.py'))['configure']('WEARY_STUMBLE_RECOVER',root_motion=False)
s=bpy.context.scene;s.frame_set(41)
for ob in s.objects:
    if ob.parent and ob.parent.type=='ARMATURE':ob.hide_render='rigid original boot' not in ob.name
s.render.filepath=str(P/'evidence/rigid_boots_only_041.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:
    if ob.parent and ob.parent.type=='ARMATURE':ob.hide_render=not str(ob.get('skin_region','')).startswith('leg_')
s.render.filepath=str(P/'evidence/leg_regions_only_041.png');bpy.ops.render.render(write_still=True)
