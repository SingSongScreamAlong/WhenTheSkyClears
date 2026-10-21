"""Neutral current model plus real older preferred native reference, no source save."""
import bpy,math,json,hashlib,ast,shutil
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];V=P/'previews/model_review';V.mkdir(exist_ok=True);new=P/'native/WTSC_Connected_Weight_Loading_v048.blend';old=ROOT/'locomotion/neck_collar_connection_v041/native/WTSC_Neck_Collar_Connection_Candidate_v041.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]};assert hashes[str(old)]=='c9806d2d905168f9e1ff2adbc20842ac298e37def9f37223d228639f414b931c'
for f,label in [(1,'CONTACT'),(5,'LOADING'),(9,'PASSING')]:shutil.copyfile(P/'previews/frames_V048'/('FRAME_%04d.png'%f),V/('CURRENT_WALK_%s_F%02d.png'%(label,f)))
bpy.ops.wm.open_mainfile(filepath=str(new),load_ui=False,use_scripts=False);S=bpy.data.scenes['V048 | CONNECTED WEIGHT LOADING | ordinary walk'];bpy.context.window.scene=S;C=bpy.data.collections['V046 | restored original painted wardrobe'];RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
hidden={o:o.hide_render for o in S.objects if o.parent==RIGS['GIRL'] and o.type=='MESH'}
for o in hidden:o.hide_render=True
S.frame_set(1);S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;S.render.filepath=str(V/'CURRENT_BOY_ACTUAL_F1_SAME_METRES.png');bpy.ops.render.render(write_still=True,scene=S.name)
for o,h in hidden.items():o.hide_render=h
root=bpy.data.objects['V048 | shared travel | steady .73125mps'];root.animation_data_clear();root.location.x=0;S.camera.animation_data_clear();S.camera.location=(0,-10,.8)
for r in RIGS.values():
 r.animation_data_clear()
 for pb in r.pose.bones:pb.matrix_basis.identity()
S.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();deviation=0
for r in RIGS.values():
 e=r.evaluated_get(dg)
 for n,b in e.pose.bones.items():deviation=max(deviation,(b.head-r.data.bones[n].head_local).length,(b.tail-r.data.bones[n].tail_local).length)
assert deviation<1e-6,deviation
# Limb clothes were cached to walking poses; regenerate their actual straight
# rest-axis shapes rather than displaying a neutral skeleton in walking clothes.
tree=ast.parse((ROOT/'locomotion/painted_outfit_restoration_v046/scripts/build_outfits.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['interp','smooth','rounded']];exec(compile(tree,'same_wardrobe_geometry_for_true_neutral','exec'),globals())
for who,r in RIGS.items():
 for side in ['near','far']:
  for kind in ['sleeve','leg']:
   o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));n1=('upper_arm_' if kind=='sleeve' else 'thigh_')+side;n2=('forearm_' if kind=='sleeve' else 'shin_')+side;H=r.data.bones[n1].head_local;K=r.data.bones[n1].tail_local;A=r.data.bones[n2].tail_local;l1=r.data.bones[n1].length;total=l1+r.data.bones[n2].length;start=-.008 if kind=='sleeve' else -.025;end=l1+.027 if kind=='sleeve' else total-.030;rows=49 if kind=='sleeve' else 65;verts=[]
   def radius(t):
    if kind=='sleeve':return interp(t,[(0,.038),(.12,.049),(.5,.045),(.85,.034),(1,.041)])
    return interp(t,[(0,.060),(.13,.063),(.4,.052),(.56,.043),(.77,.044),(.92,.034),(1,.040)]) if who=='BOY' else interp(t,[(0,.043),(.45,.036),(.56,.031),(.78,.033),(1,.024)])
   for row in range(rows):
    t=row/(rows-1);d=start+(end-start)*t;center,tangent=rounded(H,K,A,l1,d,.018 if kind=='sleeve' else .022);normal=Vector((-tangent.z,0,tangent.x))
    for col in range(9):
     p=center+normal*((col/8*2-1)*radius(t));p.y=0;verts.append(p)
   o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in verts for c in p]);o.data.update()
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;S.render.filepath=str(V/'CURRENT_NEUTRAL_STANDING_SIDE.png');bpy.ops.render.render(write_still=True,scene=S.name)
# Actual v041 native and its original materials/compositor. Change only the
# review camera so one metre occupies the same pixels as in current renders.
bpy.ops.wm.open_mainfile(filepath=str(old),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update();r=bpy.data.objects['LOCO_BOY | RIG'];T=r.parent;camdata=bpy.data.cameras.new('RAM ONLY same-metres model camera');camdata.type='ORTHO';camdata.ortho_scale=3.25;cam=bpy.data.objects.new(camdata.name,camdata);S.collection.objects.link(cam);cam.location=(r.matrix_world.translation.x+.4,-10,T.matrix_world.translation.z+.8);cam.rotation_euler=(math.pi/2,0,0);S.camera=cam;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;S.render.filepath=str(V/'OLDER_V041_BOY_ACTUAL_F1_SAME_METRES.png');bpy.ops.render.render(write_still=True,scene=S.name)
for file,d in hashes.items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==d
(P/'evidence/MODEL_REVIEW_RENDER.json').write_text(json.dumps({'source_hashes':hashes,'sources_unchanged':True,'current_neutral':'Actual current native anatomy, identity rest-bone poses; walking sleeve/leg caches rebuilt to those rest axes IN RAM. No native save.','max_neutral_bone_deviation_m':deviation,'current_walk_frames':[1,5,9],'framing':{'resolution':[1280,720],'ortho_width_m':3.25,'camera_height_above_sole_plane_m':.8,'boy_x_relative_camera_m':-.4},'older_reference':'Actual v041 F1 painted BOY native; original paper backdrop/materials/compositor and older anatomy. Same metres/pixel camera. It is a walking reference, not a neutral pose or current proportions. No girl colour model was in that preferred boy study.','no_rescale_or_design_edits':True},indent=2));print('V048_NEUTRAL_AND_OLDER_MODEL_REVIEW_READY_SOURCES_UNCHANGED',flush=True)
