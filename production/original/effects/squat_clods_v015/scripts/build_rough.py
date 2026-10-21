"""Two early, fixed-size squat clods released from overlapping root flow."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1]
for d in ['native','previews','evidence']:(P/d).mkdir(parents=True,exist_ok=True)
s=bpy.data.scenes['FXv014 | connected wedge TWO TONE ROUGH'];bpy.context.window.scene=s
origin=bpy.data.objects['FXv014 | fixed impact anchor | ROUGH'].location.copy();camera_matrix=[list(v) for v in s.camera.matrix_world]
for col in list(s.collection.children):s.collection.children.unlink(col)
for o in list(s.collection.objects):
    if o!=s.camera:s.collection.objects.unlink(o)
s.name='FXv015 | squat clods SILHOUETTE ROUGH';s.frame_start=1;s.frame_end=32;s.render.fps=24;s.render.fps_base=1;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
c=bpy.data.collections.new('FXv015 | OVERLAPPING SQUAT CLODS | rough only');s.collection.children.link(c)
r=bpy.data.objects.new('FXv015 | impact anchor | ROUGH',None);c.objects.link(r);r.location=origin;r['start_frame']=7.;r['age']=0.
fc=r.driver_add('["age"]');v=fc.driver.variables.new();v.name='start';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["start_frame"]';fc.driver.expression='frame-start'
def drive(owner,path,expr):
    fc=owner.driver_add(path);v=fc.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["age"]';fc.driver.expression=expr
def material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
clay=material('FXv015 | flat clay soil',(.32,.21,.11));dark=material('FXv015 | flat dark soil',(.085,.058,.032))
# Explicit broad lobes/bites. These are not corners cut off a slab and not
# scaled poses: each primary contour keeps its area and bulk through flight.
outlines={
 'A':[(-.245,-.055),(-.225,-.09),(-.14,-.105),(-.095,-.145),(-.015,-.13),(.045,-.15),(.12,-.105),(.19,-.09),(.205,-.04),(.24,-.015),(.215,.055),(.175,.07),(.16,.12),(.09,.125),(.045,.155),(-.025,.14),(-.075,.165),(-.145,.125),(-.20,.11),(-.195,.055),(-.24,.03)],
 'B':[(-.19,-.035),(-.16,-.085),(-.105,-.095),(-.055,-.12),(.015,-.10),(.065,-.125),(.12,-.09),(.175,-.055),(.165,-.01),(.205,.025),(.17,.07),(.115,.085),(.075,.125),(.015,.105),(-.04,.13),(-.085,.105),(-.145,.11),(-.165,.065),(-.195,.025)]
}
specs={'A':{'center':[-.12,.08],'vx':-1.4,'vz':4.8,'theta0':.07,'spin':-.85,'rest_angle':-.10,'mat':clay,'depth':-.022},'B':{'center':[.14,.035],'vx':1.45,'vz':4.0,'theta0':-.10,'spin':1.,'rest_angle':.08,'mat':dark,'depth':-.012}}
def area(pts):return abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2)
def airborne(piece,t):
    f=specs[piece];cx,cz=f['center'];x=cx+f['vx']*t/(1+.65*t);z=cz+f['vz']*t-7*t*t;ang=f['theta0']+f['spin']*t;co=math.cos(ang);sn=math.sin(ang);pts=[(x+px*co+pz*sn,z-px*sn+pz*co) for px,pz in outlines[piece]];return pts,x,z,ang
flight={}
for piece in outlines:
    # Ignore the initially buried part of the launch; solve the later downward
    # ground crossing. This rough uses one flat bank level at the impact anchor.
    t=specs[piece]['vz']/14+.01
    while min(z for x,z in airborne(piece,t)[0])>0:t+=.01
    a=t-.01;b=t
    for _ in range(40):
        mid=(a+b)/2
        if min(z for x,z in airborne(piece,mid)[0])>0:a=mid
        else:b=mid
    land=(a+b)/2;pts,lx,lz,la=airborne(piece,land);flight[piece]={'landing_seconds':land,'landing_age':1+24*land,'landing_x':lx,'landing_angle':la,'launch_age':1,'apex_age':1+specs[piece]['vz']/14*24,'area_metres2':area(outlines[piece])}
def clod_pose(piece,age):
    f=specs[piece]
    if age==0:
        # Full-size mass is present but predominantly submerged before ejection.
        x=-.07 if piece=='A' else .075;z=-.115 if piece=='A' else -.15;ang=f['theta0']
    else:
        t=(age-1)/24;fl=flight[piece]
        if t<fl['landing_seconds']:return airborne(piece,t)[0]
        after=t-fl['landing_seconds'];x=fl['landing_x']+f['vx']*.012*(1-math.exp(-16*after));ang=f['rest_angle']+(fl['landing_angle']-f['rest_angle'])*math.exp(-18*after);co=math.cos(ang);sn=math.sin(ang);z=-min(-px*sn+pz*co for px,pz in outlines[piece])
    co=math.cos(ang);sn=math.sin(ang);return [(x+px*co+pz*sn,z-px*sn+pz*co) for px,pz in outlines[piece]]
# Attached root lobes use the same squat irregular bulk, partly buried. This
# replaces the narrow stalk-like connections caught in the first actual keys.
# age : center x, center z, horizontal factor, vertical factor
root_states={
 'A':{0:(-.03,-.095,1.30,.75),1:(-.05,-.025,1.30,.90),2:(-.11,.015,1.28,.90),3:(-.15,-.04,1.40,.75),4:(-.18,-.065,1.50,.60),5:(-.20,-.08,1.60,.55),8:(-.21,-.09,1.65,.55)},
 'B':{0:(.10,-.065,1.40,.75),1:(.13,-.025,1.40,.90),2:(.19,.015,1.40,.90),3:(.23,-.025,1.50,.75),4:(.26,-.05,1.60,.55),5:(.28,-.065,1.65,.50),8:(.29,-.07,1.70,.50)}
}
def root_state(piece,age):
    states=root_states[piece];keys=sorted(states)
    if age>=keys[-1]:return states[keys[-1]]
    a=max(k for k in keys if k<=age);b=min(k for k in keys if k>=age)
    if a==b:return states[a]
    u=(age-a)/(b-a);return tuple(x*(1-u)+y*u for x,y in zip(states[a],states[b]))
def root_pose(piece,age):
    cx,cz,sx,sz=root_state(piece,age);return [(cx+x*sx,cz+z*sz) for x,z in outlines[piece]]
def mesh_object(name,poses,mat,y):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,y,z) for x,z in poses[0]],[],[tuple(range(len(poses[0])))]);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);o.parent=r
    for age,pts in enumerate(poses):
        k=o.shape_key_add(name=f'AGE_{age:02d}');k.interpolation='KEY_LINEAR'
        for v,(x,z) in zip(k.data,pts):v.co=(x,y,z)
    me.shape_keys.use_relative=False;drive(me.shape_keys,'eval_time','10*max(0,min(31,t))');drive(o,'hide_render','t<0');drive(o,'hide_viewport','t<0');return o
tables={piece:[clod_pose(piece,age) for age in range(32)] for piece in outlines}
for piece in outlines:
    err=max(abs(area(p)-flight[piece]['area_metres2']) for p in tables[piece]);assert err<1e-7,err;flight[piece]['max_area_error_metres2']=err
    mesh_object('FXv015 | primary squat clod '+piece,tables[piece],specs[piece]['mat'],specs[piece]['depth'])
mesh_object('FXv015 | attached broad dark root clod',[root_pose('B',a) for a in range(32)],dark,.004)
mesh_object('FXv015 | overlapping broad clay root clod',[root_pose('A',a) for a in range(32)],clay,-.004)
for node in s.compositing_node_group.nodes:
    if node.type=='R_LAYERS':node.scene=s;node.layer='RUPTURE'
q=world_to_camera_view(s,s.camera,origin);qx=world_to_camera_view(s,s.camera,origin+Vector((1,0,0)));ppm=(qx.x-q.x)*1920
r['construction']='Two fixed-size squat clods emerge early from overlapping shallow root flow. Independent ragged boundaries open gaps during rise as base diminishes. No intact plate, clean section cut, growth of primary outlines, smoke or contact polish.'
s.frame_set(10);r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();native=P/'native/WTSC_Squat_Clods_SILHOUETTE_ROUGH_v015.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
overlap=[]
for age in range(1,7):
    lh=max(z for x,z in root_pose('A',age));rh=max(z for x,z in root_pose('B',age));overlap.append({'age':age,'scene_frame':age+7,'A_bottom_minus_root_top':min(z for x,z in tables['A'][age])-lh,'B_bottom_minus_root_top':min(z for x,z in tables['B'][age])-rh})
report={'blender':bpy.app.version_string,'source':'v014 native rough read-only','camera_matrix':camera_matrix,'root':list(origin),'pixels_per_metre':ppm,'fps':24,'frames':[1,32],'impact_frame':7,'primary_fragments':2,'fixed_primary_contours':outlines,'flight':flight,'overlap_to_gap_progression':overlap,'root_states':root_states,'materials':2,'material_layout':'One flat tone per primary clod; matching flat root lobes. No broad light-front/dark-side faces.','smoke':False,'opacity_animation':False,'contour_rounding':False,'pigment':False,'contact_puffs':False,'landing_support':'Flat rough bank level at impact anchor; detailed terrain/contact work deferred.','native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'status':'Silhouette construction test for review before polish. No artistic acceptance.'}
(P/'evidence/construction.json').write_text(json.dumps(report,indent=2));(P/'evidence/decision.txt').write_text('Read exact independent v014 review before editing. Reuse verified installed Blender5.2.2 and original project-owned held camera, plate and holdouts. Replace slab construction with two explicit squat lobed contours at constant area from the start; position/orientation carries the primary motion. They emerge from below the bank and overlap irregular matching-tone base lobes before ragged gaps open during the upward travel. Shallow base diminishes before clod apex. No clean fracture seam or faceted side/front surface. No rounding/opacity correction, pigment, smoke, puffs, pack work or production integration. All writes under effects/squat_clods_v015; v014 is read only. No shared UI.\n');print('SQUAT_CLODS_ROUGH_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['fixed_primary_contours','camera_matrix','root_states']}),flush=True)
