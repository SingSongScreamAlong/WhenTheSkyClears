import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];FILE=P/'native/WTSC_Age10_Static_Proportion_Candidate_v044.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V044 | AGE TEN | STATIC SCALE FIRST'];bpy.context.window.scene=S;S.frame_set(0)
S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.resolution_x=1800;S.render.resolution_y=1200;S.render.resolution_percentage=100
ART=bpy.data.collections['V044 | age10 editable profile anatomy'];BEFORE=bpy.data.collections['V044 | before F1 source painting snapshots'];FRONT=bpy.data.collections['V044 | front CONSTRUCTION ONLY | no front art available'];GUIDE=bpy.data.collections['V044 | dimension grid and surface landmarks']
def show(c,on):
 for o in c.objects:o.hide_render=not on;o.hide_viewport=not on
def render(name):S.render.filepath=str(P/'previews'/name);bpy.context.view_layer.update();bpy.ops.render.render(write_still=True,scene=S.name)
show(ART,True);show(BEFORE,False);show(FRONT,False);render('AGE10_AFTER_NEUTRAL_PROFILE.png')
R={}
for who in ['BOY','GIRL']:
 rig=bpy.data.objects['V044 '+who+' | estimated joint centres'];r={'bone_lengths_m':{b.name:b.length for b in rig.data.bones},'visible_part_geometry_bounds':{},'candidate_rig_actions':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None}
 dg=bpy.context.evaluated_depsgraph_get()
 for o in ART.objects:
  if o.parent!=rig or o.type!='MESH':continue
  e=o.evaluated_get(dg);V=[e.matrix_world@v.co for v in e.data.vertices];r['visible_part_geometry_bounds'][o.name]={'xyz_bounds':[[min(v[i] for v in V),max(v[i] for v in V)] for i in range(3)],'vertices':len(V)}
 R[who]=r
show(ART,False);show(BEFORE,True)
bpy.data.objects['static title'].data.body='BEFORE | existing F1 source poses | same metres and same camera'
for o in GUIDE.objects:
 if any(k in o.name for k in ['marker','BOY height','GIRL height']):o.hide_render=True
render('BEFORE_EXISTING_F1_SAME_SCALE.png')
show(BEFORE,False);show(FRONT,True)
bpy.data.objects['static title'].data.body='AGE TEN | FRONT CONSTRUCTION GUIDE | estimated joints; no finished front art'
for o in GUIDE.objects:
 if any(k in o.name for k in ['marker','BOY height','GIRL height']):o.hide_render=False
render('AGE10_FRONT_CONSTRUCTION_GUIDE.png')
# Detail is a camera crop of the same actual native assets, never image generation.
show(FRONT,False);show(ART,True)
for o in GUIDE.objects:o.hide_render=True
S.camera.location=(0,-10,1.18);S.camera.data.ortho_scale=2.05;S.render.resolution_x=1800;S.render.resolution_y=900;render('AGE10_AFTER_HEAD_HAND_DETAIL.png')
after=hashlib.sha256(FILE.read_bytes()).hexdigest();assert before==after
(P/'evidence/STATIC_COLD_REOPEN_AND_RENDER.json').write_text(json.dumps({'native_sha256':before,'native_unchanged_during_render':True,'scene':S.name,'age10_parts':R,'renders':['AGE10_AFTER_NEUTRAL_PROFILE.png','BEFORE_EXISTING_F1_SAME_SCALE.png','AGE10_FRONT_CONSTRUCTION_GUIDE.png','AGE10_AFTER_HEAD_HAND_DETAIL.png'],'static_only':True,'no_animation_acceptance':True},indent=2));print('V044_STATIC_REVIEW_RENDER_COMPLETE',flush=True)
