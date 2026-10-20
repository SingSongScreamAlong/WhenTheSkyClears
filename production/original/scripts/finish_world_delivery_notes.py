"""Publish local delivery pointers only after the corrected movie passes QA."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
movie=root/'renders/world/WTSC_World_Atmosphere_4K_v006.mp4'
source=root/'shots/world/WTSC_World_First_v006.blend'
qa=json.loads((root/'notes/world_movie_verification_v006.json').read_text())
native=json.loads((root/'notes/world_native_reopen_verification.json').read_text())
assert Path(qa['path'])==movie and qa['decoded_frames']==2400 and qa['duration_seconds']==100
assert Path(native['source_path'])==source and native['audio']['packed']
assert qa['sha256']==hashlib.sha256(movie.read_bytes()).hexdigest()
status=(root/'notes/WORLD_STATUS.txt').read_text(encoding='utf-8')
status=status.replace('shots/world/WTSC_World_First_v004.blend','shots/world/WTSC_World_First_v006.blend')
status=status.replace('Their files are preserved unchanged and packed in Blender.','Their files are preserved unchanged and packed in Blender. The two battlefield materials use alpha blending to remove the black overlap artifacts discovered in the v004 export.')
status=status.replace('notes/world_render_workers.json identifies the four disjoint native render workers and immutable source hash.','notes/world_render_workers.json records the original native render. notes/world_render_workers_v006.json records the corrected native frames 1081-2400. Frames 1-1080 are retained from the original native render; native camera projection confirms neither repaired plane can enter before frame 1143. The retained prefix was encoded again at high quality, with no scaling or interpolation.')
status=status.replace('The final video verification and decoded review frames are written after rendering.','The corrected movie is renders/world/WTSC_World_Atmosphere_4K_v006.mp4. It passed complete decoding: 2400 frames, 3840 x 2160, 24 fps, exactly 100 seconds, audible supplied music with a 90-100 second fade, and a fully black last frame. Render-section boundaries passed adjacent-frame checks. See notes/world_movie_verification_v006.json and renders/world/decoded_review_v006/. Artistic approval remains pending.')
for name in ['WORLD_STATUS.txt','PRODUCTION_STATUS.txt']:(root/'notes'/name).write_text(status,encoding='utf-8')
manifest=json.loads((root/'notes/world_asset_manifest.json').read_text())
manifest['review_movie']=str(movie.relative_to(root)).replace('\\','/')
manifest['review_movie_sha256']=qa['sha256']
manifest['native_project_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
manifest['technical_verification']='notes/world_movie_verification_v006.json and notes/world_native_reopen_verification.json'
(root/'notes/world_asset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
guide='''WHEN THE SKY CLEARS - WORLD AND ATMOSPHERE REVIEW

Review movie: renders/world/WTSC_World_Atmosphere_4K_v006.mp4
Editable Blender project: shots/world/WTSC_World_First_v006.blend

100 seconds, 3840 x 2160 UHD, 24 fps. Music is the supplied 100-second WAV.
The movie scrolls through the warm and abandoned village, woods, school, camp,
battlefield, ash and monumental physical title. The children hold a single
Grease Pencil pose and translate together. Character performance is deferred.

The project opens on the WORLD scene camera. The numbered collections contain
the separate sets, ground, foreground, static vector pair and camera. Scrub the
timeline to review the route. Painting materials and their source images remain
editable. All paintings and the source WAV are packed in the blend.

Select WTSC_MASTER_4K_100S in Blender's Scene menu for the complete native movie
timeline and sound. Render Animation from that scene for picture plus music.
WORLD uses PNG still output; MASTER uses UHD H264/AAC movie output.

Review focus: world atmosphere, progression from warmth to loss, readable places,
camera geography, layer transitions, silhouette visibility and title reveal.
This is a provisional environment pass. It does not establish artistic approval
or finished trailer quality. Original imagegen paintings are about 1672 x 941 or
1536 x 1024; the output movie is rendered at UHD. No upscaling claim is made for
the original paintings.

Ten set paintings and the held-pair design were generated with the built-in GPT
imagegen tool. Exact prompts: notes/imagegen_world_prompts.json.
Source paintings: sets/painted_layers/. Pair vector source: characters/.
Complete status and evidence: notes/WORLD_STATUS.txt and the JSON reports.

The v004 movie is superseded: its battlefield transparency caused black artifacts.
The v006 source/movie correct that native material issue. Earlier character gait
experiments remain rejected and are not used in this world project.
'''
(root/'WORLD_REVIEW_START_HERE.txt').write_text(guide,encoding='utf-8')
print(json.dumps({'source':str(source),'movie':str(movie),'status':'local delivery notes complete; artistic review pending'}))
