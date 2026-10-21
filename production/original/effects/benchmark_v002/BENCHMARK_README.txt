WHEN THE SKY CLEARS - ONE-SHOT FX BENCHMARK v002
Status: artistic benchmark for review. Not artistically accepted.
V001 is preserved only as a rejected technical import prototype.

WHAT TO REVIEW
previews/WTSC_Explosion_Benchmark_4K_v002.png - actual3840x2160 shot still.
previews/WTSC_Explosion_Benchmark_4K_1to1_Detail_v002.png - unscaled pixel crop.
WTSC_Explosion_Motion_Proof_1080_v002a.mp4 - four-second,24fps motion proof.
No thumbnail grid represents the quality claim; judge the shot and moving clip.

SCENE AND ART
The background is the actual v038 project world at frame1825, using its existing
camera, children, scenery, floor and foreground. Production files were loaded
read-only. The working scene copies are confined to effects/benchmark_v002.
For this effects evaluation the camera, characters and environment are HELD.
It is not a locomotion test or finished moving-trailer integration.

The eruption uses original built-in GPT imagegen paint (hero1254x1254; unique
ground dust2172x724), native subdivided root-pinned mesh deformation, small UV
advection, temporal cooling, rough solid3D debris with individual trajectories,
and a short physical light pulse. It is a detailed2.5D painted-flow approach,
not a3D fluid simulation. Source image alpha is packed and marked Straight.
The4K canvas does not mean the individual texture was generated at4K.

The first4K scene render uses native foreground holdouts and live local paint
receiver materials. The efficient1080p motion proof captures the foreground
alpha and spatial receiver response once for the held camera, then animates the
native effects behind that mask. Receiver intensity follows the same source
age/flicker as the explosion. The light is local to receiving paint; it does not
alter architecture alpha, add a full-frame orange wash, or fade buildings.
This optimization is specific to a static-camera benchmark. A moving production
camera requires live geometry occlusion/receiver evaluation or matching per-frame
passes. The held proof does not establish that broader integration has passed.

NATIVE FILES
native/WTSC_FX_GPU_Preview_v002.blend is the current efficient1080p preview.
native/WTSC_FX_Shot_Proof_v002a.blend is the separate full benchmark project copy.
Its FX_SHOT_PROOF scene retains live native foreground/receiver setup for4K
reference stills. The ignition crop edge is feathered in the revised version.
native/WTSC_Hero_Eruption_Collection_v002a.blend contains the editable standalone
FX collection and packed generated dependencies. Append its collection into the
world scene for further art adaptation. It does not modify receiving production
materials automatically. Receiver setup remains in the isolated shot copy.
native/WTSC_Real_World_FX_Benchmark_v002.blend is the earlier build intermediate,
preserved for history; prefer Shot_Proof for the revised debris and light setup.

CONTROL AND TIMING
Move the fixed ground-origin empty for placement; children stay parented.
start_frame is1813 in this benchmark; speed1; intensity0.94; wind0.16; size1.
The appendable collection's size property now drives uniform native root scale.
It was tested at1.2 in a fresh sandbox with start_frame10 and origin[0,0,0].
The older full-shot authoring copy predates that size-property connection;
use the appendable collection for the current reusable controls.
The benchmark frames are1795-1890 at24fps; first ignition1813; hero1825.
X is screen-right, Z up, positiveY depth; the camera looks along+Y.
Units are metres. The fixed emitter is[109.1,10,-0.7048803] in this source shot.
New placement requires rebinding the local receiver positions; the baked proof
light/occlusion maps are only for this held camera/emitter arrangement.
For Blender File > Append, choose WTSC_Hero_Eruption_Collection_v002a.blend,
then Collection > FXv002 | Detailed painterly ground eruption. Select
FXv002 | fixed ground origin and controls. Move that empty to a new contact
point; edit start_frame, speed, intensity, wind and size in Custom Properties.
age is computed and should not be edited. Keep positive speed and size.
Palette changes remain native shader edits: detailed soot material's tone
Multiply color, granular dust tone color, and physical core light's color.
There is no single unified color control in this benchmark.
Use24fps. X is horizontal, Z is up, camera looks along positiveY; effects lie
primarily in theXZ plane. The default plume is about3.1metres high/wide.
Source PNG assets use Straight alpha; native render compositing is premultiplied.
The viewing MP4 is opaque H.264 BT.709. No transparent animation sequence is
claimed here. Native_Append_Test_RGBA_v002a.png is a single sandbox RGBA still.
Do not use held-scene receiver or foreground maps at a new camera/placement.

QUALITY LIMITS
High-detail still form does not establish convincing motion. Judge rise timing,
internal flow, debris weight, contact, occlusion, source-linked local light and
whether the texture/contrast fit the existing charcoal paint. The current
surface-flow approach cannot offer arbitrary camera movement or true volumetric
self-shadow evolution. If the motion reads like stretching a painted cutout,
that is a failed artistic benchmark, even if its drivers and import are valid.
Exported-frame audit found that the late smoke retains the same main lobe
structure and too much painted core glow. Those are unresolved art limitations.
The native append test validates packed dependencies, timing, size and anchoring;
it does not resolve that motion limitation or establish artistic acceptance.
No DLSS or other upscaling claim is made. No paid assets or new software used.
After overnight reconnection the main render was verified complete and no other
Blender render was active. The completed preview used one bounded Eevee GPU job,
32samples and two CPU threads, with GPU compositing. Partial CPU frames are kept
separately; they were not mixed into the encoded GPU motion sequence.

evidence/ records source hashes, methods, rendering limits and actual media
measurements. Only one preview job was run at a time, with two CPU threads and
no shared UI or production worker interruption. GPU preview began only after
the production render was confirmed complete and no competing render was active.
