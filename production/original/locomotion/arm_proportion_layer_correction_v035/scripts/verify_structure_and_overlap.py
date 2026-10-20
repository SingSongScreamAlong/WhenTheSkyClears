import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];out={'scope':'Cold structure/occlusion checks; not artistic acceptance','variants':{}};saved={}
def dist(p,a,b):
 d=Vector((b.x-a.x,b.z-a.z));v=Vector((p.x-a.x,p.z-a.z));return abs(d.x*v.y-d.y*v.x)/d.length
for variant,file in [('SOURCE',P/'reference/PREFERRED_v033.blend'),('ALL',P/'native/WTSC_Arm_and_Leg_Structure_v035.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];rows=[]
 for i in range(125):
  f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();r={'frame':f,'legs':{}}
  for side in ['near','far']:
   a=rig.pose.bones['thigh_'+side];b=rig.pose.bones['shin_'+side];H=rig.matrix_world@a.head;K=rig.matrix_world@a.tail;A=rig.matrix_world@b.tail;o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());V=[e.matrix_world@v.co for v in e.data.vertices];C=[(V[j*7]+V[j*7+6])*.5 for j in range(97)];r['legs'][side]={'H':list(H),'K':list(K),'A':list(A),'thigh_m':(K-H).length,'shin_m':(A-K).length,'join_m':(a.tail-b.head).length,'thigh_axis_drawing_max_deviation_m':max(dist(C[j],H,K) for j in range(18,47)),'shin_axis_drawing_max_deviation_m':max(dist(C[j],K,A) for j in range(65,78)),'cuff':[list(p) for p in V[-7:]]}
  rows.append(r)
 out['variants'][variant]={'samples':rows}
 # Actual far-hand masks at F20. No forced global front layer.
 S.frame_set(20);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;o=bpy.data.objects['V007_BOY | articulated drawn hand far'];m=bpy.data.materials.new('V035 actual hand ID');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.01,1,.01,1);outn=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],outn.inputs['Surface']);o.material_slots[0].link='OBJECT';o.material_slots[0].material=m;vis={q.name:q.hide_render for q in S.objects if q.type in ['MESH','GREASEPENCIL','CURVE']};states=[('FULL',[]),('NO_FAR_TROUSER',['V024 continuous far trouser drawing']),('NO_NEAR_TROUSER',['V024 continuous near trouser drawing']),('NO_COAT',['V025 | COAT drawings | editable GP']),('NO_COAT_OR_NEAR_TROUSER',['V025 | COAT drawings | editable GP','V024 continuous near trouser drawing']),('ISOLATED',[n for n in vis if n!=o.name])]
 for name,hidden in states:
  for n,v in vis.items():bpy.data.objects[n].hide_render=v
  for n in hidden:bpy.data.objects[n].hide_render=True
  folder=P/'previews'/('OVERLAP_'+variant);folder.mkdir(exist_ok=True);S.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
source=out['variants']['SOURCE']['samples'];candidate=out['variants']['ALL']['samples'];maxjoint=max((Vector(a['legs'][s][k])-Vector(b['legs'][s][k])).length for a,b in zip(source,candidate) for s in ['near','far'] for k in ['H','K','A']);maxcuff=max((Vector(v)-Vector(w)).length for a,b in zip(source,candidate) for s in ['near','far'] for v,w in zip(a['legs'][s]['cuff'],b['legs'][s]['cuff']));summary={}
for variant in ['SOURCE','ALL']:
 summary[variant]={}
 for side in ['near','far']:
  V=[r['legs'][side] for r in out['variants'][variant]['samples']];summary[variant][side]={k:[min(r[k] for r in V),max(r[k] for r in V)] for k in ['thigh_m','shin_m']};summary[variant][side].update({k:max(r[k] for r in V) for k in ['join_m','thigh_axis_drawing_max_deviation_m','shin_axis_drawing_max_deviation_m']})
out['summary']=summary;out['max_actual_leg_joint_change_m']=maxjoint;out['max_exact_cuff_ring_change_m']=maxcuff;(P/'evidence/COLD_STRUCTURE_AND_OVERLAP_CHECK.json').write_text(json.dumps(out,indent=2));assert maxjoint<2e-5 and maxcuff<2e-5
print('V035_COLD_STRUCTURE_COMPLETE',json.dumps({'max_joint_change_m':maxjoint,'max_cuff_change_m':maxcuff,'summary':summary}),flush=True)
