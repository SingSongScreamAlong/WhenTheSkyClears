import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
qa=json.loads((R/'notes/world_v016/movie_verification_v027.json').read_text())
native=json.loads((R/'notes/world_v016/native_motion_audit_v027.json').read_text())
completed=json.loads((R/'notes/world_v016/native_completed_v027.json').read_text())
assert qa['frames']==2400 and qa['duration_seconds']==100 and qa['resolution']==[3840,2160]
assert qa['source_sha256']==native['source_sha256']==completed['source_sha256']
source=Path(qa['source']);movie=Path(qa['movie'])
portable=json.loads((R/'notes/world_v016/portable_reopen_v029.json').read_text())
editable=Path(portable['editable'])
assert portable['world_samples_identical_to_v027'] and portable['native_audio_export_checked']['native_master_audio_present']
assert hashlib.sha256(editable.read_bytes()).hexdigest()==portable['editable_sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest()==qa['source_sha256']
assert hashlib.sha256(movie.read_bytes()).hexdigest()==qa['movie_sha256']
assets=[]
for p in [R/'characters/Pair_Painterly_Near_Age_v015.png',R/'characters/Pair_Painterly_Near_Age_Vector_v015.json',R/'sets/village_lookdev/v014/Bakery_Detail_Repaint.png',R/'sets/village_lookdev/v014/Path_Detail_Repaint.png',R/'sets/fx/Painted_Smoke_Wisp_v016.png',R/'sets/world_v026/Countryside_Continuous_Panorama.png']:
    assets.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest={'project':'When the Sky Clears','stage':'Painted animated world development pass','movie':movie.relative_to(R).as_posix(),'source':source.relative_to(R).as_posix(),'movie_sha256':qa['movie_sha256'],'source_sha256':qa['source_sha256'],'output':{'resolution':[3840,2160],'fps':24,'frames':2400,'duration_s':100,'audio':'Supplied WAV, AAC 48 kHz stereo, fade 90-100s','picture_fade':'98-100s, black last frame verified'},'preview':'renders/world_v016/WTSC_Motion_Excerpts_1080p_v027.mp4','preview_scope':'1920x1080,24fps,12s: timeline0-8s and30-34s, actual native scene motion','important_assets':assets,'paint_sources':{'most_base_images':[1672,941],'bakery_repaint':[1356,1159],'path_repaint':[1908,824],'near_age_children':[1672,941],'smoke':[1024,1536],'continuous_panorama':[1983,793]},'children':'Held native GP vector drawing with vector-clipped painterly fill; slightly taller boy; object translation only','world':'2.5D painted sets at distinct native depths, rooted canopy/cloth/grass shape keys, localized light/shadow shaders, anchored smoke, drifting leaves/paper/ash/mist, actual extruded 3D title','motion_feedback_resolved':['Original oak was split across two depths: now whole oak/roots/fence/path share one surface','Rear countryside followed camera: replaced with stationary continuous world panorama','Nearly same-size duplicate woods: distant row smaller, different whole foreground tree asset','Smoke base translation: origins fixed at emitters','Opaque lower strip: continuous native painted ground with irregular feathered joins'],'evidence':['notes/world_v016/layer_motion_diagnosis_v019.json','notes/world_v016/attachment_corrections_v025.json','notes/world_v016/native_motion_audit_v027.json','notes/world_v016/movie_verification_v027.json','notes/world_v016/prior_source_preservation_v027.json'],'prompt_files':['notes/village_lookdev/imagegen_prompts_v014.json','notes/village_lookdev/character_imagegen_prompts_v015.json','notes/world_v016/smoke_imagegen_prompt.txt','notes/world_v016/panorama_imagegen_prompt_v026.txt'],'limitations':['Character gait, performance and interaction remain deliberately held for this world pass','Architecture primarily painted depth cards, not modeled 3D buildings','Source paintings have lower raster resolution than UHD output','Exact older approved ink-and-wash image remains missing; current direction is liked, not final art/motion approval','Not a claim of Arcane-level finish']}
manifest.update({'editable_source':editable.relative_to(R).as_posix(),'editable_sha256':portable['editable_sha256'],'editable_visual_change':False,'native_edit_scene':portable['world_scene'],'native_export_scene':portable['master_scene'],'music_packed_in_editable':True,'native_audio_export_verified':True,'portable_reopen_evidence':'notes/world_v016/portable_reopen_v029.json','paint_provenance':'Raster paint assets generated through GPT imagegen. Native GP, mesh/vector FX and title geometry authored in Blender. Title uses the packed local Arial Black font.','observed_review_note':'Foreground foliage briefly partially occludes the held children in the woods; final art/motion still needs review.'})
(R/'notes/world_v016/delivery_manifest_v027.json').write_text(json.dumps(manifest,indent=2))
guide=f'''WHEN THE SKY CLEARS - PAINTED WORLD PASS v027

MOVIE: {movie}
BLENDER EDITABLE: {editable}
EXACT MOVIE RENDER SOURCE: {source}
MOVING EXCERPTS: {R/'renders/world_v016/WTSC_Motion_Excerpts_1080p_v027.mp4'}

Native 3840 x 2160 UHD, 24 fps, 2400 frames, exactly 100 seconds.
All 2400 output frames decoded successfully. Resolution, rate, duration,
48 kHz stereo music, render-section joins, final 10-second audio fade and
final two-second picture fade verified. The last frame is black.
Representative actual movie frames are under renders/world_v016/decoded_review_v027.

The complete route passes through warm village, abandoned village/woods,
school, camp, battlefield and monumental title. Native scene geometry,
materials, texture files, GP drawing, shape keys, drivers and camera keys
remain editable. Packed image assets are also retained under sets/.
The supplied music is referenced relatively under edit/.
In the portable v029 file it is also packed. Edit the world in
WTSC_WORLD_EDIT_v029. Select WTSC_MASTER_4K_100S_v029 for native picture+music
export; its actual Scene strip and packed WAV were reopened and checked,
including a non-silent native audio export and the final volume fade.
v029 changes packaging/export setup; its sampled world/camera/GP state is
identical to the exact v027 movie render source.

This continues the painterly direction Conrad liked. The children are near
the same age/height, with the boy slightly taller, near-black painted detail
and tiny off-white eye marks. They remain in one held pose as specifically
requested for this world pass. Only their root travel moves. Gait and acting
still need the separately planned 3D-motion-reference/vector workflow.

Motion corrections after the v019 preview:
- One opening oak/roots/fence/path surface replaces the split-depth tree.
- A newly painted continuous countryside panorama stays fixed at real depth.
  Only the sky area drifts with cloud wind; land does not follow the camera.
- Far woods are smaller than the near row. Whole isolated foreground trees
  replace cropped strips of the same forest painting.
- Smoke origins stay at chimneys/fire emitters. Facades and roofs remain rigid.
- Registered bakery/path paint remains on its owning mesh UVs.
- Continuous painted earth and small native alpha feathers remove the opaque
  lower strip edge and blend regional roots into the path.

Most set/character base paintings are 1672 x 941. The new panorama is 1983 x 793,
smoke 1024 x 1536, bakery detail 1356 x 1159, path detail 1908 x 824. Output is
native UHD; this does not turn those into native UHD source paintings.
Buildings are primarily 2.5D painted cards; the extruded title is actual 3D.

Current direction is liked, but technical verification is not artistic approval.
The exact older approved ink-and-wash reference remains unavailable. This is a
world-animation development pass; no Arcane-level finish or complete character
performance is claimed.

Earlier v010 source/movie and v013 source/inspection files remain hash verified.
The live editable v011 already differed from the older preservation baseline;
its existing .blend1 preserves the original hash. Neither was restored or edited
by this continuation. Intermediate versions remain available. The incomplete
v019 render was stopped after motion feedback; use only the v027 final movie.

See notes/world_v016/delivery_manifest_v027.json for source hashes, exact scope,
asset provenance, motion diagnosis, prompt paths and verification receipts.
'''
(R/'WHEN_THE_SKY_CLEARS_WORLD_v027.txt').write_text(guide,encoding='utf-8')
print('PAINTED_WORLD_DELIVERY_VERIFIED',json.dumps({'movie':str(movie),'source':str(source),'manifest':str(R/'notes/world_v016/delivery_manifest_v027.json'),'frames':2400,'duration_s':100}),flush=True)
