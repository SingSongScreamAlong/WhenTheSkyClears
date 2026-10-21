import bpy,json,hashlib
from pathlib import Path
R=Path(r"WTSC_LOCAL_WORKSPACE")
P=R/'characters/rig_capability_audit_v016'
source=R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update()
rigs=[o for o in S.objects if o.type=='ARMATURE' and o.get('character')]
report={}
for rig in rigs:
 w=rig['character'];report[w]={'bones':{},'meshes':[]}
 for b in rig.data.bones:
  pb=rig.pose.bones[b.name]
  report[w]['bones'][b.name]={'rest_head':list(b.head_local),'rest_tail':list(b.tail_local),'pose_head':list(pb.head),'pose_tail':list(pb.tail),'matrix':[list(row) for row in pb.matrix]}
 for o in rig.children:
  if o.type!='MESH' or o.hide_render:continue
  report[w]['meshes'].append({'name':o.name,'role':o.get('v007_role'),'vertices':len(o.data.vertices),'groups':[g.name for g in o.vertex_groups],'shape_keys':len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0,'matrix_local':[list(row) for row in o.matrix_local]})
(P/'evidence/source_pose_structure.json').write_text(json.dumps(report,indent=2))
print('FRAMES',S.frame_start,S.frame_end,[(r.name,[(st.frame_start,st.frame_end) for tr in r.animation_data.nla_tracks for st in tr.strips]) for r in rigs]);print('V016_SOURCE_INSPECTED',source.name,hashlib.sha256(source.read_bytes()).hexdigest())
