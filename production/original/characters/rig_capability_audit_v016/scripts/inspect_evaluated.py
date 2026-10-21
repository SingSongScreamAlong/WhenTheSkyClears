import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;out=[]
for f in [1,21,161]:
 S.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for r in [o for o in S.objects if o.type=='ARMATURE']:
  d={'frame':f,'who':r['character'],'bones':{},'ends':{}}
  for n in ['pelvis','chest','upper_arm_near','forearm_near','hand_near','thigh_near','shin_near','foot_near']:
   b=r.pose.bones[n];d['bones'][n]={'head':list(b.head),'tail':list(b.tail),'matrix':[list(row) for row in b.matrix]}
  for o in r.children:
   if o.type=='MESH' and o.get('v007_role') in ['drawn_leg','support_boot','drawn_hand'] and o.name.endswith('near'):
    ev=o.evaluated_get(dg);vs=[r.matrix_world.inverted()@ev.matrix_world@v.co for v in ev.data.vertices]
    d['ends'][o.name]={'first':list(vs[0]),'last':list(vs[-1]),'max_z':max(v.z for v in vs),'min_z':min(v.z for v in vs),'center':list(sum(vs,Vector())/len(vs))}
    if o.get('v007_role')=='drawn_leg':
     d['ends'][o.name]['end_center']=list((vs[-1]+vs[-2])*.5)
     for n in ['H','K','boot collar']:
      ob=bpy.data.objects.get(o.name+' | '+n);d['ends'][o.name][n]=list(r.matrix_world.inverted()@ob.matrix_world.translation)
  w=bpy.data.objects[r['character']+' | WRIST_near'];d['wrist']={k:w[k] for k in w.keys()};out.append(d)
(P/'evidence/evaluated_geometry_debug.json').write_text(json.dumps(out,indent=2,default=list))
print('GEOMETRY_DEBUG_SAVED')
