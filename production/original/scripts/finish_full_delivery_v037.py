import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
qa=json.loads((R/'notes/world_v016/full_verification_v037.json').read_text());editable=json.loads((R/'notes/world_v016/final_editable_v038.json').read_text());native=json.loads((R/'notes/world_v016/full_native_audit_v037.json').read_text());build=json.loads((R/'notes/world_v016/full_knockout_build_v037.json').read_text())
assert qa['full_decode_frames']==2544 and qa['total_seconds']==106 and qa['viewing_copy']['bytes']<20_000_000
assert hashlib.sha256(Path(editable['editable']).read_bytes()).hexdigest()==editable['editable_sha256']
assert hashlib.sha256(Path(qa['source']).read_bytes()).hexdigest()==qa['source_sha256']
asset=R/'sets/fx/v036/Painterly_Flame.png'
manifest={'project':'When the Sky Clears','delivery':'Complete106-second v037 CHECKPOINT; v039 lighting/contact benchmark and updated film remain in progress','movie':qa['movie'],'movie_bytes':qa['bytes'],'movie_sha256':qa['movie_sha256'],'chat_viewing_copy':qa['viewing_copy'],'editable':editable,'timing':{'fps':24,'resolution':[3840,2160],'total_frames':2544,'total_seconds':106,'moving_world_seconds':[0,100],'last_S_clear_seconds':100,'silent_credit_seconds':[100,106],'music_start':0,'music_fade_seconds':[90,100]},'exact_card_wording':['WHEN THE SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'],'picture_method':'All100seconds of the corrected world rendered fresh at native3840x2160, with nativeFontalpha rendered losslessly and composited into black. Native source provides equivalent direct compositor. No obsolete fading-world cache or repeated52–70excerpt.','environment_corrections':['7persistentregionalmaterialfadecurves removed; no building hide/alpha animation','Whole paintings spaced physically; slight depth separation prevents coplanar transitions','Continuous ground extended toX220; opaque panorama covers route keys and all linear interpolation','Static paint-edge masks blend layer boundaries spatially, no time-driven edge fades','4groundedfires withroot-pinnedflames,16newrootedsmokelayers,40embers,physicalpointlights andmatchinglocalpaintresponse','Existing15smokewisps reanchored/moved withtheirsets; grass/canopy/cloud/mist motion retained'],'children':'Held near-age painterly pair, slightly tallerboy; shared center .5/.5, existing local drawing/spacing untouched, whole-root route only. No gait.','asset_provenance':{'new_flame_asset':str(asset),'pixels':[1024,1536],'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'generator':'Built-in GPTimagegen, transparent_background=true','original_alpha_unchanged':True,'prompt_file':str(R/'notes/world_v016/flame_imagegen_prompt_v036.txt')},'fonts':'Installed ArialBlack/Impact/Arial; fsType8 inspected; source local. Rendered-video usage checked against Microsoft FontFAQ.','font_rights_source':'https://learn.microsoft.com/en-us/typography/fonts/font-faq','verification':'notes/world_v016/full_verification_v037.json','native_verification':'notes/world_v016/full_native_audit_v037.json','artist_review_scope':'Technical checkpoint QC complete; current painterly2.5D world with held characters. v039 polish benchmark and full updated movie still pending. No artistic acceptance or Arcane-level quality inferred.'}
(R/'notes/world_v016/full_delivery_manifest_v037.json').write_text(json.dumps(manifest,indent=2))
guide=f'''WHEN THE SKY CLEARS - FULL-FILM KNOCKOUT CHECKPOINT v037

This preserved checkpoint precedes the requested v039 five-second lighting,
grounding and paint/depth benchmark. The full updated-film task remains active.

READY:106seconds /1:46 /2544frames /24fps /3840x2160.

HIGH-QUALITY4K MOVIE
{qa['movie']}
{qa['bytes']:,}bytes
SHA256 {qa['movie_sha256']}

CHAT VIEWING COPY (under20,000,000bytes)
{qa['viewing_copy']['path']}
{qa['viewing_copy']['bytes']:,}bytes /1280x720 /24fps /AACstereo.
SHA256 {qa['viewing_copy']['sha256']}

EDITABLE LOCAL BLENDER MASTER
{editable['editable']}
Opens {editable['native_export_scene']}.
Edit world in WTSC_WORLD_CORRECTED_v037 and lettering/credits in
WTSC_FULL_FILM_KNOCKOUT_v037. Master contains actual Scene strip + suppliedWAV.
World/picture staging is identical to immutable render sourcev037. v038 only
sets native audio fade to exact100-second frame2401 boundary, packs local fonts,
and uses safe versioned export paths. No older source/movie is overwritten.
Immutable exact picture source: {qa['source']}

TIMING / WORDING
0.000-100.000: the complete village/woods/school/camp/battlefield/ruins journey
appears EXCLUSIVELY inside enormous slowly scrolling WHEN THE SKY CLEARS text.
Black everywhere outside glyphs. Native capink about99.5%height; roundovershoot
may crop at the top/bottom. Child pair stays centered with existing held poses.
99.958333: last moving frame with a small remaining fragment of the last S.
100.000: S clears; cut to6-second silent white-on-black credits card:

WHEN THE SKY CLEARS.
The Animated Series.
2027.
A Two Truck Productions project.

Title wraps WHEN THE /SKY CLEARS. for scale. Impact main title, Arial supporting
type, all uniform glyph proportions. Whole card uses97%frameheight; main lines
use96%width. Full wording remains readable, including every period/case.
105.958333: final frame starts. Exact file runtime106seconds.
Original supplied100s music starts0, fades90-100 once, then silence100-106.

WHAT CHANGED
Live native audit found7regional materials dissolving via animated alphaMath
multipliers. These and15regional smoke gates were removed. Original cutout alpha
and legitimate particle/light variation remain. Architecture now enters/exits
by spatial travel. Whole cards were spaced and depth-separated to avoid old
overlap/coplanar problems. Continuous ground extends toX220, covering the route.
Static edge masks repair rectangular paint seams without timed building fades.

4fires have pinned native flame meshes, anchored smoke, local embers, real point
lights and matching facade light response. Their contact heights were corrected
against the actual painted ground; hearthstones, flames, lights, smoke bases and
responsive-paint coordinates moved together. Existing canopy/cloth/grass, cloud
drift, mist and airborne paint motion remain. No character walk/acting added.

PICTURE / ASSET SCOPE
All100seconds of the world are NEW native4K renders of the corrected scene.
No cached old fading-world footage, no52-70loop, no output upscale or frame
interpolation. NativeFontalpha lossless mask plus fresh world matched the direct
native compositor exactly in the4K split-pipeline check. This is a2.5D painted
world with some3D effects/props. Most original paints1672x941, so native4K output
does not imply every source painting has4K texture detail.

New asset from BUILT-IN GPTimagegen, copied unchanged and packed in source:
{asset}
1024x1536RGBA, true alpha. Prompt/provenance:
{R/'notes/world_v016/flame_imagegen_prompt_v036.txt'}
All needed painting/audio/font data are packed for local authoring. Movies
delivered contain rendered pixels, no font files. Installed Windows font use in
rendered video checked against https://learn.microsoft.com/en-us/typography/fonts/font-faq
No dependency on unfinished assets from the separate reusable-effects-pack chat.

VERIFICATION
notes/world_v016/full_verification_v037.json
notes/world_v016/full_native_audit_v037.json
notes/world_v016/full_delivery_manifest_v037.json
Both movies decoded2544frames. Duration/frame rate/resolution/stereo checked.
Original audio timing/alignment and90-100fade verified, silent100-106 credits.
Black outside glyphs sampled across the movie; render joins and finalS/card cut
checked. Native audit:7persistent materials have0animated alpha paths, fixed
emitter roots with evaluated flame/light motion, constant held GP drawing hash,
centered pair and continuous underpaint coverage. Prior sources/movies hashed
unchanged. Actual decoded review frames live in renders/world_v016/full_decoded_v037.
Technical completion does not establish final artistic/performance approval.
'''
(R/'WHEN_THE_SKY_CLEARS_TRAILER_v037.txt').write_text(guide,encoding='utf8')
p=R/'notes/WORLD_CONTINUE_v037.txt';old=p.read_text();p.write_text('COMPLETED v037 FULL106s CHECKPOINT EXPORT. The v039 benchmark and full updated-film work remain active; see WORLD_CONTINUE_BENCHMARK_v039.txt. No v037 render jobs remain.\n\n'+old,encoding='utf8')
print('FULL_DELIVERY_MANIFEST_AND_GUIDE_READY',json.dumps({'movie':qa['movie'],'view':qa['viewing_copy'],'editable':editable['editable']}),flush=True)
