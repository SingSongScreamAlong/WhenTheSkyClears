WHEN THE SKY CLEARS — GAS + PARTICLE TECHNIQUE TEST v004
Coarse feasibility proof. Not approved cinematic art or a production replacement.

WHAT TO REVIEW
WTSC_Gas_Particles_75-80s_v004.mp4: five seconds, 1920 x 1080, 24 fps.
WTSC_Compare_LEFT-v003_RIGHT-Gas-v004.mp4: v003 left; gas/particles right.
Both panels retain native 1920 x 1080 framing. Both use the same held source
camera, children, scenery and foreground mask. The comparison covers production
frames 1800–1919, ignition 1824. It does not test the new stumble performance,
moving camera, live occlusion, production contact or integrated lighting.

RESULT
Installed Blender 5.2.2 LTS executed real native GAS/Mantaflow and OpenVDB bakes.
The gas field evolves in 3D without recycling the four painted smoke forms.
Two native Newtonian particle systems supply 12 small debris chips and six
short-lived embers. Their disk caches and actual live particle positions were
verified. v003's 13 cold smoke cards and old 38 debris objects are hidden only
in this isolated copy; its brief painted launch and low dust are retained.

This proves technical feasibility at low cost. It does NOT prove an art upgrade.
At 48 divisions without noise up-res, the cloud is soft, smooth and fog-like,
with less granular painted definition than v003. It spreads broadly late in
the shot. Current source shaping, density, shading and painterly finishing are
not sufficient for cinematic acceptance. Do not replace production v003 with
this coarse gas test as approved final art. No larger bake was attempted.

MEASURED COST
Initial40-division,72-frame pilot: 5.56 s bake, 23.5 MiB cache, 321 MiB peak RSS.
Five-second48-division,120-frame gas: 9.50 s bake, 61.4 MiB cache, 327 MiB peak RSS.
Sparse particles: 0.46 s bake, about42 KiB of point-cache files.
Final120 GPU render calls: about61.45 s total, 32 Eevee samples with volume
shadows. The main volumetric pass measured about1.01 GiB peak process RSS and
1801 MiB total GPU memory used, from a282 MiB baseline. GPU memory is device
total, not exclusive process attribution. Exact evidence is in evidence/.
The gas jobs requested two CPU threads at below-normal priority. Each bake was
supervised with120 s,128 MiB cache and2 GiB RSS hard caps; none was reached.
No noise up-res, new software, stock purchase or large simulation cache was used.
GPU work was deferred whenever production workers were observed. A slow
one-thread CPU preview was stopped only after its exact owned PID was checked;
its27 partial frames remain separate and are excluded from final videos.

NATIVE FILE AND CACHES
Extract the entire ZIP and open:
native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend
Keep cache/proof_48r_120f and the native/blendcache_* folder beside it as shipped.
The gas cache uses //../cache/proof_48r_120f. The particle cache depends on the
blend basename; preserve that basename and its matching blendcache folder.
All image dependencies are packed. Relative gas cache loading and18 live
particles at frame12 were checked in the portable copy; density at frame60
matches the original cache. The ZIP contains ordinary bytes, not hardlinks.

TIMELINE, SCALE AND LIMITS
Cache frames1–120 cover five seconds after ignition. Local frame1 corresponds
to production frame1824 (76 seconds), so production frame = local +1823.
The five-second review movie includes local -23..0 pre-roll, then1..96.
Blender's animation start clamps negative values to0, so the helper renders the
23 negative pre-roll frames explicitly as stills; all120 final frames are actual
new GPU renders. The native UI can inspect cache frames1–120 by extending End.
The source remains at [109.1,10,-0.7048803] metres; Z up, X horizontal, camera
toward +Y. Domain dimensions are4.2 x2.8 x4.0 m; actual grid48 x32 x46.
This is a cached local technique scene, not a tested global-timeline Append
asset. Moving, scaling or retiming the native solver/particle caches requires
proper cache rebinding or rebaking. Production owns that integration.

The volume uses actual density, zero emission/blackbody, and native shadowing.
A mild16%3D noise wash modulates density as finish; it is not simulated fine
detail. The initial painted hot jet/flash end independently at age14. The
embers cool and die early; there is no persistent smoke-core glow.
The native scene contains clearly named preview-only shading lights and a
transparent TEST collision floor. They affect this isolated proof only.
Do not append the whole proof scene's lights, collider or held masks into
production. Existing production scenes, scripts, assets and renders were not
modified. v003's protected source hash is unchanged; rejected v001 is excluded.

ALPHA AND DELIVERY
Review MP4s are opaque H.264 BT.709 yuv420p, each under20 MB. Source painted
images use Straight alpha; native render compositing uses premultiplied results.
No transparent animation export,4K validation or cinematic acceptance is claimed.
