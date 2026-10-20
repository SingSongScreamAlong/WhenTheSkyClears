import bpy,json,re,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend'),load_ui=False);s=bpy.context.scene
new=next(o for o in s.objects if o.get('motion_revision')=='v010_polish_continuation');col=new.users_collection[0]
with bpy.data.libraries.load(str(R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'),link=False) as (av,loaded):loaded.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v007']
source=loaded.collections[0];stem=lambda n:re.sub(r'\.\d{3}$','',n);original={stem(o.name):o for o in source.all_objects};err=0.;uv_error=0.;checks=[]
for ob in col.all_objects:
 other=original.get(stem(ob.name))
 if other is None:continue
 if ob.type=='MESH':
  assert len(ob.data.vertices)==len(other.data.vertices)
  a=ob.data.uv_layers.active;b=other.data.uv_layers.active
  if a and b:
   assert len(a.data)==len(b.data);uv_error=max(uv_error,max((x.uv-y.uv).length for x,y in zip(a.data,b.data)))
  if ob.get('skin_region') in ['body','dress'] or 'original head' in ob.name:
   delta=max((a.co-b.co).length for a,b in zip(ob.data.vertices,other.data.vertices));err=max(err,delta);checks.append({'mesh':ob.name,'rest_mesh_max_error_m':delta})
 if ob.type=='ARMATURE':
  for bone in ob.data.bones:err=max(err,(bone.head_local-other.data.bones[bone.name].head_local).length,(bone.tail_local-other.data.bones[bone.name].tail_local).length)
assert err<1e-8 and uv_error<1e-8,(err,uv_error)
imagehashes={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
heads=[o for o in new.children_recursive if o.get('v007_head_exposure')];rows=[];normal_error=0
for f in range(1,169):
 s.frame_set(f);bpy.context.view_layer.update();visible=[o for o in heads if not o.hide_render];assert len(visible)==1 and 'original head and attached braid' in visible[0].name
 rig=next(o for o in new.children_recursive if o.type=='ARMATURE' and o.get('character')=='GIRL');axis=rig.pose.bones['head'].matrix.to_3x3()@__import__('mathutils').Vector((0,0,1));normal_error=max(normal_error,abs(axis.x),abs(axis.z))
 rows.append({'frame':f,'visible_head':visible[0].name})
report={'body_head_mesh_rest_and_skeleton_error_m':err,'UV_error':uv_error,'checks':checks,'packed_source_image_sha256':imagehashes,'all168_original_profile_visible':True,'girl_head_out_of_plane_normal_error':normal_error,'head_exposures':rows,'technical_scope':'Geometry/rest/UV/exposure tests establish preservation, not artistic acceptance.'}
(P/'evidence/art_preservation.json').write_text(json.dumps(report,indent=2));print('ART_PRESERVATION',json.dumps({k:v for k,v in report.items() if k!='head_exposures'}),flush=True)
