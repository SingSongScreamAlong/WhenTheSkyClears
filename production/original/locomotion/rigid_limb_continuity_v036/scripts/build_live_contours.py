import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import live_leg_graph as L
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_v035.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];fore=S.view_layers['V025 | original foreground'];cache={}
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();fore.update()
def pts(o,vl=None):
 vl=vl or bpy.context.view_layer;vl.update();e=o.evaluated_get(vl.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
def h(a):return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
actions={a.name:h(a) for a in bpy.data.actions};protected=['PERF_BOY | original head','V033 | near | canonical painted shoe','V033 | far | canonical painted shoe','V007_BOY | articulated drawn hand near','V007_BOY | articulated drawn hand far'];fgn={o.name for o in bpy.data.collections['V025 | retained foreground identity'].all_objects}
for i in range(249):
 f=1+i/8;frame(f);cache[f]={'bones':{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones},'protected':{n:pts(bpy.data.objects[n],fore if n in fgn else None) for n in protected},'cuffs':{s:pts(bpy.data.objects['V024 continuous '+s+' trouser drawing'])[-7:] for s in ['near','far']}}
col=bpy.data.collections.new('V036 | live contour joint probes');S.collection.children.link(col);report={'build':[]}
for side in ['near','far']:report['build'].append(L.build(bpy.data.objects['V024 continuous '+side+' trouser drawing'],rig,col,side))
maxbone=0.;maxprotected=0.;maxcuff=0.;rows=[]
def dist(p,a,b):
 dx=b.x-a.x;dz=b.z-a.z;return abs(dx*(p.z-a.z)-dz*(p.x-a.x))/(dx*dx+dz*dz)**.5
for i in range(249):
 f=1+i/8;frame(f);r=cache[f];row={'frame':f,'legs':{}}
 for b in rig.pose.bones:
  W=rig.matrix_world@b.matrix;maxbone=max(maxbone,max(abs(W[a][c]-r['bones'][b.name][a][c]) for a in range(4) for c in range(4)))
 for n,V in r['protected'].items():maxprotected=max(maxprotected,max((a-b).length for a,b in zip(pts(bpy.data.objects[n],fore if n in fgn else None),V)))
 for side in ['near','far']:
  o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];V=pts(o);C=[(V[j*7]+V[j*7+6])*.5 for j in range(97)];maxcuff=max(maxcuff,max((a-b).length for a,b in zip(V[-7:],r['cuffs'][side])));H=rig.matrix_world@rig.pose.bones['thigh_'+side].head;K=rig.matrix_world@rig.pose.bones['shin_'+side].head;A=rig.matrix_world@rig.pose.bones['shin_'+side].tail;row['legs'][side]={'thigh_axis_max_center_deviation_m':max(dist(C[j],H,K) for j in range(18,47)),'shin_axis_max_center_deviation_m':max(dist(C[j],K,A) for j in range(65,75)),'thigh_length_m':(K-H).length,'shin_length_m':(A-K).length}
 rows.append(row)
changed=[n for n,sha in actions.items() if h(bpy.data.actions[n])!=sha];report.update({'scope':'Native preservation and live-axis tests, not artistic acceptance','blender_version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'samples':rows,'max_original_bone_world_matrix_change':maxbone,'max_head_shoe_hand_mesh_change_m':maxprotected,'max_cuff_ring_change_m':maxcuff,'original_actions_changed':changed,'max_thigh_center_axis_deviation_m':max(r['legs'][s]['thigh_axis_max_center_deviation_m'] for r in rows for s in ['near','far']),'max_shin_center_axis_deviation_m':max(r['legs'][s]['shin_axis_max_center_deviation_m'] for r in rows for s in ['near','far'])})
(P/'evidence/LIVE_CONTOUR_BUILD_AND_CHECK.json').write_text(json.dumps(report,indent=2));assert not changed and max(maxbone,maxprotected,maxcuff)<.00002;assert max(report['max_thigh_center_axis_deviation_m'],report['max_shin_center_axis_deviation_m'])<.00005,report
S['V036_status']='Isolated motion-continuity candidate. Live rigid thigh/shin drawing axes; localized slimmer knees; preferred timing, body/hand/feet actions and original paint retained. Artistic review open.';frame(11);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Live_Limb_Continuity_v036.blend'),compress=True);print('V036_LIVE_CONTOURS_BUILT',json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
