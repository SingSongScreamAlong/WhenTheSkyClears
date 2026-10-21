import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'shots/world/WTSC_Living_World_v010.blend'
editable=ROOT/'shots/world/WTSC_Living_World_Editable_v011.blend'
movie=ROOT/'renders/living_world/WTSC_Living_World_4K_v010.mp4'
native=json.loads((ROOT/'notes/living_world/native_reopen_v010.json').read_text())
editcheck=json.loads((ROOT/'notes/living_world/native_reopen_v011.json').read_text())
qa=json.loads((ROOT/'notes/living_world/movie_verification_v010.json').read_text())
assert Path(qa['path'])==movie and qa['decoded_frames']==2400 and qa['duration_seconds']==100
assert qa['sha256']==hashlib.sha256(movie.read_bytes()).hexdigest()
assert native['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert editcheck['source_sha256']==hashlib.sha256(editable.read_bytes()).hexdigest()
paint=[]
for path in sorted((ROOT/'sets/surface_paint').glob('*.png')):
    paint.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
manifest={'project':'When the Sky Clears','stage':'Dimensional environment and ambient motion iteration',
    'source':editable.relative_to(ROOT).as_posix(),'source_sha256':editcheck['source_sha256'],
    'movie_render_source':source.relative_to(ROOT).as_posix(),'movie_render_source_sha256':native['source_sha256'],
    'movie':movie.relative_to(ROOT).as_posix(),'movie_sha256':qa['sha256'],
    'output':{'resolution':[3840,2160],'fps':24,'duration_seconds':100,'decoded_frames':2400},
    'new_paint':paint,'packed_images':native['packed_images'],'music_packed_sha256':native['audio_packed_sha256'],
    'mesh_and_curve_evidence':['notes/living_world/native_reopen_v010.json','notes/living_world/native_reopen_v011.json'],
    'editable_asset_roots':len(editcheck['asset_roots']),
    'native_mesh_receipts':['notes/living_world/typed_mesh_creation_v008.jsonl','notes/living_world/typed_details_v009.jsonl'],
    'imagegen_prompt_files':['notes/living_world/reuse_and_paint_sources.json','notes/living_world/organic_paint_prompt.json'],
    'character_animation':'Held native GP pair; position animation only. Reference-guided gait and acting remain deferred.',
    'visual_scope':'Real near architecture, roofs, branch curves, terrain, props, tents, classroom and ruins; painted foliage on branches and distant matte layers.',
    'review_status':'Full technical export verified; artistic quality and final character performance are not approved.'}
(ROOT/'notes/living_world/asset_manifest_v010.json').write_text(json.dumps(manifest,indent=2))
guide='''WHEN THE SKY CLEARS - DIMENSIONAL LIVING WORLD
16 October 2026

MOVIE: renders/living_world/WTSC_Living_World_4K_v010.mp4
BLENDER: shots/world/WTSC_Living_World_Editable_v011.blend
EXACT MOVIE SOURCE: shots/world/WTSC_Living_World_v010.blend

100 seconds, 3840 x 2160 UHD, 24 fps. Complete video decoding verified all 2400
frames, the supplied music and its final fade, the black final frame and the
boundaries between the native render sections.

This rebuild replaces the near image facades with original native 3D sets:
thick walls and actual openings, individually curved roof tiles, branching
trees, worn terrain, village props and planters, a damaged classroom and bell,
tent shelters with interiors and camp props, ruins, wire and physical title.
Painted foliage clusters are arranged on native branches. Distant sky, hills
and ruined street remain matte paintings. The result is a hybrid dimensional
world, with the continuous lateral village/woods/school/camp/battlefield route.

Animated ambience includes branches and canopy, grass, washing, tent canvas,
moving water normals, three-dimensional smoke, chimney smoke, birds, papers,
slow sky drift and changing light. Cloth attachment points remain anchored.
These are native editable shape keys, drivers and keys; no external simulation
handler is needed. The Shader to RGB paint materials target EEVEE; keep that
render engine for the intended material appearance.

The children remain a held editable Grease Pencil drawing, translated as a unit.
The rejected segmented mannequin gait is excluded. Character movement and acting
still need the actual animated 3D reference behind editable vector silhouettes,
following the user's direction. Environment-first review remains the priority.

Open the WORLD scene to edit the numbered set collections, particularly
20 | LIVING WORLD dimensional sets. v011 provides 40 individual ASSET roots for
buildings, trees, tents and ruins. Select a root to move its full set piece;
children retain their material parts, geometry and wind controls. The source
geometry was regrouped while preserving world positions, UVs, colors and motion.
The exact v010 movie source is also preserved. Per-object foliage sorting can
differ after regrouping, so the v011 project still needs artistic review.
Select WTSC_MASTER_4K_100S for the complete
native Scene/Sound edit and movie rendering. Both images and source music are
packed. The song fades over 90-100 seconds; picture fades over 98-100 seconds.

New original surface paintings were made with built-in GPT imagegen and saved
unchanged in sets/surface_paint. Exact prompts and provenance are in
notes/living_world/reuse_and_paint_sources.json and organic_paint_prompt.json.
Original texture resolutions are lower than UHD. The movie is natively rendered
at 3840 x 2160; no image scaling or generated intermediate frames were used.

The previous v006 concept is preserved. v007-v009 are development iterations,
including construction issues corrected in later versions. This is a substantial
environment production pass for review, not final artistic approval or a fully
animated character trailer. Further environment refinement can follow review.
'''
(ROOT/'LIVING_WORLD_START_HERE.txt').write_text(guide,encoding='utf-8')
old=ROOT/'WORLD_REVIEW_START_HERE.txt';archive=ROOT/'notes/WORLD_REVIEW_START_HERE_v006.txt'
if old.exists() and not archive.exists():archive.write_bytes(old.read_bytes())
old.write_text(guide,encoding='utf-8')
for name in ['WORLD_STATUS.txt','PRODUCTION_STATUS.txt']:
    p=ROOT/'notes'/name;backup=ROOT/'notes'/(p.stem+'_v006.txt')
    if p.exists() and not backup.exists():backup.write_bytes(p.read_bytes())
    p.write_text(guide,encoding='utf-8')
previous=json.loads((ROOT/'notes/world_asset_manifest.json').read_text())
previous.update(native_project=manifest['source'],review_movie=manifest['movie'],native_project_sha256=manifest['source_sha256'],review_movie_sha256=manifest['movie_sha256'],current_stage='Dimensional living environment v010; character performance deferred',latest_manifest='notes/living_world/asset_manifest_v010.json')
(ROOT/'notes/world_asset_manifest.json').write_text(json.dumps(previous,indent=2))
print(json.dumps({'source':str(editable),'movie_source':str(source),'movie':str(movie),'guide':str(ROOT/'LIVING_WORLD_START_HERE.txt'),'status':'Technical delivery verified; visual review pending'}))
