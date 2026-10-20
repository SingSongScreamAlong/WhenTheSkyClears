# First morning

One small, civilian search in a damaged village. The two established leads remain age ten. The boy is controlled; the girl remains inside the shelter near their sleeping area. Their relationship is not invented. This is a bounded prototype, not a campaign or finished child-performance solution.

The opening view is a cutaway house: sleeping area to the west, a stove and work table in the middle, and communal supply shelves to the east. Upstairs, a rolled blanket, an abandoned suitcase and a schoolbook suggest an interrupted home. The camera stays close enough to read the shelter before revealing a single damaged shop across a short street. Cool dawn and muted plaster contrast with restrained warm lamps and the stove.

The scene combines editable native geometry, seven imported Poly Haven props, and the established village painting as a background matte. The custom walls, beams, roof, street scars, rubble, shop counter and crate are provisional authored geometry. A matte is not 3D terrain. The actual viewport pass repaired camera clipping/exposure, orthographic framing, static attachment, ground contact and shop readability. This is the first playable composition, with substantial character, animation and environment craft still ahead of the cinematic ambition.

The established boy atlas and girl profile are reused without altering their originals. Texture UVs select the existing face and garment parts. The initial controller is a painted puppet in a 3D scene, with provisional procedural limb motion. It is not a ready-made 3D child or a Quaternius retarget. The girl's provisional body also reuses boy garment pieces; this is explicitly unfinished and must be reviewed before character acceptance. Child silhouette, dress, contact, turning, crouching and acting need a dedicated pass.

## Playable scope

- A/D or left/right: walk along the shallow side-view route.
- Hold E beside the shop crate for 2.5 seconds while stationary to search. It yields two food units, two water units and one bandage, filling a five-unit pack. The finite cache cannot yield duplicates.
- Return to the shelter's supply shelves and press E to deposit. Storage begins with two food, two water and one bandage; after a full return it contains four food, four water and two bandages.
- Food and water needs decline over time. Exhaustion can reduce health. F/G/H beside storage consume available food/water/bandages, with bounded recovery. A failed day resets at home.
- R resets the day, restoring the original supplies and cache. F5/F9 use a project-specific native save slot. Esc pauses.

No combat, campaign, companion-carrying, multi-location system, external account or paid dependency is included.

## Acceptance

Run the authored native level in the installed engine. Inspect shelter scale, imported prop placement/materials, the painted faces, 2.5D camera and warm/cool lighting before expanding the scene. Fix collisions and visual registration in this one view first.

The opt-in native replay uses simulated engine key events to walk from shelter to cache, hold search, test finite cache behavior, return and deposit. It then exercises native save/readback and the R restart binding. It records state assertions and captures real viewport frames. This does not establish human playtest quality or operating-system keyboard delivery. Verify ordinary keyboard control separately when a supported foreground route and resource release are available.
