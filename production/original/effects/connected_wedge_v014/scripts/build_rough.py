"""One action-hierarchy rough: a rooted connected wedge tears into two parts."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1]
for d in ['native','previews','evidence']:(P/d).mkdir(parents=True,exist_ok=True)
s=bpy.data.scenes['FXv013 | drawn expansion and seated contacts'];bpy.context.window.scene=s
origin=bpy.data.objects['FXv013 | terrain anchor and controls'].location.copy()
camera_matrix=[list(v) for v in s.camera.matrix_world]
for col in list(s.collection.children):s.collection.children.unlink(col)
for o in list(s.collection.objects):
    if o!=s.camera:s.collection.objects.unlink(o)
s.name='FXv014 | connected wedge TWO TONE ROUGH';s.frame_start=1;s.frame_end=32;s.render.fps=24;s.render.fps_base=1;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
c=bpy.data.collections.new('FXv014 | CONNECTED SOIL WEDGE | rough only');s.collection.children.link(c)
r=bpy.data.objects.new('FXv014 | fixed impact anchor | ROUGH',None);c.objects.link(r);r.location=origin;r['start_frame']=7.;r['age']=0.
f=r.driver_add('["age"]');v=f.driver.variables.new();v.name='start';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["start_frame"]';f.driver.expression='frame-start'

def drive(owner,path,expr):
    fc=owner.driver_add(path);v=fc.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["age"]';fc.driver.expression=expr

def mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
dark=mat('FXv014 | FLAT dark soil',(.065,.043,.025));clay=mat('FXv014 | FLAT clay face',(.34,.21,.11))
names=['A','B','C','D','E','F','G','H','I','J','K','S1','S2']
raw=[
 [(-.06,0),(.06,0),(.08,.02),(.07,.04),(.03,.05),(0,.06),(-.015,.09),(-.05,.06),(-.065,.04),(-.045,.028),(-.05,.01),(.025,.03),(-.018,.045)],
 [(-.08,0),(.09,0),(.12,.06),(.16,.13),(.08,.21),(.025,.24),(-.07,.34),(-.18,.23),(-.19,.15),(-.11,.13),(-.10,.04),(.045,.12),(-.04,.18)],
 [(-.11,0),(.10,0),(.19,.12),(.25,.28),(.15,.39),(.04,.48),(-.11,.59),(-.29,.44),(-.29,.31),(-.19,.28),(-.17,.12),(.08,.25),(-.07,.35)],
 [(-.13,0),(.12,0),(.22,.16),(.32,.37),(.19,.50),(.075,.64),(-.16,.77),(-.34,.62),(-.35,.46),(-.23,.38),(-.22,.18),(.10,.34),(-.10,.47)],
 [(-.14,0),(.13,0),(.24,.19),(.36,.43),(.21,.58),(.09,.74),(-.17,.88),(-.38,.72),(-.39,.54),(-.26,.44),(-.25,.22),(.12,.40),(-.12,.54)],
 [(-.15,0),(.13,0),(.25,.21),(.38,.46),(.22,.63),(.10,.80),(-.18,.96),(-.40,.80),(-.42,.60),(-.27,.49),(-.27,.24),(.12,.44),(-.12,.59)],
 [(-.16,0),(.13,0),(.25,.22),(.39,.49),(.23,.67),(.09,.85),(-.19,1.005),(-.42,.85),(-.44,.64),(-.28,.53),(-.28,.27),(.12,.47),(-.13,.63)],
 [(-.16,0),(.13,0),(.25,.22),(.40,.49),(.23,.68),(.08,.865),(-.205,1.025),(-.43,.87),(-.45,.65),(-.29,.54),(-.28,.27),(.12,.47),(-.14,.64)]
]
poses=[dict(zip(names,p)) for p in raw];peak=poses[-1]
pieces={'body':['A','B','C','S1','S2','J','K'],'upper':['J','S2','F','G','H','I'],'shoulder':['S1','C','D','E','F','S2']}
collapse={8:{k:peak[k] for k in pieces['body']},9:dict(zip(pieces['body'],[(-.17,0),(.15,0),(.25,.20),(.12,.40),(-.12,.53),(-.27,.44),(-.28,.23)])),10:dict(zip(pieces['body'],[(-.18,0),(.18,0),(.27,.17),(.13,.31),(-.12,.41),(-.28,.32),(-.30,.18)])),12:dict(zip(pieces['body'],[(-.22,0),(.25,0),(.31,.10),(.15,.18),(-.11,.23),(-.31,.18),(-.33,.10)])),14:dict(zip(pieces['body'],[(-.27,0),(.31,0),(.35,.045),(.18,.07),(-.10,.09),(-.33,.07),(-.36,.04)])),16:dict(zip(pieces['body'],[(-.30,0),(.35,0),(.38,.02),(.20,.03),(-.09,.035),(-.35,.03),(-.39,.015)])),24:dict(zip(pieces['body'],[(-.30,0),(.35,0),(.38,.012),(.20,.015),(-.09,.018),(-.35,.015),(-.39,.008)]))}
def body_pose(age):
    if age<=7:return poses[age]
    keys=sorted(collapse)
    if age>=keys[-1]:return collapse[keys[-1]]
    a=max(k for k in keys if k<=age);b=min(k for k in keys if k>=age)
    if a==b:return collapse[a]
    u=(age-a)/(b-a);return {n:(collapse[a][n][0]*(1-u)+collapse[b][n][0]*u,collapse[a][n][1]*(1-u)+collapse[b][n][1]*u) for n in pieces['body']}

profile=json.loads((P.parent/'drawn_impact_v013/evidence/visible_terrain_profile.json').read_text())['profile']
q=world_to_camera_view(s,s.camera,origin);qx=world_to_camera_view(s,s.camera,origin+Vector((1,0,0)));qz=world_to_camera_view(s,s.camera,origin+Vector((0,0,1)));sx=q.x*1920;sy=(1-q.y)*1080;ppm=(qx.x-q.x)*1920;pz=(qz.y-q.y)*1080
def interp(x):
    if x<=profile[0][0]:return profile[0][1]
    if x>=profile[-1][0]:return profile[-1][1]
    j=next(i for i in range(len(profile)-1) if profile[i][0]<=x<profile[i+1][0]);a,b=profile[j],profile[j+1];return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
def ground(x):return (sy-interp(sx+ppm*x))/pz
facets={
 'body':[{'A':.35,'B':.65},{'B':.7,'C':.3},{'C':.25,'S1':.75},{'S1':1},{'S2':1},{'J':.7,'S2':.3},{'K':.65,'C':.35}],
 'upper':[{'S2':1},{'F':1},{'G':.82,'H':.18},{'H':.72,'S2':.28},{'J':.55,'S2':.45}],
 'shoulder':[{'S1':1},{'C':.7,'S1':.3},{'D':.75,'S1':.25},{'E':.8,'S2':.2},{'F':1},{'S2':1}]
}
flight={}
for piece,launch,vx,vz,spin in [('upper',7,-1.2,1.6,-1.3),('shoulder',8,1.0,1.1,1.65)]:
    pts=[peak[n] for n in pieces[piece]];cx=sum(p[0] for p in pts)/len(pts);cz=sum(p[1] for p in pts)/len(pts)
    def state(t):
        x=cx+vx*t/(1+.6*t);z=cz+vz*t-5*t*t;ang=spin*t;co=math.cos(ang);sn=math.sin(ang);bottom=z+min((p[1]-cz)*co-(p[0]-cx)*sn for p in pts);return x,z,ang,bottom-ground(x)
    a,b=0.,.01
    while state(b)[3]>0:b+=.01
    for _ in range(40):
        mid=(a+b)/2
        if state(mid)[3]>0:a=mid
        else:b=mid
    land=(a+b)/2;lx,lz,la,_=state(land)
    flight[piece]={'launch_age':launch,'center':[cx,cz],'vx':vx,'vz':vz,'spin':spin,'landing_seconds':land,'landing_age':launch+land*24,'landing_x':lx,'landing_angle':la}

def geometry(piece,age,weights):
    if age<=7:pd=poses[age]
    elif piece=='body':pd=body_pose(age)
    else:pd=peak
    pts=[(sum(pd[n][0]*v for n,v in w.items()),sum(pd[n][1]*v for n,v in w.items())) for w in weights]
    if piece=='body' or age<=flight[piece]['launch_age']:return pts
    f=flight[piece];cx,cz=f['center'];t=(age-f['launch_age'])/24
    if t<f['landing_seconds']:x=cx+f['vx']*t/(1+.6*t);z=cz+f['vz']*t-5*t*t;ang=f['spin']*t
    else:
        after=t-f['landing_seconds'];x=f['landing_x']+f['vx']*.018*(1-math.exp(-16*after));ang=f['landing_angle']*.45+f['landing_angle']*.55*math.exp(-18*after);co=math.cos(ang);sn=math.sin(ang);support=-min((peak[n][1]-cz)*co-(peak[n][0]-cx)*sn for n in pieces[piece]);z=ground(x)+support
    co=math.cos(ang);sn=math.sin(ang);return [(x+(px-cx)*co+(pz-cz)*sn,z-(px-cx)*sn+(pz-cz)*co) for px,pz in pts]

for piece,label in [('body','01 Rooted connected wedge'),('upper','02 Upper wedge fragment'),('shoulder','03 Shoulder fragment')]:
    for face in [False,True]:
        weights=facets[piece] if face else [{n:1} for n in pieces[piece]];pts=geometry(piece,0,weights);y=-.012 if face else 0
        mesh=bpy.data.meshes.new('FXv014 '+label+(' face' if face else ' body'));mesh.from_pydata([(x,y,z) for x,z in pts],[],[tuple(range(len(pts)))]);mesh.materials.append(clay if face else dark);mesh.update();o=bpy.data.objects.new('FXv014 | '+label+(' | clay face' if face else ' | dark silhouette'),mesh);c.objects.link(o);o.parent=r
        for age in range(32):
            k=o.shape_key_add(name=f'AGE_{age:02d}');k.interpolation='KEY_LINEAR'
            for v,(x,z) in zip(k.data,geometry(piece,age,weights)):v.co=(x,y,z)
        mesh.shape_keys.use_relative=False;drive(mesh.shape_keys,'eval_time','10*max(0,min(31,t))');drive(o,'hide_render','t<0');drive(o,'hide_viewport','t<0')
for node in s.compositing_node_group.nodes:
    if node.type=='R_LAYERS':node.scene=s;node.layer='RUPTURE'
r['construction']='Rough only. One connected asymmetric wedge through age 7. Upper and shoulder are contiguous parts before separation, then two rigid fragments. Solid two-tone; no smoke, opacity animation, pigment or contact puffs.'
s.frame_set(13);r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();native=P/'native/WTSC_Connected_Soil_Wedge_ROUGH_v014.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'blender':bpy.app.version_string,'source':'v013 held proof read-only','camera_matrix':camera_matrix,'root':list(origin),'pixels_per_metre':ppm,'fps':24,'frames':[1,32],'impact_frame':7,'connected_ages':[0,7],'connected_scene_frames':[7,14],'expanding_heights_metres':[max(z for x,z in p.values()) for p in poses],'visible_fragments_after_breakup':2,'flight':flight,'pieces':pieces,'peak_nodes':peak,'rough_materials':2,'smoke':False,'opacity_animation':False,'pigment':False,'incidental_contact_puffs':False,'criterion':'Read one compact rooted ejection and its causal breakup before incidental detail. Native correctness is not artistic acceptance.','native_sha256':hashlib.sha256(native.read_bytes()).hexdigest()}
(P/'evidence/construction.json').write_text(json.dumps(report,indent=2));(P/'evidence/decision.txt').write_text('Read independent v013 report. Reuse installed Blender 5.2.2 and original held project-owned camera/plate/holdouts. Fundamental replacement of action hierarchy: one connected opaque asymmetric soil wedge, explicitly authored expansion node poses over eight frames, then breakup into its own two constituent tiles. No seven-chip reuse, contour rounding, opacity remedy, pigment, smoke or contact-puff polish. Only new effects/connected_wedge_v014 writes; no production integration or shared UI. Trial timing is not a verified tutorial prescription.\n');print('CONNECTED_WEDGE_ROUGH_BUILT',json.dumps(report),flush=True)
