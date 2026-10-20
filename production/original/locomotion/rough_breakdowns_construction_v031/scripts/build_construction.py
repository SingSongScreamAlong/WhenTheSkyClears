"""Isolated V031 native rough construction; packed painting and V030 silhouette family."""
import bpy,sys,json,math,csv,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
import construction_motion as M
import draw_construction as D
SOURCE=P/'reference/PRESERVED_BASELINE_v028.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent
fg=bpy.data.collections['V025 | retained foreground identity'];fore=S.view_layers['V025 | original foreground'];deps=bpy.data.collections['V025 | evaluation dependencies']
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();fore.update()
def evaluated_copy(o,view):
    view.update();e=o.evaluated_get(view.depsgraph);tmp=e.to_mesh(preserve_all_data_layers=True,depsgraph=view.depsgraph);m=tmp.copy();e.to_mesh_clear();return m,e.matrix_world.copy()
frame(1);oldneck=rig.matrix_world@rig.pose.bones['chest'].tail;templates={}
for tag,name in [('head','PERF_BOY | original head'),('collar','LOCO_BOY | PAINT body')]:
    mesh,W=evaluated_copy(bpy.data.objects[name],fore);coords=[W@v.co-oldneck for v in mesh.vertices];mesh.vertices.foreach_set('co',[x for v in coords for x in v]);templates[tag]=mesh
bootmeshes={s:evaluated_copy(bpy.data.objects[M.B[s]['object']],bpy.context.view_layer)[0] for s in ['near','far']}
if T.animation_data:T.animation_data_clear()
T.location=(0,0,0);frame(1)
camera_world={name:bpy.data.objects[name].matrix_world.copy() for name in ['V024 | CLOSE portrait','V020 | CHILD | SHOT']}
for o in list(S.objects):
    if o.type in ['MESH','GREASEPENCIL','CURVE'] and o.name!='V024 floor ticks':o.hide_render=True
pack=bpy.data.collections.new('V031 | ROUGH construction body');S.collection.children.link(pack);fore.layer_collection.children[pack.name].exclude=True
root=bpy.data.objects.new('V031 | CONSTRUCTION TRAVEL',None);deps.objects.link(root);root.empty_display_type='ARROWS';root['contract']='+X metres; D=.8146774020162355*(F-1)/32; 30fps. Import body/boots/head/collar and travel together.'
for f in [1,33]:root.location.x=M.root(f-1);root.keyframe_insert('location',index=0,frame=f)
def parent(ob):ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4)
parts={}
for tag,mesh in templates.items():
    ob=bpy.data.objects.new('V031 | retained painted '+tag,mesh);fg.objects.link(ob);parent(ob);parts[tag]=ob
    ob['choice']='Single original F1 painted profile translated with neck. No profile morph, head-card rotation, hair redraw or rejected v008 reuse.'
for s,mesh in bootmeshes.items():
    assert len(mesh.vertices)==len(M.V[s]);mesh.vertices.foreach_set('co',[x for v in M.V[s] for x in (v[0],0,v[1])]);mesh.update()
    ob=bpy.data.objects.new('V031 | original painted '+s+' boot',mesh);pack.objects.link(ob);parent(ob);ob.rotation_mode='XYZ';parts[s]=ob
for name,W in camera_world.items():
    cam=bpy.data.objects[name]
    if cam.animation_data:cam.animation_data_clear()
    for c in list(cam.constraints):cam.constraints.remove(c)
    parent(cam);cam.matrix_basis=W
gp=bpy.data.grease_pencils.new('V031 | 32 rough body drawings');ob=bpy.data.objects.new('V031 | editable rough construction GP',gp);pack.objects.link(ob);parent(ob);gp.stroke_depth_order='3D';D.initialize(gp)
layer=gp.layers.new('01 | construction on ones | 32-frame period',set_active=True);layer.use_lights=False
for f in range(1,33):
    p,r,m=M.evaluate(f-1);assert min(m.values())>0
    drawing=layer.frames.new(f).drawing
    D.arm(drawing,p,'far');D.leg(drawing,p,r,'far');D.leg(drawing,p,r,'near');D.torso(drawing,p);D.arm(drawing,p,'near');drawing.tag_positions_changed()
for f in range(33,98):layer.frames.copy(1+(f-1)%32,f,instance_drawing=True)
floor_data=bpy.data.grease_pencils.new('V031 | static world contact ruler');floor_ob=bpy.data.objects.new('V031 | static ground ruler | review only',floor_data);pack.objects.link(floor_ob);floor_data.stroke_depth_order='3D';D.initialize(floor_data)
floor_layer=floor_data.layers.new('world stationary contact reference',set_active=True);floor_layer.use_lights=False;fd=floor_layer.frames.new(1).drawing;mi=D.mat('subtle ground guide',(.22,.23,.21,.28),False,True)
D.draw(fd,[[-2,0],[5,0]],mi,.1,closed=False,steps=1,radius=.0007)
for i in range(-20,51):D.draw(fd,[[i*.1,-.009],[i*.1,.006 if i%2 else .012]],mi,.1,closed=False,steps=1,radius=.00065)
fd.tag_positions_changed();floor_ob['review_only']='Static world ruler, never parented to travel. Remove for final painterly integration.'
rows=[]
for j in range(513):
    q=j/16;f=q+1;p,r,m=M.evaluate(q)
    for tag in ['head','collar']:
        parts[tag].location=(p['neck'][0],0,p['neck'][1]);parts[tag].keyframe_insert('location',frame=f)
    for s in ['near','far']:
        L=r['legs'][s];b=parts[s];b.location=(L['ankle'][0],-.024 if s=='near' else .015,L['ankle'][1]);b.rotation_euler=(0,L['angle'],0);b.keyframe_insert('location',frame=f);b.keyframe_insert('rotation_euler',frame=f)
        if j%4==0:rows.append({'frame':f,'phase_q':q,'side':s,'root_x_m':r['D'],'hip_local_x_m':L['hip'][0],'hip_z_m':L['hip'][1],'knee_local_x_m':L['knee'][0],'knee_z_m':L['knee'][1],'ankle_world_x_m':L['world_ankle'][0],'ankle_z_m':L['ankle'][1],'pitch_degrees':math.degrees(L['angle']),'support':L['mode'],'minimum_sole_z_m':L['sole_clearance'],'contact_vertex':L['contact'].get('vertex',''),'contact_world_x_m':L['contact'].get('anchor_x',''),'reach_margin_m':m[s]})
def curves(id):
    if id.animation_data and id.animation_data.action:
        for l in id.animation_data.action.layers:
            for st in l.strips:
                for bag in st.channelbags:yield from bag.fcurves
for object in [root,*parts.values()]:
    for fc in curves(object):
        for k in fc.keyframe_points:k.interpolation='LINEAR'
        mod=fc.modifiers.new('CYCLES');mod.mode_before='REPEAT_OFFSET' if object==root else 'REPEAT';mod.mode_after=mod.mode_before
ob['scope']='Rough on-ones construction only. Fuller V030 volumes, rounded chest contour, partial oblique waist seam. 32-frame two-step loop, native head/boot painting retained. Not finished ink/paint, not paired recovery or an approved walk.'
with (P/'evidence/TRAVEL_SOLE_AND_BODY_QUARTER_FRAME.csv').open('w',newline='') as out:
    w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
check={'scope':'Numerical construction safeguards, not visual acceptance','Blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'period_frames':32,'fps':30,'stride_m':M.STRIDE,'speed_m_per_sec':M.STRIDE*30/32,'root_curve':'LINEAR; X=stride*(F-1)/32 metres','selected_phase_frames':{'contact':1,'down':4,'passing':10,'up':13,'opposite_contact':17,'opposite_down':20,'opposite_passing':26,'opposite_up':29},'limb_lengths_m':{'thigh':M.THIGH,'shin':M.SHIN,'upper_arm':.198,'forearm':.178},'minimum_reach_margin_m':min(r['reach_margin_m'] for r in rows),'maximum_support_sole_height_error_m':max(abs(r['minimum_sole_z_m']) for r in rows if r['support']=='CONTACT'),'drawings':32,'native_review_frames':96,'head_choice':'Single original source F1 side profile, translated by neck; no profile change, card rotation, v008 reuse or hair redraw. Head design and UVs retained.','body_height_corrections':'Explicit authored vertical breakdowns in construction_motion.py, applied to body stack. No reach clamp, stretch or generic IK mass correction.','chest_and_waist':'Rounded outer shoulder/rib contours; down rib/waist settle, up opens. Short partial oblique seam replaces full-width belt crease.','source_scope':'Only isolated v031 files changed; no production timeline, pair animation, music/title changes.'}
assert check['minimum_reach_margin_m']>0 and check['maximum_support_sole_height_error_m']<1e-8
(P/'evidence/NATIVE_CONSTRUCTION_CHECK.json').write_text(json.dumps(check,indent=2))
S.frame_start=1;S.frame_end=96;S.render.fps=30;S.render.fps_base=1;S['V031_status']='CONSTRUCTION TEST. NOT APPROVED OR FINISHED CYCLE. 32 drawings repeated three times; normal speed30fps.';S['V031_integration']='New root and foot curves; old v026-v028 travel is incompatible. Match exact new root or use a world-cancelling stage; do not combine old world speed with these sole contacts.'
frame(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Rough_Construction_v031.blend'),compress=True)
print('V031_NATIVE_BUILT',json.dumps(check),flush=True)
