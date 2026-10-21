import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
src=P/'reference/PRESERVED_v046_INPUT.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='0bac9af67c64a3a215093033c384c063e3631f6dcf8c3e7b63abe8184c9b5dd9'
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
S=bpy.context.scene
R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
out={'scene':S.name,'range':[S.frame_start,S.frame_end],'fps':S.render.fps,'samples':{},'rigs':{},'wardrobe':{}}
for w,r in R.items():
 out['rigs'][w]={'matrix_world':[list(z) for z in r.matrix_world],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in r.data.bones}}
 out['wardrobe'][w]=[]
 for o in bpy.data.objects:
  if o.parent==r and o.get('wardrobe_role') in ['sleeve','hand','skin']:
   out['wardrobe'][w].append({'name':o.name,'role':o.get('wardrobe_role'),'count':len(o.data.vertices),'location':list(o.location),'matrix_basis':[list(z) for z in o.matrix_basis],'matrix_parent_inverse':[list(z) for z in o.matrix_parent_inverse],'materials':[m.name for m in o.data.materials],'props':{k:o[k] for k in o.keys()},'local_bounds':[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)],'shape_keys':len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0})
for f in [1,9,17,25,32,40,55,63,94]:
 S.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();q={}
 for w,r in R.items():
  e=r.evaluated_get(dg);q[w]={}
  for n in ['chest','upper_arm_near','forearm_near','hand_near','upper_arm_far','forearm_far','hand_far','foot_near','foot_far']:
   b=e.pose.bones[n];q[w][n]={'head_world':list(e.matrix_world@b.head),'tail_world':list(e.matrix_world@b.tail),'head':list(b.head),'tail':list(b.tail),'matrix':[list(z) for z in b.matrix]}
  q[w]['root_matrix_world']=[list(z) for z in e.matrix_world]
 out['samples'][str(f)]=q
out['source_preserved']=hashlib.sha256(src.read_bytes()).hexdigest()=='0bac9af67c64a3a215093033c384c063e3631f6dcf8c3e7b63abe8184c9b5dd9'
(P/'evidence/PAIRED_REACH_SOURCE_POSE_PROBE.json').write_text(json.dumps(out,indent=2))
print('PAIRED_REACH_READONLY_PROBE_DONE',flush=True)
