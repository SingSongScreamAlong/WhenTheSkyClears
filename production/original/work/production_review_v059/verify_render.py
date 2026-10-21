import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/production_review_v059';OUT=O/'WTSC_Production_Benchmark_v059.blend'
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059c.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_PAIRED_RECOVERY_WORLD_v059c'];s.name='WTSC_RECOVERY_WORLD_v059'
mask=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'];mask.name='WTSC_TITLE_VISIBILITY_REVIEW_v059';mask.frame_start=1801;mask.frame_end=1920
for sc in [s,mask]:
 sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100;sc.render.fps=24;sc.render.filepath='//renders_v059/'+sc.name;sc.render.use_sequencer=False
master=bpy.data.scenes.new('WTSC_5S_REVIEW_MASTER_v059');master.frame_start=1;master.frame_end=120;master.render.fps=24;master.render.resolution_x=3840;master.render.resolution_y=2160;master.render.resolution_percentage=100
seq=master.sequence_editor_create();strip=seq.strips.new_scene('75-80s paired recovery | original clock1801-1920',s,channel=1,frame_start=1)
music=R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
snd=seq.strips.new_sound('Supplied music | original75-80 seconds',str(music),channel=2,frame_start=-1799);snd.frame_final_start=1;snd.frame_final_end=121;snd.volume=1
snd.sound.pack()
master.render.filepath='//renders_v059/WTSC_Recovery_Benchmark_v059'
readme=bpy.data.texts.new('START HERE | v059 reviewed production benchmark')
readme.write('Five-second75-80s production candidate. WORLD1801-1920, MASTER1-120,24fps. Latestv058d environment plusv048a paired recovery, independently baked original camera, original boot contacts, new late palm contact, existing original painted ground impact study. Sources preserved. Actual preview1280x720; three keys3840x2160. Full film still unfinished. Inspect title visibility scene separately: inherited lettering hides acting. No finished-film or Arcane-equivalence claim. See START_HERE_v059.txt and verification/production review in this folder.')
bpy.context.window.scene=s;s.frame_set(1901)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
before_sha=hashlib.sha256(OUT.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(OUT),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_RECOVERY_WORLD_v059'];mask=bpy.data.scenes['WTSC_TITLE_VISIBILITY_REVIEW_v059'];bpy.context.window.scene=s
refs=json.loads((O/'integration_inspection.json').read_text());errors={'baked_camera':0};rows=[];root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
boots=[o for o in root.children_recursive if o.get('v007_role')=='support_boot']
for row in refs['camera_samples']:
 s.frame_set(row['f']);bpy.context.view_layer.update()
 errors['baked_camera']=max(errors['baked_camera'],max(abs(s.camera.matrix_world[i][j]-row['matrix'][i][j]) for i in range(4) for j in range(4)))
 if row['f'] in [1801,1844,1881,1897,1901,1918,1920]:
  deps=bpy.context.evaluated_depsgraph_get()
  feet={}
  for ob in boots:
   e=ob.evaluated_get(deps);ps=[e.matrix_world@v.co for v in e.data.vertices];feet[ob.name]={'minZ':min(p.z for p in ps),'minX':min(p.x for p in ps),'maxX':max(p.x for p in ps)}
  rows.append({'frame':row['f'],'feet':feet})
checks={'camera_all120_matches_original_recovery':errors['baked_camera']<1e-5,'all_original_sources_sha256_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in refs['sources'].items()),'all_file_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.type!='RENDER_RESULT'),'four_new_contact_meshes':sum(o.get('v059_role')=='late_contact_native_drawing' for o in s.objects)==4,'four_original_boot_contacts':sum(o.name.startswith('v041 sole contact |') and bool(o.get('v046_new_boot_reference')) for o in s.objects)==4,'world_frame_range':[s.frame_start,s.frame_end]==[1801,1920],'master_frame_range':[bpy.data.scenes['WTSC_5S_REVIEW_MASTER_v059'].frame_start,bpy.data.scenes['WTSC_5S_REVIEW_MASTER_v059'].frame_end]==[1,120]}
(O/'cold_reopen_verification.json').write_text(json.dumps({'checks':checks,'errors':errors,'file_sha256':before_sha,'foot_samples':rows,'render_scope':'All120frames720p; three4Kkeys; three native final-title-maskkeys. No live native player observation.'},indent=2))
assert all(checks.values()),checks
for sc in [s,mask]:
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.eevee.taa_render_samples=32;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG'
folder=O/'frames_world';folder.mkdir(exist_ok=True)
for f in range(1801,1921):
 s.frame_set(f);s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 if (f-1800)%12==0:print('RENDERED_WORLD',f,flush=True)
for f in [1844,1901,1918]:
 mask.frame_set(f);mask.render.filepath=str(O/f'title_visibility_{f}.png');bpy.ops.render.render(write_still=True,scene=mask.name);print('TITLE_KEY',f,flush=True)
bpy.context.window.scene=s;s.render.resolution_x=3840;s.render.resolution_y=2160;s.eevee.taa_render_samples=64
for f in [1844,1901,1918]:
 s.frame_set(f);s.render.filepath=str(O/f'native4K_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('NATIVE_4K_KEY',f,flush=True)
assert hashlib.sha256(OUT.read_bytes()).hexdigest()==before_sha
(O/'renders_complete.json').write_text(json.dumps({'world_frames':120,'frame_range':[1801,1920],'fps':24,'preview_size':[1280,720],'native4K_keys':[1844,1901,1918],'native_title_keys':[1844,1901,1918],'saved_native_unchanged_after_render':True},indent=2))
print('V059_ALL_RENDERS_COMPLETE',flush=True)
