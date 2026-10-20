import bpy,math,json,ast
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'),load_ui=False,use_scripts=False);RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];TARGET=json.loads((ROOT/'locomotion/age10_proportion_candidate_v044/evidence/STATIC_SCALE_BUILD.json').read_text())['candidate_measurements'];PERIOD=32.;STANCE=18.8;FOOT={}
for who,r in RIGS.items():
 b=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith('near'));off=[Vector((p.co.x,0,p.co.z-TARGET[who]['estimated_ankle_joint_z_m'])) for p in b.data.vertices];z=min(p.z for p in off);FOOT[who]={'offsets':off,'heel':min(p.x for p in off if p.z<=z+.000001)}
tree=ast.parse((P/'scripts/build_steady_walk.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['D','ease5','ease3','rot','angle','support_geometry','stance','foot']];exec(compile(tree,'authored_foot_paths','exec'),globals());report=[]
for STRIDE in [.80,.79,.78,.77]:
 out={'stride_m':STRIDE,'hip_offset_m':.032,'characters':{}}
 for who,r in RIGS.items():
  lowest=(999,None)
  for i in range(256):
   f=1+i/8;phi=math.tau*(f-1)/32;H=Vector((.0015*math.sin(2*phi),0,TARGET[who]['estimated_hip_joint_z_m']-.032+.026*math.sin(phi)**2))
   for side in ['near','far']:
    A,_,meta=foot(f,who,side);margin=r.data.bones['thigh_'+side].length+r.data.bones['shin_'+side].length-(A-H).length
    if margin<lowest[0]:lowest=(margin,{'frame':f,'side':side,'stance':meta['stance'],'hip':list(H),'ankle':list(A)})
  out['characters'][who]={'minimum_reach_margin_m':lowest[0],'worst_pose':lowest[1]}
 report.append(out)
(P/'evidence/AUTHORED_REACH_SELECTION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
