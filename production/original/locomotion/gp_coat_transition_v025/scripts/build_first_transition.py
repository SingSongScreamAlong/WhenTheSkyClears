"""Authored GP coat drawing study, not cutout-to-stroke conversion.
Current5.2 API verified in RUNTIME_API_AND_REGISTRATION.json.
Only one half-step is drawn; v024 rig/support and identity parts remain reference.
"""
import bpy,json,math,random,csv
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_WALK_v024.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;body=bpy.data.objects['LOCO_BOY | PAINT body']
C=bpy.data.collections.new('V025 | separate authored GP coat transition');S.collection.children.link(C)
gp=bpy.data.grease_pencils.new('V025 | authored cloth drawings');ob=bpy.data.objects.new('V025 | COAT drawings | editable GP',gp);C.objects.link(ob);ob.parent=T
ob['drawing_scope']='Original contour/fold paths authored for this half-step; not converted cutout strokes. Existing packed pigment reused for texture only.'
gp.stroke_depth_order='3D'
def material(name,color,fill=True,stroke=False):
    m=bpy.data.materials.new(name);bpy.data.materials.create_gpencil_data(m);g=m.grease_pencil;g.show_fill=fill;g.show_stroke=stroke;g.fill_color=color;g.color=color;gp.materials.append(m);return len(gp.materials)-1,m
BASE,_=material('V025 | charcoal cloth base',(.014,.015,.014,1))
SHADOW,_=material('V025 | folded ink shadow',(.004,.005,.005,.65))
WASH,_=material('V025 | brushed wash plane',(.032,.034,.031,.48))
RIM,_=material('V025 | soft compressed fold edge',(.045,.047,.043,.45))
INK,_=material('V025 | dry charcoal contour',(.004,.005,.005,.65),False,True)
GRAIN,_=material('V025 | retained charcoal grain',(.031,.033,.030,.35),False,True)
TEXTURE,tex=material('V025 | original packed coat pigment',(.8,.8,.8,.75))
original_image=next(n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
tex.grease_pencil.fill_style='TEXTURE';tex.grease_pencil.fill_image=original_image
tex.grease_pencil.texture_scale=(.15,.32);tex.grease_pencil.texture_offset=(.325,.37);tex.grease_pencil.texture_clamp=False
layer=gp.layers.new('01 | new coat silhouette and painted planes',set_active=True);layer.use_lights=False
def catmull(points,steps=5,closed=False):
    out=[];n=len(points)
    for i in range(n if closed else n-1):
        a=Vector(points[(i-1)%n] if closed or i else points[0]);b=Vector(points[i]);c=Vector(points[(i+1)%n]);d=Vector(points[(i+2)%n] if closed or i+2<n else points[-1])
        for j in range(steps):
            t=j/steps;out.append((b*2+(-a+c)*t+(a*2-b*5+c*4-d)*t*t+(-a+b*3-c*3+d)*t*t*t)*.5)
    if not closed:out.append(Vector(points[-1]))
    return out
def lerp(a,b,t):return a+(b-a)*t
def curve_value(f,knots):
    # Individually authored timing per cloth feature, no periodic sine flapping.
    i=max(0,min(len(knots)-2,next((j for j in range(len(knots)-1) if f<=knots[j+1][0]),len(knots)-2)))
    a,v=knots[i];b,w=knots[i+1];t=max(0,min(1,(f-a)/(b-a)));t=t*t*(3-2*t)
    return lerp(v,w,t)
def add(d,points,mi,H,angle,y=-.017,cyclic=False,radius=.0012,opacity=1,soft=.22):
    points=catmull(points,5,cyclic);d.add_strokes([len(points)]);s=d.strokes[-1];s.cyclic=cyclic;s.material_index=mi;s.softness=soft
    for p,v in zip(s.points,points):
        x,z=v;xx=x*math.cos(angle)+z*math.sin(angle);zz=-x*math.sin(angle)+z*math.cos(angle)
        p.position=(H.x+xx,y,H.z+zz);p.radius=radius;p.opacity=opacity
    return s
records=[]
for f in range(17,33):
    S.frame_set(f);bpy.context.view_layer.update();H=rig.pose.bones['pelvis'].head.copy();ch=rig.pose.bones['chest'].tail;angle=math.atan2(ch.x-H.x,ch.z-H.z)
    d=layer.frames.new(f).drawing
    compress=curve_value(f,[(17,0),(19,.85),(21,1),(24,.25),(27,0),(32,.1)])
    # Tail keeps descending after pelvis lowF19.25; tucks as thigh passes, peaksF26 (between body keys).
    tail_z=curve_value(f,[(17,-.018),(20,-.030),(23,-.009),(26,.023),(29,.011),(32,-.005)])
    tail_x=curve_value(f,[(17,-.143),(20,-.149),(23,-.130),(26,-.103),(29,-.115),(32,-.137)])
    belly=curve_value(f,[(17,.105),(20,.115),(23,.108),(26,.096),(32,.104)])
    hem=curve_value(f,[(17,.086),(20,.085),(23,.072),(26,.050),(29,.062),(32,.084)])
    # New closed contour. Upper attachment/collar is retained separately from original paint.
    silhouette=[(-.055,.505),(.033,.509),(.089,.455),(.113,.382),(belly,.283),(.090,.195),(.082,.125),(hem,.041),(.046,.009),(-.022,-.009),(tail_x,tail_z),(-.121,.071),(-.086,.168),(-.083,.279),(-.101,.382),(-.095,.448)]
    add(d,silhouette,BASE,H,angle,cyclic=True,radius=.0008)
    # Retained pigment is a wash inside the new shape, not a transferred old silhouette.
    add(d,silhouette,TEXTURE,H,angle,y=-.0173,cyclic=True,radius=.0008,opacity=.65)
    # Connected side shadow and broad front cloth plane describe volume, with pose-specific waist compression.
    side=[(-.087,.451),(-.053,.411),(-.038,.294),(-.049,.188),(-.045,.095),(-.026,.004),(tail_x,tail_z),(-.114,.100),(-.084,.217),(-.093,.365)]
    add(d,side,SHADOW,H,angle,y=-.018,cyclic=True)
    front=[(.048,.446),(.090,.387),(belly-.011,.301),(.067,.220),(.045,.168),(.033,.103),(.043,.039),(.065,.052),(.079,.137),(.085,.236),(.097,.344)]
    add(d,front,WASH,H,angle,y=-.0185,cyclic=True)
    foldz=.17-.015*compress
    fold=[(-.065,foldz+.025),(-.024,foldz+.010),(.026,foldz-.007),(.077,foldz+.018),(.031,foldz+.003),(-.023,foldz+.018)]
    add(d,fold,SHADOW,H,angle,y=-.019,cyclic=True,opacity=.5+.5*compress)
    foldrim=[(-.063,foldz+.034),(-.022,foldz+.019),(.025,foldz+.003),(.064,foldz+.024)]
    add(d,foldrim,GRAIN,H,angle,y=-.020,radius=.0013,opacity=.35+.3*compress)
    # Front/back tail overlap changes shape at the hip, not a uniform oscillation.
    lap=[(.031,.148),(.018,.100),(.032,.038),(.047,.012),(hem,.041),(.071,.094)]
    add(d,lap,SHADOW,H,angle,y=-.0195,cyclic=True,opacity=.60)
    add(d,[(-.081,.414),(-.057,.333),(-.048,.249),(-.061,.192)],INK,H,angle,y=-.020,radius=.0009,opacity=.5)
    add(d,[(.071,.412),(.068,.327),(.050,.251),(.030,.198)],GRAIN,H,angle,y=-.020,radius=.0013,opacity=.5)
    # Fixed-seed irregular dry marks follow the newly drawn fabric planes. No frame-to-frame noise.
    rng=random.Random(251)
    for j in range(125):
        z=rng.uniform(.045,.445);x=rng.uniform(-.065,.072);length=rng.uniform(.006,.024);tilt=rng.uniform(-.4,.6)
        x+=.012*compress*math.exp(-((z-foldz)/.07)**2)
        add(d,[(x,z),(x+tilt*length*.5,z+length*.45),(x+tilt*length,z+length)],GRAIN if j%3 else INK,H,angle,y=-.0205,radius=rng.uniform(.0003,.0009),opacity=rng.uniform(.18,.48),soft=.5)
    records.append({'frame':f,'pelvis_z':H.z,'sternum_x':ch.x,'sternum_z':ch.z,'compress':compress,'rear_tail_local_x':tail_x,'rear_tail_local_z':tail_z,'front_hem_local_x':hem,'strokes':len(d.strokes)})
# Retain original collar/shoulder painting with a non-destructive rest-space mask before deformation.
g=bpy.data.node_groups.new('V025 | original collar only | rest-coordinate mask','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=g.nodes;l=g.links;a=n.new('NodeGroupInput');b=n.new('NodeGroupOutput');pos=n.new('GeometryNodeInputPosition');sep=n.new('ShaderNodeSeparateXYZ');lt=n.new('ShaderNodeMath');lt.operation='LESS_THAN';lt.inputs[1].default_value=1.005;dele=n.new('GeometryNodeDeleteGeometry');dele.domain='POINT';l.new(pos.outputs[0],sep.inputs[0]);l.new(sep.outputs['Z'],lt.inputs[0]);l.new(a.outputs[0],dele.inputs['Geometry']);l.new(lt.outputs[0],dele.inputs['Selection']);l.new(dele.outputs[0],b.inputs[0]);mod=body.modifiers.new('V025 | keep original collar, GP replaces coat','NODES');mod.node_group=g
body.modifiers.move(len(body.modifiers)-1,0)
ob['V025_timing']='F17-32 at30fps, one contact-loading-passing-up transition only; no inferred complete cycle'
S['V025_scope']='Separate GP coat transition over unchangedv024 support; original head/hair/arms/hands/collar/legs/boots retained'
S.frame_start=17;S.frame_end=32;S.frame_set(20);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_GP_Coat_Transition_v025.blend'),compress=True)
(P/'evidence/AUTHORED_COAT_TRANSITION.json').write_text(json.dumps({'frames':records,'data_rna':gp.bl_rna.identifier,'object_type':ob.type,'current_API':True,'automatic_interpolation_operator_used':False,'source_silhouette_converted':False,'packed_pigment_image':original_image.name,'texture_material_values':{'scale':list(tex.grease_pencil.texture_scale),'offset':list(tex.grease_pencil.texture_offset)},'drawing_frames':len(layer.frames)},indent=2))
print('V025_COAT_NATIVE_BUILT',len(layer.frames))
