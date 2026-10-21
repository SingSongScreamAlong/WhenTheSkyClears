"""Write delivery records only after full movie QC and decoded visual review."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
qa=json.loads((R/'notes/world_v016/full_verification_v040.json').read_text());native=json.loads((R/'notes/world_v016/full_native_audit_v040.json').read_text());build=json.loads((R/'notes/world_v016/full_build_v040.json').read_text());review=json.loads((R/'notes/world_v016/full_visual_review_v040.json').read_text());benchmark=json.loads((R/'notes/world_v016/camp_comparison_completed_v039.json').read_text())
assert review['decoded_frames_inspected'] and qa['full_decode_frames']==2544 and qa['viewing_copy']['bytes']<20_000_000
assert hashlib.sha256(Path(qa['source']).read_bytes()).hexdigest()==qa['source_sha256']==native['source_sha256']
manifest={'project':'When the Sky Clears','delivery':'Updated106s painted-world trailer pass v040; held children','high_quality_4K_movie':{'path':qa['movie'],'bytes':qa['bytes'],'sha256':qa['movie_sha256'],'resolution':[3840,2160],'fps':24,'frames':2544},'chat_viewing_copy':qa['viewing_copy'],'editable':{'path':qa['source'],'sha256':qa['source_sha256'],'master_scene':native['master_scene'],'world_scene':native['world_scene'],'picture_scene':native['picture_scene'],'images_packed':native['used_images_packed'],'music_packed':native['music_packed'],'fonts_packed_and_signature_verified':True,'actual_scene_and_sound_strips':True},'comparison_first':benchmark,'timing':{'moving_world':[0,100],'silent_credits':[100,106],'single_original_music_start':0,'single_music_fade':[90,100]},'exact_credit_wording':['WHEN THE SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'],'changes':build['changes'],'preserved':'v037 checkpoint, v038 companion and all earlier sources/movies. Separate character motion and FX benchmark workstreams untouched.','v001_pack_used':False,'new_character_gait_added':False,'verification':'notes/world_v016/full_verification_v040.json','native_verification':'notes/world_v016/full_native_audit_v040.json','visual_review':'notes/world_v016/full_visual_review_v040.json','limitations':['Foreground plant repetition remains visible; treatment is partial rather than a full repaint.','Most source paintings remain1672x941; UHD native output does not create4K texture detail.','Current world uses2.5D layered paint plus native props/effects; not fully modeled architecture.','Held characters remain intentionally unanimated for this world pass.','Technical QC and decoded inspection do not establish human artistic approval or Arcane-level finish.']}
manifest['original_supplied_music_proof']=qa['original_supplied_music_proof']
(R/'notes/world_v016/full_delivery_manifest_v040.json').write_text(json.dumps(manifest,indent=2))
guide=f'''WHEN THE SKY CLEARS - UPDATED PAINTED WORLD TRAILER v040

3840x2160 /24fps /2544frames /106seconds.
Complete100-second moving world through the enormous scrolling title, then
6seconds of silent credits. Same held near-age charcoal pair; boy slightly taller.

4K MASTER
{qa['movie']}
{qa['bytes']:,}bytes
SHA256 {qa['movie_sha256']}

SMALL VIEWING COPY (720p, under20,000,000bytes)
{qa['viewing_copy']['path']}
{qa['viewing_copy']['bytes']:,}bytes
SHA256 {qa['viewing_copy']['sha256']}

EDITABLE BLENDER SOURCE
{qa['source']}
SHA256 {qa['source_sha256']}
Opens {native['master_scene']}, containing an actual Scene strip and suppliedWAV.
World: {native['world_scene']}
Native lettering/credits/compositor: {native['picture_scene']}
All used painting images, music and local authoring fonts are packed.
Default native output paths are versioned040. Prior versions stay preserved.

MATCHED FIVE-SECOND COMPARISON DELIVERED BEFORE PROPAGATION
{benchmark['comparison']}
Global64–69seconds, matched120frames, baseline left/study right,
unmasked world above/whole-film knockout below. Original music64–69 underneath.
Native4K study world and knockout files are beside the comparison.

REFINEMENT
The camp benchmark removed the broad orange canvas wash, retained painted folds,
connected localized receiving light and subtle charcoal contours to actual fixed
fire positions and flicker, softened measured shoe contacts, restrained the
existing production flame palette/glow, and kept smoke reset opacity atzero.
The demonstrated lighting/paint treatment now extends to school/battlefield/ruins
and the continuous ground. Original village warmth, depth layers, wind and held
pair staging remain. Camp grass correction stays local after regional proof review.
No rejected ink_wash_v001 assets and no untested new character motion were imported.

TIMING
0–100seconds: moving world appears only inside huge left-scrolling
WHEN THE SKY CLEARS lettering on black. LastS clears at100.
Original100sWAV starts0, fades90–100 once, then silence100–106.
100–106 exact card wording:
WHEN THE SKY CLEARS.
The Animated Series.
2027.
A Two Truck Productions project.

VERIFICATION
Both movies fully decoded2544frames. UHD/frame rate/duration/audio alignment,
singlefade/silentcredits, black outside native glyphs, render-block joins,
finalS/card boundary, exact wording, native-frame agreement and source hashes
were checked. Actual decoded movie samples were inspected after export.
Native audit compares glyph/credit and charactergeometry/topology/UV signatures
against038. It verifies all7regionalalpha paths are static,4fixedfire sources
with evaluated motion/coherent light, continuous underpaint coverage and pack data.
Every updatedWorldframe was freshly rendered at4K. Only the unchanged exact native
glyph alpha/credit pixels are reused from037, after native signature comparison.

KNOWN VISUAL LIMITS
This is the updated world pass with intentionally held children. Foreground plant
repetition remains visible; the bank treatment is partial. Most original painting
textures are1672x941. UHD output therefore does not imply4Ksourcepaint detail.
The scene uses layered2.5Dpaint with native props/effects. No human artistic
acceptance or Arcane-level finish is inferred from successful technical checks.

RECORDS
notes/world_v016/full_delivery_manifest_v040.json
notes/world_v016/full_verification_v040.json
notes/world_v016/full_native_audit_v040.json
notes/world_v016/full_visual_review_v040.json
'''
(R/'WHEN_THE_SKY_CLEARS_TRAILER_v040.txt').write_text(guide,encoding='utf8');print('FULL_V040_DELIVERY_RECORDS_READY',json.dumps({'movie':qa['movie'],'view':qa['viewing_copy']['path'],'editable':qa['source']}),flush=True)
