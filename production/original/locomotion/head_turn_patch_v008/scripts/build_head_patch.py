"""Two authored2D head-turn drawings, replacing only v007's disc placeholder."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1];source=R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE' and o.get('character')=='GIRL');head=next(o for o in rig.children if 'original head and attached braid' in o.name);source_material_name=head.data.materials[0].name;rest=rig.data.bones['head'].matrix_local.copy();axis=rest.translation.x;poses={}
for f in [44,45]:s.frame_set(f);bpy.context.view_layer.update();poses[f]=rig.pose.bones['head'].matrix.copy()
braid_group=head.vertex_groups['braid'].index
braid_polys=[p for p in head.data.polygons if all(any(g.group==braid_group and g.weight>.80 for g in head.data.vertices[i].groups) for i in p.vertices)]
braid_ids=sorted({i for p in braid_polys for i in p.vertices});braid_map={v:i for i,v in enumerate(braid_ids)};braid_coords=[head.data.vertices[i].co.copy() for i in braid_ids];braid_faces=[tuple(braid_map[i] for i in p.vertices) for p in braid_polys];braid_uv={loop.vertex_index:head.data.uv_layers.active.data[loop.index].uv.copy() for loop in head.data.loops};assert braid_ids
original=head.data.materials[0].copy();original.name='V008 | original girl hair and braid RGB+alpha'
face=original.copy();face.name='V008 | original charcoal face paint, native contour'
mix=next(n for n in face.node_tree.nodes if n.type=='MIX_SHADER');value=face.node_tree.nodes.new('ShaderNodeValue');value.outputs[0].default_value=1;face.node_tree.links.new(value.outputs[0],mix.inputs[0])
eye=bpy.data.materials.new('V008 | original warm-white eye marks');eye.use_nodes=True;nt=eye.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(.81,.80,.75,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
scale=1.45/851
def sourcepoint(px,py):return Vector(((px-1010)*scale,-.04,(907-py)*scale))
def uv(px,py):return (px/1672,1-py/941)
def catmull(points,steps=5):
 result=[];N=len(points)
 for i,p1 in enumerate(points):
  p0,p2,p3=points[(i-1)%N],points[(i+1)%N],points[(i+2)%N]
  for j in range(steps):
   t=j/steps;result.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 return result
# Source-pixel hair crop keeps actual painted wisps and alpha edges; its lower
# contour is newly drawn as a fringe over a face, rather than a circular mask.
hair_pixels=[(878,86),(1112,86),(1112,174),(1090,185),(1030,190),(975,215),(935,230),(902,230),(878,220)]
braid_pixels=[(947,272),(977,281),(964,302),(945,330),(931,363),(910,389),(887,389),(870,369),(879,340),(894,310),(918,291)]
allverts={};alluv=[];faces=[];slots=[];guides={}
for f,sign in [(44,1),(45,-1)]:
 verts=[];localuv=[];localfaces=[];localslots=[];cx=axis-.010
 def polygon(points,uvs,slot):
  offset=len(verts);verts.extend(points);localuv.extend(uvs);localfaces.append(tuple(range(offset,offset+len(points))));localslots.append(slot)
 # Full cranial width is retained through both drawings. The eye/jaw/nose
 # shapes describe the view change; no edge-on card rotation or width collapse.
 raw=[(-.070,1.247),(.040,1.250),(.090,1.216),(.099,1.186),(.120,1.158),(.102,1.143),(.105,1.125),(.080,1.098),(.037,1.081),(.018,1.067),(.030,1.028),(.030,1.000),(-.027,1.000),(-.032,1.065),(-.113,1.151),(-.105,1.207)]
 contour=catmull([Vector((cx+sign*x,-.043,z)) for x,z in raw],4)
 faceuv=[uv(1020+(p.x-cx)*sign/.22*27,250+(1.17-p.z)/.20*22) for p in contour];polygon(contour,faceuv,1)
 # An ear partly veiled by hair makes the quarter-view silhouette anatomical.
 ear=[Vector((cx-sign*.084+math.cos(i*math.tau/20)*.019,-.045,1.155+math.sin(i*math.tau/20)*.029)) for i in range(20)];polygon(ear,[uv(1020+math.cos(i*math.tau/20)*8,254+math.sin(i*math.tau/20)*10) for i in range(20)],1)
 # Braid sweeps behind the neck while keeping its original source RGB/bow.
 braid=[];anchor=sourcepoint(950,280)
 for point in braid_coords:
  p=point.copy();p.x=(p.x-anchor.x)*(.93 if f==44 else .82)+(cx-.095 if f==44 else cx+.070);p.y=.008;braid.append(p)
 offset=len(verts);verts.extend(braid);localuv.extend(tuple(braid_uv[i]) for i in braid_ids);localfaces.extend(tuple(offset+i for i in face) for face in braid_faces);localslots.extend([0]*len(braid_faces))
 hair=[]
 for i,(px,py) in enumerate(hair_pixels):
  p=sourcepoint(px,py);p.x=cx+sign*(p.x-cx)*.96;p.y=-.050
  hair.append(p)
 polygon(hair,[uv(x,y) for x,y in hair_pixels],0)
 # Curved charcoal forelocks are authored separately from the upper source
 # cap. Their donor patch contains hair only, preventing the old source eye
 # from appearing as an extra mark in the new forehead opening.
 locks=[
  [(-.135,1.286),(-.070,1.310),(.025,1.282),(.109,1.253),(.129,1.224),(.114,1.202),(.128,1.188),(.077,1.205),(.041,1.245),(-.052,1.264)],
  [(.074,1.275),(.130,1.263),(.152,1.235),(.141,1.207),(.110,1.194),(.123,1.217),(.119,1.245)],
  [(-.100,1.262),(-.033,1.265),(.020,1.245),(.047,1.220),(.023,1.199),(.023,1.222),(-.046,1.242)]
 ]
 for shape in []:
  pts=catmull([Vector((cx+sign*x,-.052,z)) for x,z in shape],4);uvs=[uv(970+(p.x-cx)*sign/.27*32,166+(1.26-p.z)/.10*24) for p in pts];polygon(pts,uvs,3)
 # Restrained source-style eye marks: near eye plus a narrower far-eye sliver.
 for centerx,width,height in [(cx+sign*.060,.015,.018),(cx-sign*.024,.008,.012)]:
  z=1.176;points=[Vector((centerx-sign*width*.65,-.054,z+height*.40)),Vector((centerx+sign*width*.55,-.054,z+height*.15)),Vector((centerx-sign*width*.18,-.054,z-height*.62))];polygon(points,[(0,0)]*3,2)
 # Bake only the two new drawings against the unchanged native head matrices.
 # Desired pitch is drawn in the XZ plane; bone pose, scale and parent stay fixed.
 pitch=.20 if f==44 else -.065;draw=Matrix.Translation(poses[f].translation)@Matrix.Rotation(pitch,4,'Y')@Matrix.Translation(-rest.translation);unpose=rest@poses[f].inverted();result=[unpose@draw@p for p in verts]
 allverts[f]=result;guides[f]={'rest_outline_XZ':[list(p) for p in contour],'hair_source_pixels':hair_pixels,'braid_source_pixels':braid_pixels,'desired_drawn_pitch_radians':pitch}
 if f==44:alluv=localuv;faces=localfaces;slots=localslots
 else:assert len(result)==len(allverts[44]) and localfaces==faces
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='V008 | Two native intermediate girl head drawings';s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
collection=bpy.data.collections.new('WTSC_GIRL_HEAD_TURN_PATCH_v008');s.collection.children.link(collection);me=bpy.data.meshes.new('V008 | authored quarter-face drawings44+45');me.from_pydata(allverts[44],[],faces);me.update();ob=bpy.data.objects.new('V008 | PATCH DATA | girl head drawings44+45',me);collection.objects.link(ob)
# Materials survive the factory reset only when explicitly retained by fake user.
# Reload the exact source material/image via the native library, then construct
# the matching face/eye material in this portable file.
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.materials=[source_material_name]
paint=b.materials[0];hairmat=paint.copy();hairmat.name='V008 | original hair alpha';facemat=paint.copy();facemat.name='V008 | original face RGB opaque'
mix=next(n for n in facemat.node_tree.nodes if n.type=='MIX_SHADER');value=facemat.node_tree.nodes.new('ShaderNodeValue');value.outputs[0].default_value=1;facemat.node_tree.links.new(value.outputs[0],mix.inputs[0])
eyemat=bpy.data.materials.new('V008 | warm-white original eye color');eyemat.use_nodes=True;nt=eyemat.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(.8288183821,.7926273040,.7498113321,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs['Surface'])
for mat in [hairmat,facemat,eyemat]:me.materials.append(mat)
layer=me.uv_layers.new(name='Original v015 painting, authored face and hair registration')
for lp in me.loops:layer.data[lp.index].uv=alluv[lp.vertex_index]
for poly,slot in zip(me.polygons,slots):poly.material_index=slot
vg=ob.vertex_groups.new(name='head');vg.add(list(range(len(me.vertices))),1,'REPLACE');ob.shape_key_add(name='Basis | authored right three-quarter44');key=ob.shape_key_add(name='Authored left three-quarter45');key.data.foreach_set('co',[c for p in allverts[45] for c in p])
for f,v in [(1,0),(44,0),(45,1),(120,1)]:key.value=v;key.keyframe_insert('value',frame=f)
action=me.shape_keys.animation_data.action;action.name='V008_GIRL_HEAD | authored intermediate exposure44_45';slot=me.shape_keys.animation_data.action_slot
for l in action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
me.shape_keys.animation_data.action=None;track=me.shape_keys.animation_data.nla_tracks.new();track.name='V008 drawing clock120F';strip=track.strips.new(action.name,1,action);strip.action_slot=slot;strip.action_frame_start=1;strip.action_frame_end=120;strip.frame_end=120;strip.extrapolation='HOLD';action.use_fake_user=True
ob['head_turn_patch']='WTSC_v008_2FRAME_HEAD';ob['target_motion_revision']='v007_drawn_pose_corrections';ob['reference_head_rest_matrix']=json.dumps([list(row) for row in rest]);ob['reference_head_pose_matrices']=json.dumps({str(f):[list(row) for row in M] for f,M in poses.items()});ob['scope']='Replace only girl passing-head Mesh data at local44..45. Keep native v007 head exposure action and all body/root/foot actions unchanged.'
collection.asset_mark();collection.asset_data.description='Narrow2-frame native painted head-turn patch: authored quarter faces, jaw/nose/eyes, original textured fringe/hair/braid. Replaces v007 disc only.'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
out=P/'native/WTSC_Girl_Head_Turn_Patch_v008.blend';s.frame_set(44);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report={'source':str(source),'source_sha256':sha,'source_preserved':hashlib.sha256(source.read_bytes()).hexdigest()==sha,'patch':str(out),'patch_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'vertices':len(me.vertices),'native_drawings':[44,45],'collection':collection.name,'method':'Two authored face/jaw/nose/fringe/ear/braid drawings using source charcoal RGB+hair alpha and restrained native eye marks. Full skull width retained, no card edge-on rotation. Head bone anchor/poses are unchanged.','source_guides':guides}
(P/'evidence/build_patch.json').write_text(json.dumps(report,indent=2));print('V008_TWO_DRAWING_PATCH_BUILT',json.dumps({k:v for k,v in report.items() if k!='source_guides'}),flush=True)
