"""v029 whole-pose drawings. Four chosen frames only; no generated cycle.
Existing head/collar/boot pigments retained. New anatomical body/limb contours.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import pose_design as D
SOURCE=P/'reference/PRESERVED_BASELINE_v028.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;boots=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());anatomy=D.analyze(boots);frames=[p['frame'] for p in D.POSES]
fg=bpy.data.collections['V025 | retained foreground identity'];stage=bpy.data.collections['V020 | study stage and sole controls'];fore=S.view_layers['V025 | original foreground']
def frame(f):S.frame_set(f);bpy.context.view_layer.update();fore.update()
def evaluated_copy(o,view):
    view.update();e=o.evaluated_get(view.depsgraph);tmp=e.to_mesh(preserve_all_data_layers=True,depsgraph=view.depsgraph);m=tmp.copy();e.to_mesh_clear();return m,e.matrix_world.copy()
headsource=bpy.data.objects['PERF_BOY | original head'];collarsource=bpy.data.objects['LOCO_BOY | PAINT body'];headcoords=[];collarcoords=[];headmesh=None;collarmesh=None
for p in D.POSES:
    frame(p['frame']);oldneck=rig.matrix_world@rig.pose.bones['chest'].tail;newneck=Vector((p['neck'][0],0,p['neck'][1]))
    for source,cache,tag in [(headsource,headcoords,'head'),(collarsource,collarcoords,'collar')]:
        m,W=evaluated_copy(source,fore);V=[W@v.co-oldneck+newneck for v in m.vertices];cache.append(V)
        if tag=='head' and headmesh is None:headmesh=m
        elif tag=='collar' and collarmesh is None:collarmesh=m
        else:bpy.data.meshes.remove(m)
frame(1);bootmeshes={}
for side in ['near','far']:bootmeshes[side]=evaluated_copy(bpy.data.objects[boots[side]['object']],bpy.context.view_layer)[0]
# Freeze the study stage. Original controls/rig remain as hidden reference only.
if T.animation_data:T.animation_data.action=None
T.location=(0,0,0)
for o in list(S.objects):
    if o.type in ['MESH','GREASEPENCIL','CURVE'] and o.name!='V024 floor ticks':o.hide_render=True
pack=bpy.data.collections.new('V029 | FOUR whole-body silhouette drawings');S.collection.children.link(pack)
fore.layer_collection.children[pack.name].exclude=True
def curves(id):
    if id.animation_data and id.animation_data.action:
        for l in id.animation_data.action.layers:
            for st in l.strips:
                for bag in st.channelbags:yield from bag.fcurves
def posemesh(name,mesh,coords,collection):
    assert len({len(v) for v in coords})==1
    mesh.vertices.foreach_set('co',[x for v in coords[0] for x in v]);ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);ob.shape_key_add(name='Basis CONTACT')
    for i in range(1,4):
        k=ob.shape_key_add(name=D.POSES[i]['name']);k.data.foreach_set('co',[x for v in coords[i] for x in v])
        for f in frames:k.value=float(f==frames[i]);k.keyframe_insert('value',frame=f)
    for fc in curves(mesh.shape_keys):
        for k in fc.keyframe_points:k.interpolation='CONSTANT'
    ob['V029_scope']='Four independent chosen poses only. No inbetweens or timing approval.';return ob
head=posemesh('V029 | retained painted head | four source profiles',headmesh,headcoords,fg);head['design']='Original v028 painted head/profile coordinates preserved relative to neck; translated to new pose. No turnaround, edge-on card or v008 reuse.'
collar=posemesh('V029 | retained painted collar',collarmesh,collarcoords,fg)
for side in ['near','far']:
    V=[]
    for p,r in zip(D.POSES,anatomy):V.append([Vector((x,-.024 if side=='near' else .015,z)) for x,z in r['legs'][side]['boot_vertices']])
    assert len(V[0])==len(bootmeshes[side].vertices)
    ob=posemesh('V029 | refitted original painted '+side+' boot',bootmeshes[side],V,pack);ob['fit']='Original painted boot/UVs retained;X*.78,Z*.90 about ankle, then sole-fitted to the authored pose. No old leg trajectories reused.'
gp=bpy.data.grease_pencils.new('V029 | reauthored body silhouettes');ob=bpy.data.objects.new('V029 | contact down passing up | editable GP',gp);pack.objects.link(ob);gp.stroke_depth_order='3D';layer=gp.layers.new('01 | whole-body anatomy and gesture',set_active=True);layer.use_lights=False
def mat(name,color,fill=True,stroke=False):
    m=bpy.data.materials.new('V029 | '+name);bpy.data.materials.create_gpencil_data(m);g=m.grease_pencil;g.show_fill=fill;g.show_stroke=stroke;g.fill_color=color;g.color=color;gp.materials.append(m);return len(gp.materials)-1
COAT=mat('charcoal coat',(.014,.015,.014,1));WASH=mat('coat volume wash',(.032,.034,.031,.65));SHADOW=mat('fold ink',(.004,.005,.005,.72));NEAR=mat('near trouser charcoal',(.019,.021,.019,1));FAR=mat('far trouser wash',(.036,.039,.035,1));LEGPLANE=mat('trouser plane',(.027,.029,.026,.55));CUFF=mat('restrained gray cuff',(.057,.060,.054,1));SKIN=mat('charcoal skin',(.012,.014,.012,1));FARSKIN=mat('far charcoal skin',(.028,.031,.027,1));INK=mat('drawn seam',(.006,.008,.006,.75),False,True)
def v(xz,y=0):return Vector((xz[0],y,xz[1]))
def unit(a,b):return (b-a).normalized()
def normal(u):return Vector((-u.z,0,u.x))
def catmull(V,steps=3,closed=True):
    n=len(V);out=[]
    for i in range(n if closed else n-1):
        a=V[(i-1)%n] if closed or i else V[0];b=V[i];c=V[(i+1)%n];d=V[(i+2)%n] if closed or i+2<n else V[-1]
        for j in range(steps):
            t=j/steps;out.append((b*2+(-a+c)*t+(a*2-b*5+c*4-d)*t*t+(-a+b*3-c*3+d)*t*t*t)*.5)
    if not closed:out.append(V[-1])
    return out
def draw(d,points,mi,y,closed=True,steps=3,radius=.0008):
    V=[v(p,y) if not isinstance(p,Vector) else Vector((p.x,y,p.z)) for p in points];V=catmull(V,steps,closed);d.add_strokes([len(V)]);s=d.strokes[-1];s.cyclic=closed;s.material_index=mi;s.fill_id=len(d.strokes) if closed else 0;s.fill_opacity=1.;s.fill_color=(0,0,0,0);s.softness=.25
    for point,co in zip(s.points,V):point.position=co;point.radius=radius;point.opacity=1
def leg(d,p,r,side):
    L=r['legs'][side];H=v(L['hip']);K=v(L['knee']);A=v(L['ankle']);u=unit(H,K);w=unit(K,A);Nu=normal(u);Nv=normal(w);Nm=(Nu+Nv).normalized();width=1 if side=='near' else .92;y=-.018 if side=='near' else .012
    # Separate thigh mass, front patella, calf and tapered shin. No shared S-curve ribbon.
    V=[H+Nu*.052*width,H.lerp(K,.52)+Nu*.048*width,K-u*.030+Nu*.034*width,K+Nm*.035*width,K+w*.040+Nv*.033*width,K.lerp(A,.64)+Nv*.029*width,A-w*.004+Nv*.024*width,A-w*.004-Nv*.024*width,K.lerp(A,.53)-Nv*.030*width,K+w*.070-Nv*.035*width,K-Nm*.027*width,H.lerp(K,.70)-Nu*.039*width,H-Nu*.052*width]
    draw(d,V,NEAR if side=='near' else FAR,y,steps=4)
    draw(d,[H+Nu*.013,H.lerp(K,.60)+Nu*.020,K-u*.029+Nu*.012,K-u*.008-Nm*.004,H.lerp(K,.45)-Nu*.015],LEGPLANE,y-.0005)
    draw(d,[K+w*.052+Nv*.008,K.lerp(A,.75)+Nv*.012,A-w*.021-Nv*.006,K+w*.065-Nv*.009],LEGPLANE,y-.0007)
    # Narrow integrated cuff, not a large rectangular gray boot-collar block.
    C=A-w*.013;draw(d,[C-w*.018+Nv*.028*width,C-w*.018-Nv*.028*width,C+w*.007-Nv*.027*width,C+w*.007+Nv*.027*width],CUFF,y-.001,steps=3)
    draw(d,[K-Nm*.018-u*.008,K-Nm*.011+w*.014,K+w*.026-Nv*.020],INK,y-.0015,closed=False,steps=2,radius=.0011)
def arm(d,p,side):
    N=v(p['neck']);S0=N+Vector((-.018 if side=='near' else .035,0,-.078));aa,bb,hh=[math.radians(a) for a in p[side+'_arm']];u=Vector((math.sin(aa),0,-math.cos(aa)));w=Vector((math.sin(bb),0,-math.cos(bb)));h=Vector((math.sin(hh),0,-math.cos(hh)));E=S0+u*.198;W=E+w*.178;C=E.lerp(W,.30);Nu=normal(u);Nw=normal(w);Nh=normal(h);y=-.045 if side=='near' else .026
    draw(d,[C+Nw*.016,W+Nw*.011,W-Nw*.011,C-Nw*.016],SKIN if side=='near' else FARSKIN,y-.001)
    draw(d,[S0+Nu*.034,S0.lerp(E,.60)+Nu*.032,E+Nu*.028,C+Nw*.023,C-Nw*.023,E-Nu*.026,S0.lerp(E,.4)-Nu*.032,S0-Nu*.034],COAT,y,steps=3)
    draw(d,[C-w*.014+Nw*.024,C-w*.014-Nw*.024,C+w*.004-Nw*.023,C+w*.004+Nw*.023],CUFF,y-.002,steps=2)
    hand=[W-Nh*.011,W+h*.024-Nh*.017,W+h*.050-Nh*.015,W+h*.062-Nh*.007,W+h*.060+Nh*.001,W+h*.053+Nh*.004,W+h*.058+Nh*.009,W+h*.051+Nh*.014,W+h*.032+Nh*.014,W+h*.025+Nh*.025,W+h*.014+Nh*.024,W+h*.020+Nh*.009,W+Nh*.011]
    draw(d,hand,SKIN if side=='near' else FARSKIN,y-.003,steps=2)
    draw(d,[S0+Nu*.014,E+Nu*.010,C+Nw*.009,C-Nw*.006,E-Nu*.011,S0-Nu*.008],WASH,y-.0007)
def torso(d,p):
    H=v(p['hip']);N=v(p['neck']);W=v(p['waist']);R=v(p['rib']);F=v(p['hem_front']);B=v(p['hem_back'])
    draw(d,[H+Vector((-.068,0,.066)),H+Vector((.066,0,.066)),H+Vector((.073,0,-.020)),H+Vector((.022,0,-.058)),H+Vector((-.062,0,-.026))],NEAR,-.010)
    contour=[N+Vector((-.035,0,.010)),N+Vector((.031,0,.012)),N+Vector((.072,0,-.059)),R+Vector((.083,0,.065)),R+Vector((.079,0,-.055)),W+Vector((.060,0,.004)),F,H+Vector((.022,0,-.004)),B,W+Vector((-.064,0,-.021)),R+Vector((-.076,0,-.048)),N+Vector((-.083,0,-.068))]
    draw(d,contour,COAT,-.026,steps=4)
    draw(d,[N+Vector((-.055,0,-.075)),R+Vector((-.035,0,.055)),W+Vector((-.033,0,.009)),H+Vector((-.031,0,.023)),B,W+Vector((-.059,0,-.015)),R+Vector((-.065,0,-.047))],SHADOW,-.027)
    draw(d,[N+Vector((.040,0,-.075)),R+Vector((.060,0,.055)),R+Vector((.052,0,-.049)),W+Vector((.033,0,-.002)),F+Vector((-.018,0,.012)),H+Vector((.028,0,.059)),W+Vector((.010,0,.018)),R+Vector((.026,0,.015))],WASH,-.028)
    # Waist fold follows each whole-pose bend, rather than ornamenting a fixed panel.
    draw(d,[W+Vector((-.050,0,.013)),W+Vector((-.009,0,-.012)),W+Vector((.044,0,-.003)),W+Vector((.012,0,.002)),W+Vector((-.025,0,.022))],SHADOW,-.029,steps=2)
    draw(d,[N+Vector((.027,0,-.082)),R+Vector((.034,0,.039)),W+Vector((.024,0,.015)),F+Vector((-.027,0,.009))],INK,-.030,closed=False,steps=3,radius=.0012)
for p,r in zip(D.POSES,anatomy):
    d=layer.frames.new(p['frame']).drawing;arm(d,p,'far');leg(d,p,r,'far');leg(d,p,r,'near');torso(d,p);arm(d,p,'near');d.tag_positions_changed()
ob['V029_scope']='Four reauthored contact/down/passing/up whole-body silhouettes only; no cycle, timing or production integration. Shared anatomical lengths; defined knee/calf/shin volumes; deliberate arm gestures.'
# Keep only the four drawings in the study timeline; no interpolated inbetweens.
S.frame_start=1;S.frame_end=13;S.render.fps=30;S['V029_status']='FOUR POSES ONLY. Native rendered silhouette comparison awaiting artistic review. Not a cycle or animation pass.';S['V029_travel']='No integration curve authored. Stage/root frozen for pose comparisons. Do not infer travel/timing from study frame numbers.'
report={'scope':'Anatomy/support safeguards, not visual acceptance','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'version':bpy.app.version_string,'selected_frames':frames,'new_drawings':4,'shared_thigh_length_m':D.THIGH,'shared_shin_length_m':D.SHIN,'boot_refit':[D.BOOT_SCALE_X,D.BOOT_SCALE_Z],'new_arm_lengths_m':[.198,.178],'head_design':'Four existing painted source profiles retained as translated native mesh shape samples; head/hair UV/materials unchanged. No turnaround.','head_vertices':len(headmesh.vertices),'collar_vertices':len(collarmesh.vertices),'poses':[{**r,'legs':{s:{k:v for k,v in data.items() if k!='boot_vertices'} for s,data in r['legs'].items()}} for r in anatomy],'no_cycle_or_production_integration':True}
(P/'evidence/FOUR_POSE_ANATOMY_AND_SCOPE.json').write_text(json.dumps(report,indent=2));frame(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Four_Pose_Silhouette_Rebuild_v029.blend'),compress=True);print('V029_FOUR_POSES_BUILT',json.dumps({k:v for k,v in report.items() if k!='poses'}),flush=True)
