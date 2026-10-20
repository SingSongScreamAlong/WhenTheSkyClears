import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
BASE=R/'characters/rig_capability_audit_v016/native/WTSC_Painted_Rig_Capability_v016.blend';NEW=P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend'
def pts(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def uv(o):return [tuple(o.data.uv_layers.active.data[l.index].uv) for l in o.data.loops]
def weights(o):return [[(o.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in o.data.vertices]
def rigs():return {o['character']:o for o in bpy.context.scene.objects if o.type=='ARMATURE'}
def area(vs,poly):
 p=[vs[i] for i in poly.vertices];return sum(a.x*b.z-b.x*a.z for a,b in zip(p,p[1:]+p[:1]))*.5
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene;br=rigs();baseline={};data={}
for r in br.values():
 for o in r.children:
  if o.type=='MESH':data[o.name]={'uv':uv(o),'weights':weights(o),'materials':[m.name for m in o.data.materials],'vertices':len(o.data.vertices)}
for f in range(1,222,20):
 S.frame_set(f);bpy.context.view_layer.update();baseline[f]={'bones':{w:{b.name:[list(row) for row in b.matrix] for b in r.pose.bones} for w,r in br.items()},'boots':{o.name:pts(o) for r in br.values() for o in r.children if o.get('v007_role')=='support_boot'},'areas':{o.name:[area(pts(o),p) for p in o.data.polygons] for r in br.values() for o in r.children if o.type=='MESH' and (o.get('skin_region') in ['body','dress'] or o.get('v007_role')=='drawn_leg')}}
bpy.ops.wm.open_mainfile(filepath=str(NEW),load_ui=False,use_scripts=False);S=bpy.context.scene;rr,cc=api.initialize_from_scene();report={'IK_chains':sum(c.type=='IK' for r in rr.values() for b in r.pose.bones for c in b.constraints),'static_tests':[],'source_reuse':[]}
for r in rr.values():
 for o in r.children:
  if o.type=='MESH':
   old=data[o.name];report['source_reuse'].append({'mesh':o.name,'base_UV_exact':uv(o)==old['uv'],'body_weights_exact':weights(o)==old['weights'] if o.get('skin_region') in ['body','dress'] else None,'materials_exact':[m.name for m in o.data.materials]==old['materials'],'base_vertex_count_exact':len(o.data.vertices)==old['vertices']})
for f in range(1,222,20):
 S.frame_set(f);bpy.context.view_layer.update();errors=[];bootdrift=0;flips={};finite=True
 for w,r in rr.items():
  errors.extend(abs(b.matrix[i][j]-baseline[f]['bones'][w][b.name][i][j]) for b in r.pose.bones for i in range(4) for j in range(4))
  for o in r.children:
   if o.type!='MESH':continue
   pp=pts(o);finite=finite and all(math.isfinite(x) for p in pp for x in p)
   if o.get('v007_role')=='support_boot':bootdrift=max(bootdrift,max((a-b).length for a,b in zip(pp,baseline[f]['boots'][o.name])))
   if o.name in baseline[f]['areas']:
    old=baseline[f]['areas'][o.name];new=[area(pp,p) for p in o.data.polygons];flips[o.name]=sum(a*b<0 for a,b in zip(old,new) if abs(a)>1e-8)
 report['static_tests'].append({'frame':f,'bone_matrix_error':max(errors),'boot_geometry_delta_m':bootdrift,'IK':api.reach_report(),'additional_signed_polygon_flips':flips,'finite_geometry':finite})
# Fresh off-cache native edits, no keyed Action interference.
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v017.blend'),load_ui=False,use_scripts=False);rr,cc=api.initialize_from_scene();S=bpy.context.scene
meshes=[o for r in rr.values() for o in r.children if o.type=='MESH'];before={o.name:pts(o) for o in meshes};boots=[o for o in meshes if o.get('v007_role')=='support_boot']
for w in rr:
 c=cc[w,'HIP'];M=c.matrix_world.copy();M.translation+=Vector((.012,0,-.015));c.matrix_world=M
bpy.context.view_layer.update();report['off_cache_HIP']={'all16_response_m':{o.name:max((a-b).length for a,b in zip(before[o.name],pts(o))) for o in meshes if o.get('v007_role') in ['drawn_leg','drawn_arm','drawn_cuff']},'boot_drift_m':max(max((a-b).length for a,b in zip(before[o.name],pts(o))) for o in boots),'IK':api.reach_report(),'actions':len(bpy.data.actions)}
for w,r in rr.items():
 S0=r.pose.bones['upper_arm_near'].head;W=r.pose.bones['forearm_near'].tail;d=(W-S0).normalized();length=(r.data.bones['upper_arm_near'].length+r.data.bones['forearm_near'].length+abs(r.data.bones['upper_arm_near'].length-r.data.bones['forearm_near'].length))*.5;target=S0+d*length;api.set_wrist(w,'near',target.x,target.z,-60,'Reach');api.choose_planes(w,{})
report['off_cache_wrist']={'IK':api.reach_report(),'arm_response_m':{o.name:max((a-b).length for a,b in zip(before[o.name],pts(o))) for o in meshes if o.get('v007_role') in ['drawn_arm','drawn_cuff']}}
S.render.filepath=str(P/'previews/OFF_CACHE_NATIVE_EDIT.png');bpy.ops.render.render(write_still=True)
known=json.loads((P/'evidence/v016_baseline_hashes.json').read_text());report['v016_sources_unchanged']={path:hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in known.items()}
report['gates']={'eight_IK_chains':report['IK_chains']==8,'original_bone_poses_unchanged':all(x['bone_matrix_error']<1e-6 for x in report['static_tests']),'boots_unchanged':all(x['boot_geometry_delta_m']<1e-6 for x in report['static_tests']),'UV_materials_base_topology_retained':all(x['base_UV_exact'] and x['materials_exact'] and x['base_vertex_count_exact'] for x in report['source_reuse']),'body_weights_retained':all(x['body_weights_exact'] is not False for x in report['source_reuse']),'all_static_IK_reachable':all(y['reachable'] for x in report['static_tests'] for y in x['IK']),'off_cache_all16_respond':all(v>1e-5 for v in report['off_cache_HIP']['all16_response_m'].values()),'off_cache_boots_fixed':report['off_cache_HIP']['boot_drift_m']<1e-6,'finite_geometry':all(x['finite_geometry'] for x in report['static_tests']),'v016_immutable':all(report['v016_sources_unchanged'].values())}
(P/'evidence/core_validation.json').write_text(json.dumps(report,indent=2));print('V017_CORE_GATES',json.dumps(report['gates']));print('ADDITIONAL_FLIPS',[(x['frame'],x['additional_signed_polygon_flips']) for x in report['static_tests'] if any(x['additional_signed_polygon_flips'].values())])
