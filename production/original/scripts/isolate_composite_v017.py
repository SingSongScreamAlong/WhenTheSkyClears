import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;s.frame_set(1);s.render.resolution_percentage=50;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for label,prefixes in [('without_new_fx',['v016 | 05','v016 | 06']),('without_regional_sets',['v016 | 05','v016 | 06','v016 | 02','v016 | 04','v016 | 07']),('original_cards_only',['v016 | 05','v016 | 06','v016 | 02','v016 | 04','v016 | 07','v016 | 03'])]:
    for c in bpy.data.collections:
        if any(c.name.startswith(p) for p in prefixes):c.hide_render=True
    s.render.filepath=str(R/'renders/world_v016/inspection_v017'/('isolate_'+label+'.png'));bpy.ops.render.render(write_still=True)
