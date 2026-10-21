# Painted blast refinement v006

Review candidate for the held 75–80 second shot in *When The Sky Clears*. Blender 5.2.2 LTS, 24 fps, metric units with scale length 1. No gas simulation, cache or additional software is required. This is a five-second effects test; production lighting, character contact and the moving-camera integration remain production work.

## Native import

1. Append `native/WTSC_Painted_Blast_Assets_v006.blend` → Collection → `FXv006 | APPEND ASSETS | painted blasts impacts tracers`.
2. Keep the `MID`, `NEAR` or `FAR` layer collection you need. Each contains independent `BLAST` and `GROUND IMPACT` collections. Six independently timed tracer collections are also included.
3. Select the named `Blast controls` empty. Move that empty to a ground position. The cards face the project camera: X is screen horizontal, Z is up, the camera looks along +Y. Positive Y is farther from the camera. One native unit is one metre. Local origin is the fixed ground contact, not the sprite centre.
4. Set `start_frame`, `speed`, `size`, `intensity`, `smoke_density`, `wind`, `burst_spread`, `burst_rise`, `atmosphere`, `hot_frames` and `bloom_gain` on the empty. `age = (frame − start_frame) × speed`; speed 2 plays twice as fast. `smoke_color` is inherited by the painted materials. Root rotation and translation provide placement; internal drivers animate the children.
5. Move the matching `Ground impact controls` empty to the same contact and set its start, speed and size separately. The separation is deliberate: the crater/rim can remain after disabling or deleting the dynamic blast collection. `impact_visible`, `reveal_start` and `reveal_duration` control its reveal. It has **no end fade**.
6. For a tracer, edit the root transform, `start_frame`, `duration_frames`, `width` and `intensity`. Its saved `path_delta` records the authored trajectory; change direction with root rotation and travel length in the strip's native scale/location drivers. No collision or weapon ballistics are simulated.

The library has 133 objects, four packed source images, native material/shapekey drivers and no camera or lights. All driver targets belong to the appended collection. Appending into an empty factory scene, retiming, scaling, image packing, persistent ground and RGBA rendering were tested. Linked collections retain shared animation; editable Library Overrides were not tested. Prefer Append for shot-specific timing.

## Timing and appearance

The proof covers global frames **1800–1919** (five seconds at 24 fps). MID starts at 1824, NEAR at 1871, FAR at 1890. All thirteen smoke lobes are emitted in ages 0–5; their rapid expansion decelerates and their differing 62–125 frame lifetimes create breakup. Cold smoke continues to hang and drift. Hot emission and the light envelope end by age 10. Rough fragments follow authored rise/apex/fall arcs and remain at their landing positions. Three small landing puffs accompany each blast.

The NEAR and FAR labels denote relative depth/scale variations in this test fixture. The actual set has a mostly opaque battlefield card at Y=12: the far blast is at Y=11.5, **in front of that card**. Tracers at Y=14 are behind it. The far blast cannot honestly be described as threading behind every painted ruin without a new scene-layer split.

The proof uses a held actual-project background and children at frame 1825. Occlusion masks were rendered from read-only native scene geometry at Y=4, 9, 10, 11.5 and 14; the children's/foreground alpha is also preserved. These are camera-specific test fixtures, not a solution for a moving production camera. Use live depth/holdouts in production. Production owns the final light response, contact and live occlusion.

## Bloom and lighting

Append NodeTree `FXv006 | HDR FX bloom over | append helper` from the same file if compositing separate FX layers. Inputs are HDR FX `Foreground`, `Background`, an `Occluder` mask (white blocks effects), and `Bloom gain`. The helper glows the FX-only HDR signal, adds glare outside sprite alpha, and masks both effect and bloom. The background never enters the Glare node. Use a transparent Render Layer for Foreground and retain linear HDR until after bloom.

Each blast root publishes `hot_envelope` and `light_envelope` for production to drive nearby lights or receiver materials. The proof's brief warm receiver response is a captured native project light map driven by MID; it is a preview fixture, not a reusable scene-wide lighting rig. No sustained fire core or whole-screen glow is added.

## Transparent working sequence

`sequences/MID_unbloomed_960_RGBA/0001.png`–`0120.png`: 960×540, 24 fps, straight/unassociated alpha, 8-bit display-referred sRGB PNG using Blender Standard. Frame 1 is blast age 0 (native frame 1824). It is one shot, not a seamless loop; smoke and landed fragments may remain at the last frame. Interpret as **Straight** alpha and 24 fps in the importer. There is no baked bloom, ground scar, scene occlusion or background.

The orthographic export spans 7.0m horizontally and 3.9375m vertically. Ground anchor UV is approximately (0.5, 0.081), measured from the lower-left. To recreate its size with a card, use those physical dimensions and place that UV at the emitter contact. The export is a working proxy; append native assets for final-resolution results and HDR bloom. Apply any bloom before compositing over the destination, not to the whole finished image.

## Review and limitations

The comparison places preferred v003 on the LEFT and this candidate on the RIGHT, with identical held camera, exposure, Standard view and 24 fps. Sparse tracers and later depth variants intentionally differ. The separate ignition strip exposes consecutive native frames; any slow review is labelled and does not change project fps.

The painterly smoke uses layered original painted forms with native deformation, erosion and independent motion. It is a 2.5D authored effect, not a volumetric fluid simulation. Repeated forms can still be recognizable; final artistic acceptance and moving-shot integration are pending. Ground gouges must be placed on visible terrain; a foreground holdout may hide a correctly anchored distant mark.

All files were created under this effects folder. Protected v003 and production v038 sources were checked by SHA-256. No production scene, script, asset, render or shared UI was modified. Original earlier candidates remain preserved in their separate folders.
