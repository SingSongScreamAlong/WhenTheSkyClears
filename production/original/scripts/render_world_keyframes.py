from pathlib import Path
from create_native_drawings import call
ROOT=Path(__file__).resolve().parents[1]
for label,seconds in [('Village',0),('Woods',28),('School',43),('Battlefield',58),('Ash',74),('Title',95),('Black',2399/24)]:
    frame=round(seconds*24)+1
    call('blender_scripting__execute_python',{'code':f'import bpy\nbpy.context.scene.frame_set({frame})\nprint(bpy.context.scene.frame_current)'})
    dest=ROOT/'renders/world'/f'{label}_World_4K_v002.png'
    call('blender_render__render_scene',{'output_path':str(dest),'write_still':True})
    print(label,frame,str(dest),flush=True)
