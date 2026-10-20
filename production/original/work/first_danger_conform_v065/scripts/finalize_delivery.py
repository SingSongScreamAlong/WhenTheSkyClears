import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
load=lambda name:json.loads((O/'evidence'/name).read_text())
delivery=load('DELIVERY.json');build=load('BUILD.json');cold=load('COLD_NATIVE_VALIDATION.json');edit=load('NATIVE_EDIT_PIXEL_AGREEMENT.json');witness=load('LIVE_NATIVE_CACHE_AGREEMENT.json')
assert cold['all_checks_pass'] and cold['native_sha256']==build['native_sha256']
assert edit['all_within_one_RGB_code_value'] and witness['maximum_RGB_error']<=8 and witness['mean_RGB_error']<.05
assert witness['native_sha256']==build['native_sha256']
assert edit['native_sha256']==build['native_sha256']
assert delivery['all_movies_fully_decoded'] and delivery['video_timestamps_contiguous']
assert delivery['native_sha256']==build['native_sha256']
assert hashlib.sha256(Path(build['source']).read_bytes()).hexdigest()==build['source_sha256']
assert hashlib.sha256(Path(build['native']).read_bytes()).hexdigest()==build['native_sha256']
assert hashlib.sha256(Path(build['world_render_native']).read_bytes()).hexdigest()==build['world_render_native_sha256']
fraction=delivery['title_visibility']['minimum_original_mask_actor_fraction']
clipnames=[Path(x['path']).name for x in delivery['clips']]
text=f'''WHEN THE SKY CLEARS | FIRST-DANGER PASS v065f
19 October 2026 | Rendered shot candidate

ACTUAL RESULT
previews/WTSC_First_Danger_Title_v065f_View.mp4
Small 720p viewing copy, downsampled from the actual UHD movie.

previews/WTSC_First_Danger_Title_v065f_4K.mp4
Actual 3840x2160 / 24fps / 168 frames / seven seconds.

previews/WTSC_First_Danger_Unmasked_v065_4K.mp4
The same actual UHD world without the title mask, with original audio.

previews/WTSC_First_Danger_World_and_Title_v065f_Review.mp4
Labeled side-by-side comparison, normal 24fps timing, original supplied music.

previews/Title_Visibility_Before_After_v065.jpg
Matched native keys: inherited mask versus the new readable drawing reveal.

EDITABLE NATIVE
native/WTSC_First_Danger_Conformed_v065f.blend
Main editable/render scene: WTSC_FIRST_DANGER_WORLD_v065
Scene/Sound review master: WTSC_FIRST_DANGER_REVIEW_MASTER_v065
Global frames 913-1080 / 38-45 seconds. The developed core remains G937-1056,
39-44 seconds, with one second of neighboring movement on each side.
Native source settings remain UHD. All source painting images are packed.

COLOR
World, compositor and native edit/master use Standard/None, exposure0/gamma1.
The shared palette follows the current full-cut absolute 0-96-second smoothstep,
with no shot reset. Driver time is an explicit world-scene dependency. The world
owns the compositor, avoiding the stale cross-scene driver state caught in the
first pilot. Every movie-frame record checks both controller and actor-material
values against global time after the actual world render.
The title reveal mixes to the ORIGINAL painted world pixels via the visible
drawing matte, avoiding alpha-over brightening of translucent paint.

CAMERA CONTINUITY
The route matches the old route through G913, eases over one second into the
actual .73125m/s walk, tracks that pace through the core, and eases back over
the outgoing second. A persistent {build['camera_route']['downstream_offset_m']:.6f}m offset then carries through
the rest of the supplied full camera action. The core step error is below
{cold['core_camera_step_max_error_m']:.9f}m/frame in the independent cold check.
This is a continuous NEW route. Old downstream movie pixels must be rerendered
with it; do not cut this directly into an unchanged v040/v064 export.
The root travel, original gait, baked girl phase lead and body/foot actions were
not edited. Existing evaluated boot positions match source exactly across
{cold['boot_frame_samples']} representative integer/fractional samples. Contact marks were regenerated
from those boots to cover the two neighboring handles.

TITLE VISIBILITY AND THE ARTWORK
The original title font geometry, wording and scroll remain. The world stays
inside those letters; a native visible-object Cryptomatte reveals the children
in front of the letter mask. It follows the ACTUALLY VISIBLE drawing contribution,
and the exact rendered alpha of the nearer oak suppresses the reveal where it
occludes a child. The girl naturally passes behind that tree in the outgoing
handle; the tree is not shown in the shape of her silhouette.
At the worst sampled movie frame, the inherited mask retained only
{100*fraction:.2f}% of the visible opaque drawing pixels. The new reveal retains their
original color within one RGB code value in every rendered frame check.
Geometry, original mesh UVs, packed artwork and rest bones are preserved.
The existing layered 2D/2.5D paintings remain the visible art; no volumetric forest,
3D character replacement, new costume or new raster painting was introduced.
To inspect the raw world, disable Compositing on the main world scene or use
its live unmasked File Output. The inherited helper edit's older name is historical.

ACTUAL RENDER / COMPOSITE PROVENANCE
The world/glyph/visible-drawing passes were freshly rendered at UHD from the
frozen v065d native. v065f adds the precise foreground-occlusion pass and the
final drawing-reveal operation. The oak alpha was also rendered natively at UHD.
Blender then composited those unchanged native UHD pixel caches using the same
color-exact reveal graph as the editable v065f scene. No image scaling or frame
interpolation was used for the UHD movies. A separate fresh live-v065f UHD key
at G{witness['frame']} agrees with the cache composite within {witness['maximum_RGB_error']} RGB code values (mean error
{witness['mean_RGB_error']:.6f}/255). The cache inputs and each result are hashed.
The 720p clip and labeled side-by-side copy are viewing derivatives.

NATIVE AND MEDIA READBACK
All independent cold preservation checks pass. Direct native and native
Scene-strip master renders at G937 and G1056 agree within one RGB code value.
All four movies fully decode all168frames with contiguous24fps timestamps.
The soundtrack is the actual supplied WAV excerpt38-45s; decoded comparison
correlation is {delivery['audio']['correlation_to_original']:.6f}. No new SFX or unrelated music source was added.
All earlier sources, including the concurrent v064 full-cut work, are preserved.

SCOPE
This is the first-danger color/camera/title pass, with the existing gesture.
It is not a new full-film export or new story acting/gaze/cloth production pass.
The new title layering is a reviewable composition candidate, not an assertion
of final artistic acceptance. Agents inspected actual native keys and decoded
chronological frames; continuous native-player artistic playback is not claimed.

REPRODUCTION
The scripts are project-local and resolve the original project root. For a new
revision, duplicate/version the candidate folder before changing it. The build
and small correction scripts retain the exact construction history. Render jobs
take explicit frame ranges, freeze native source hashes and verify actual clock,
material, output and completion records. Never replay a partial range without
checking its completed-frame/hash record.
The raw UHD caches remain in renders/ for the verified final composite; the
editable native contains the live graph and can render directly without caches.

RECORDS
evidence/BUILD.json
evidence/COLD_NATIVE_VALIDATION.json
evidence/RENDER_MOVIE_COMPLETE.json
evidence/FINAL_COMPOSITE_COMPLETE.json
evidence/NATIVE_EDIT_RENDER.json
evidence/NATIVE_EDIT_PIXEL_AGREEMENT.json
evidence/LIVE_NATIVE_WITNESS.json
evidence/LIVE_NATIVE_CACHE_AGREEMENT.json
evidence/DELIVERY.json

Native SHA256: {build['native_sha256']}
Original v063 SHA256: {build['source_sha256']}
Render recovery: two long world workers hit an access violation in the Blender
GPU/Grease Pencil volume draw path. All87completed UHD frames were hash/PNG
verified; the remaining81used six new nonoverlapping batches of at most16frames.
No uncertain mutation was replayed. See evidence/RENDER_RECOVERY.json.
'''
(O/'START_HERE_v065.txt').write_text(text,encoding='utf-8')
(R/'WHEN_THE_SKY_CLEARS_FIRST_DANGER_v065.txt').write_text('WHEN THE SKY CLEARS | FIRST-DANGER PASS v065e\n\nOPEN\nwork/first_danger_conform_v065/START_HERE_v065.txt\n\nACTUAL RENDER\nwork/first_danger_conform_v065/previews/WTSC_First_Danger_Title_v065_View.mp4\nwork/first_danger_conform_v065/previews/WTSC_First_Danger_Title_v065_4K.mp4\n\nEDITABLE NATIVE\nwork/first_danger_conform_v065/native/WTSC_First_Danger_Conformed_v065e.blend\n\nSeven seconds, global38-45s,24fps, with actual UHD rendering. Color pipeline and live clock corrected; continuous camera route with neighboring handles; children remain readable through the title via their original visible drawing layer. Established layered artwork preserved. The full film has not been re-exported.\n',encoding='utf-8')
pointer=R/'WHEN_THE_SKY_CLEARS_FIRST_DANGER_v065.txt';pointer.write_text(pointer.read_text(encoding='utf-8').replace('v065e','v065f').replace('Title_v065_','Title_v065f_'),encoding='utf-8')
print('FIRST_DANGER_DELIVERY_FINALIZED',json.dumps({'native':build['native'],'movies':clipnames,'source_preserved':True}),flush=True)
