"""V028 preferred movement retained. One original painted shoe asset, two rigid instances.
Only far-shoe placement and lower trouser/cuff art adapt to its consistent hull.
"""
import bpy,math,json,sys,csv,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
SOURCE=P/'reference/PREFERRED_MOVEMENT_v028.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs,C=api.initialize_from_scene();rig=rigs['BOY'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());PER=31.;STRIDE=.9524437384576381;SCALE={'near':1.,'far':.97}
JOIN=json.loads((P/'evidence/ORIGINAL_CUFF_TO_SHOE_RELATION.json').read_text())['1'];JN=Vector(JOIN['near']['relative_to_flat_shoe_ankle']);JF=Vector(JOIN['far']['relative_to_flat_shoe_ankle']);JN.y=JF.y=0
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def sample(q):
    frame(q+1);row={'q':q,'D':T.matrix_world.translation.x,'feet':{}}
    for s in ['near','far']:
        ob=bpy.data.objects[B[s]['object']];e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());V=[e.matrix_world@v.co for v in e.data.vertices];F=rig.matrix_world@rig.pose.bones['foot_'+s].matrix;R=F.to_3x3()@Matrix(B[s]['flat_bone']).to_3x3().inverted();a=math.atan2(R[0][2],R[0][0]);row['feet'][s]={'A':list(F.translation),'a':a,'clear':min(v.z for v in V),'depth':sum(v.y for v in V)/len(V)}
    return row
frame(1);source=bpy.data.objects[B['near']['object']];e=source.evaluated_get(bpy.context.evaluated_depsgraph_get());tmp=e.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh=tmp.copy();W=e.matrix_world.copy();source.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear();first=sample(0);a=first['feet']['near']['a'];A=Vector(first['feet']['near']['A']);inv=Matrix.Rotation(-a,4,'Y');canonical=[inv@(W@v.co-A) for v in mesh.vertices];mesh.vertices.foreach_set('co',[x for v in canonical for x in v]);mesh.update();mesh.name='V033 | one canonical original painted shoe | shared geometry UVs soles'
# Cache the preferred native feet. No body controls, actions or timing are rewritten.
cache={round(i/16,6):sample(i/16) for i in range(497)}
V={s:[Vector((v.x*SCALE[s],v.y*SCALE[s],v.z*SCALE[s])) for v in canonical] for s in SCALE}
oldfar=json.loads((P/'evidence/ACTUAL_V028_FOOTWEAR_AUDIT.json').read_text())['frames']['1']['far']['normalized_vertices'];oldfar=[Vector(v) for v in oldfar]
def rotate(v,a):c=math.cos(a);ss=math.sin(a);return Vector((c*v.x+ss*v.z,v.y,-ss*v.x+c*v.z))
def active(vs,a):return min(range(len(vs)),key=lambda j:rotate(vs[j],a).z)
def compile_roll(vs,sign):
    j=active(vs,sign*1e-7);anc=Vector((vs[j].x,0,0));out=[(0.,j,anc.copy())];last=j
    for i in range(1,5001):
        a=sign*math.radians(85)*i/5000;j=active(vs,a)
        if j==last:continue
        dv=vs[j]-vs[last];edge=math.atan2(dv.z,dv.x)
        while edge>math.pi/2:edge-=math.pi
        while edge<-math.pi/2:edge+=math.pi
        anc.x+=rotate(dv,edge).x;out.append((edge,j,anc.copy()));last=j
    return out
ROLL={(s,sgn):compile_roll(vs,sgn) for s,vs in [('far',V['far']),('oldfar',oldfar)] for sgn in [-1,1]}
def rolling(tag,vs,a,flat):
    seq=ROLL[tag,1 if a>=0 else -1];_,j,anc=seq[0]
    for edge,k,b in seq[1:]:
        if abs(a)+1e-9>=abs(edge):j,anc=k,b
        else:break
    r=rotate(vs[j],a);return Vector((flat+anc.x-r.x,0,-r.z)),j,flat+anc.x
contact=cache[16.]['feet']['far'];rel,_,_=rolling('oldfar',oldfar,contact['a'],0);flat0=contact['A'][0]-rel.x
def old(q):return cache[round(q,6)] if round(q,6) in cache else sample(q)
def far_stance(q):
    n=math.floor((q-16)/PER);f=old(q)['feet']['far'];return rolling('far',V['far'],f['a'],flat0+n*STRIDE)
# This cycle's far swing is q4.25..16. Preserve sole clearance and timing;
# blend horizontal placement correction with endpoint-matched velocity.
q0=4.25;q1=16.;eps=1/64
def dx_at(q):return far_stance(q)[0].x-old(q)['feet']['far']['A'][0]
d0=dx_at(q0);d1=dx_at(q1);v0=(d0-dx_at(q0-eps))/eps;v1=(dx_at(q1+eps)-d1)/eps
def hermite(u):return (2*u**3-3*u*u+1)*d0+(u**3-2*u*u+u)*(q1-q0)*v0+(-2*u**3+3*u*u)*d1+(u**3-u*u)*(q1-q0)*v1
def new_foot(row,s):
    q=row['q'];f=row['feet'][s];a=f['a'];t=(q-(0 if s=='near' else 16))%PER;toe=18.5 if s=='near' else 19.25;mode='CONTACT' if t<=toe+1e-9 else 'SWING'
    if s=='near':return Vector(f['A']),a,mode,{},Vector((0,0,0))
    if mode=='CONTACT':nA,j,anchor=far_stance(q);meta={'vertex':j,'anchor_x':anchor}
    else:
        u=(q-q0)/(q1-q0);nA=Vector((f['A'][0]+hermite(u),0,max(0,f['clear'])-min(rotate(v,a).z for v in V[s])));meta={}
    return nA,a,mode,meta,nA-Vector(f['A'])
pack=bpy.data.collections.new('V033 | consistent original shoe pair');S.collection.children.link(pack);fore.layer_collection.children[pack.name].exclude=True
parts={}
for s in ['near','far']:
    bpy.data.objects[B[s]['object']].hide_render=True
    for view in S.view_layers:
        try:bpy.data.objects[B[s]['object']].hide_set(True,view_layer=view)
        except RuntimeError:pass
    ob=bpy.data.objects.new('V033 | '+s+' | canonical painted shoe',mesh);pack.objects.link(ob);ob.parent=T;ob.matrix_parent_inverse=Matrix.Identity(4);ob.rotation_mode='XYZ';ob.scale=(SCALE[s],)*3;parts[s]=ob
    ob['design']='Shared mesh, UVs, painted material and sole design from the retained original near shoe. Far uniform97% perspective scale; no different shoe drawing.'
rows=[];deltas={}
for i in range(497):
    q=i/16;row=cache[q];f=q+1
    for s in ['near','far']:
        nA,a,mode,meta,delta=new_foot(row,s);ob=parts[s];ob.location=(nA.x-row['D'],row['feet'][s]['depth']-sum(v.y for v in V[s])/len(V[s]),nA.z);ob.rotation_euler=(0,a,0);ob.keyframe_insert('location',frame=f);ob.keyframe_insert('rotation_euler',frame=f)
        cuff_delta=delta+rotate(JN*SCALE['far']-JF,a) if s=='far' else Vector()
        if s=='far' and q==int(q):deltas[int(q)]=cuff_delta.copy()
        if i%4==0:
            vv=[nA+rotate(v,a) for v in V[s]];rows.append({'frame':f,'side':s,'root_x_m':row['D'],'pitch_degrees':math.degrees(a),'support':mode,'old_ankle_x_m':row['feet'][s]['A'][0],'old_ankle_z_m':row['feet'][s]['A'][2],'new_art_anchor_x_m':nA.x,'new_art_anchor_z_m':nA.z,'sole_min_z_m':min(v.z for v in vv),'source_sole_min_z_m':row['feet'][s]['clear'],'contact_vertex':meta.get('vertex',''),'contact_world_x_m':meta.get('anchor_x',''),'art_anchor_dx_m':delta.x,'art_anchor_dz_m':delta.z,'cuff_fit_dx_m':cuff_delta.x,'cuff_fit_dz_m':cuff_delta.z})
# A local drawing refit of the lower far trouser/cuff, leaving gait bones and
# all upper body, near leg, UVs, and original action timing exactly untouched.
pants=bpy.data.objects['V024 continuous far trouser drawing'];assert len(pants.data.vertices)==97*7;keys=pants.data.shape_keys.key_blocks;assert len(keys)==31;maxshift=0.
for q,kb in enumerate(keys):
    delta=deltas[q];arr=[]
    for j,v in enumerate(kb.data):
        t=(j//7)/96;w=max(0,min(1,(t-.72)/.28));w=w*w*(3-2*w);co=v.co+Vector((delta.x,0,delta.z))*w;maxshift=max(maxshift,(co-v.co).length);arr.extend(co)
    kb.data.foreach_set('co',arr)
    if q==0:pants.data.vertices.foreach_set('co',arr)
pants.data.update();pants['V033_scope']='Only lower28% of original far trouser/cuff drawing follows changed shoe art anchor; smooth zero displacement at72%. Original gait controls, UVs, upper leg and31-frame clock retained.'
def curves(ob):
    if ob.animation_data and ob.animation_data.action:
        for l in ob.animation_data.action.layers:
            for st in l.strips:
                for bag in st.channelbags:yield from bag.fcurves
for ob in parts.values():
    for fc in curves(ob):
        for k in fc.keyframe_points:k.interpolation='LINEAR'
        mod=fc.modifiers.new('CYCLES');mod.mode_before=mod.mode_after='REPEAT'
with (P/'evidence/SHOE_TRAVEL_AND_CONTACT_QUARTER_FRAME.csv').open('w',newline='') as out:w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report={'scope':'V028 preferred movement retained; footwear design correction, not a new preferred animation or artistic approval.','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'Blender':bpy.app.version_string,'canonical_source_object':B['near']['object'],'one_shared_mesh':parts['near'].data==parts['far'].data,'near_scale':1.,'far_uniform_perspective_scale':.97,'canonical_vertices':len(mesh.vertices),'canonical_dimensions_xz_m':[max(v.x for v in canonical)-min(v.x for v in canonical),max(v.z for v in canonical)-min(v.z for v in canonical)],'preserved':'All V028 rig/control/upper-body/head/coat actions, near trouser data and original31frame cadence/root travel. No V031/V032 movements imported.','changed':'Two consistent shoe instances; far-art rocker/swing placement and lower far cuff drawing fit the shared design. Gait bones and old ankle targets remain untouched.','period_frames':31,'fps':30,'stride_m':STRIDE,'far_flat_ankle_contact_origin_m':flat0,'maximum_lower_cuff_vertex_refit_m':maxshift,'maximum_far_art_anchor_shift_m':max(math.hypot(r['art_anchor_dx_m'],r['art_anchor_dz_m']) for r in rows if r['side']=='far'),'maximum_contact_sole_error_m':max(abs(r['sole_min_z_m']) for r in rows if r['support']=='CONTACT'),'head_choice':'Exact preferred V028 original profile action preserved; no new head-card rotation or design.','artistic_acceptance':False}
assert report['one_shared_mesh'] and report['maximum_contact_sole_error_m']<.0001
(P/'evidence/CONSISTENT_FOOTWEAR_BUILD.json').write_text(json.dumps(report,indent=2));S['V033_status']='Preferred V028 movement restored. Consistent painted shoe design correction only. User review pending; no artistic approval.';S['V033_baseline']='V028 movement is preferred by direct user feedback; V031 movement was rejected. V030 anatomy retained as reference, no wholesale construction redraw imported.'
S.frame_start=1;S.frame_end=279;S.render.fps=30;frame(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Preferred_Walk_Consistent_Shoes_v033.blend'),compress=True);print('V033_NATIVE_BUILT',json.dumps(report),flush=True)
