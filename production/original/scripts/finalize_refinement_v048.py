"""Publish a factual local checkpoint after actual native/media/visual review."""
import json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048';v=sys.argv[1]
build=json.loads((N/f'build_{v}.json').read_text());media=json.loads((N/f'media_qa_{v}.json').read_text());cold=json.loads((N/f'cold_verification_{v}.json').read_text())
assert media['actual_frames_decoded']==120 and media['resolution']==[3840,2160] and media['music75_80_original_correlation']>.99
for k in ['native','movie4K','view1080p']:
 p=Path(media[k]['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==media[k]['sha256']
base=json.loads((R/'notes/world_v016/motion_trial_build_v046.json').read_text())
for path,sha in base['preserved_inputs'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
assert hashlib.sha256(Path(build['parent_native']).read_bytes()).hexdigest()==build['parent_sha256']
visual=N/f'movie_visual_review_{v}.json';assert visual.exists(),visual
review=json.loads(visual.read_text())
checkpoint={'status':'Retained working refinement, artistically unfinished. Full trailer remains earlier v040.','version':v,'native':media['native'],'movie4K':media['movie4K'],'view1080p':media['view1080p'],'native_resolution':[3840,2160],'fps':24,'global_frames':[1801,1920],'seconds':5,'full_trailer':'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend','full_trailer_propagated':False,'artistic_acceptance':False,'technical_verification':str(N/f'cold_verification_{v}.json'),'media_verification':str(N/f'media_qa_{v}.json'),'visual_review':str(visual),'preserved_source_files_checked':len(base['preserved_inputs']),'next_world_pass':str(N/'next_world_priorities.json'),'scope':build['scope'],'remaining':['Angular torso/forearm/cuff construction and whole-body weight','Quick replacement-drawing head turn and differing hair brush language','Contact is a light offered touch, not a load-bearing clasp','Main impact timing, dust/ground interaction and persistent scar require further craft review','Extend world detail to village/woods/school/camp and review through actual title mask']}
(N/f'checkpoint_{v}.json').write_text(json.dumps(checkpoint,indent=2))
guide=R/f'WHEN_THE_SKY_CLEARS_REFINEMENT_{v}.txt'
guide.write_text(f'''WHEN THE SKY CLEARS - {v} WORKING REFINEMENT
Current state: the full 4K world/layout trailer remains v040 and is unfinished.
This retained refinement is a separate five-second unmasked battlefield shot.

EDITABLE BLENDER:
{media['native']['path']}
World scene: {build['world_scene']}
Review movie scene: {build['master_scene']}
Frames1801-1920,24fps,3840x2160 at100percent.

ACTUAL NATIVE 4K MOVIE:
{media['movie4K']['path']}

SMALL VIEWING COPY (downsampled from the actual 4K movie):
{media['view1080p']['path']}

RETAINED CHANGES:
{build['scope']}
The original acting/camera/root/feet/event-light clock is preserved.
No new gait or full-trailer propagation in this pass.
Visible painting is carried by editable native mesh contours and packed images;
real native Grease Pencil contour guides are retained as hidden editing layers.
Native output is4K. Original generated source paintings are measured below4K.

VERIFICATION:
Saved/reopened native source; preserved source hashes and relevant stage values.
All120 movie frames decoded; native4K/24fps/five seconds and supplied music checked.
Reviewed native-pixel keys and chronological decoded frame samples.
This is not a claim of continuous-speed playback inspection or artistic acceptance.

REMAINING:
Torso/cuff construction, weight/acting, turn drawing continuity, meaningful hand
contact, main impact and persistent ground response; then world-detail work on
village/woods/school/camp, with the children held, and final title-mask composition.
See notes/improvement_v048/next_world_priorities.json.
All prior native files and source artwork remain preserved.
''',encoding='utf-8')
print('V048_CHECKPOINT_RECORDED',v,str(guide))
