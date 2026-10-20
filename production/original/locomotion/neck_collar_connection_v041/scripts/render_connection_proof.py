import bpy,json,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];records=[];start=time.time()
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.frame_set(1);bpy.context.view_layer.update();src=bpy.data.objects['V024 | CLOSE portrait'];d=src.data.copy();d.type='ORTHO';d.ortho_scale=.34;o=bpy.data.objects.new('V041 | matched NECK construction camera',d);S.collection.objects.link(o);o.parent=bpy.data.objects['V021 | CHILD_SUPPORT_TRAVEL'];o.rotation_euler=src.matrix_world.to_euler();direction=o.rotation_euler.to_quaternion()@Vector((0,0,-1));o.location=Vector((.015,0,1.105))-direction*4;return S,o
for mode,path in [('CANDIDATE',P/'native/WTSC_Neck_Collar_Connection_Candidate_v041.blend'),('BASELINE',P/'reference/PRESERVED_PAINTED_WALK_v040.blend')]:
 S,detail=load(path)
 for view,cam,size,frames in ([('HERO',bpy.data.objects['V024 | CLOSE portrait'],(960,1440),[1]),('CLOSE',bpy.data.objects['V024 | CLOSE portrait'],(480,720),[1,4,11,20,27,32]),('SHOT',bpy.data.objects['V020 | CHILD | SHOT'],(1280,720),[1,20]),('DETAIL',detail,(640,480),[1,11,20,27])] if mode=='CANDIDATE' else [('DETAIL',detail,(640,480),[1,11,20,27])]):
  S.camera=cam;S.render.resolution_x,S.render.resolution_y=size;folder=P/'previews'/(mode+'_'+view);folder.mkdir(exist_ok=True)
  for f in frames:S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'mode':mode,'view':view,'frame':f,'size':size});print('V041_PROOF',mode,view,f,flush=True)
(P/'evidence/PROOF_RENDER_RECORD.json').write_text(json.dumps({'records':records,'actual_native_stills':len(records),'elapsed_seconds':time.time()-start,'threads':2,'scope':'Matched native construction proof, separate from artistic acceptance. Existing source not saved.'},indent=2));print('V041_PROOF_COMPLETE',flush=True)
