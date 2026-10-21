import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/production_review_v059'
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059a.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_PAIRED_RECOVERY_WORLD_v059a'];src=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v048a'];bpy.context.window.scene=s
root=next(o for o in src.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
added=[]
for ob in [root]+list(root.children_recursive):
 if ob.name not in s.objects:s.collection.objects.link(ob);added.append(ob.name)
contacts=[]
for ob in src.objects:
 if ob.name.startswith('v041 sole contact |') and ob.get('v046_new_boot_reference'):
  if ob.name not in s.objects:s.collection.objects.link(ob)
  contacts.append(ob.name)
fx=src.objects.get('FXv003 | fixed ground origin and controls');hidden=[]
if fx:
 for ob in fx.children_recursive:
  if ob.type in {'MESH','CURVE','GREASEPENCIL','VOLUME'}:
   ob.animation_data_clear();ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
P=R/'effects/main_impact_v015/native/WTSC_Painted_Main_Impact_Append_v015d.blend'
cn='FXv015d | PAINTED SOIL RUPTURE | separated native planes'
with bpy.data.libraries.load(str(P),link=False) as (a,b):
 assert cn in a.collections;b.collections=[cn]
col=b.collections[0];s.collection.children.link(col)
s.name='WTSC_PAIRED_RECOVERY_WORLD_v059b'
s.frame_start=1801;s.frame_end=1920;s.frame_set(1901)
report={'scene':s.name,'extra_actor_dependencies':added,'contact_planes':contacts,'hidden_old_effects':hidden,'painted_impact':{'path':str(P),'collection':col.name,'sha256':hashlib.sha256(P.read_bytes()).hexdigest()},'original_source_sha256':json.loads((O/'integration_inspection.json').read_text())['sources'],'scope':'Five-second recovery staging, latest v058d world; repaired missing appended actor dependencies and linked source boot contact planes. Original v048a files and v058d untouched. New painted FX are a fresh candidate for visual review, not a previous acceptance.'}
(O/'integration_v059b.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059b.blend'),compress=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [1801,1829,1844,1881,1901,1918]:
 s.frame_set(f);s.render.filepath=str(O/f'candidate_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('CANDIDATE_KEY',f,flush=True)
print('CANDIDATE_READY',flush=True)
