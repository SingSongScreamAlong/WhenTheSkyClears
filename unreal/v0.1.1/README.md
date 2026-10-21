# When The Sky Clears — Shelter Study v0.1.1

Open `WTSC_Survival.uproject` with installed Unreal 5.8.3, or run `Scripts/PlayPackaged.cmd` after packaging. The separate v0.1.0 project and ZIP remain untouched in the sibling `WTSC_Survival_Prototype` folder.

A bounded civilian shelter study: one controllable age-ten child, a distinct companion presence, one damaged shop, finite supplies, carry capacity five, home deposit, food/water/health, save/load and reset. The upper floor is deliberately inaccessible: a collapsed stair, broken landing and barricade explain that boundary. There is no vertical traversal in this version.

A/D or arrows walk; hold E at the crate to search; press E by the shelter shelves to unpack. F eats, G drinks, H uses a bandage when needed. Tab changes between the shelter overview and closer play framing. R resets the day, F5 saves this version's checkpoint, F9 loads it, Esc pauses.

The boy uses the established painted atlas; the girl retains her established face/braid and has a separate slate tunic/skirt silhouette. Motion consists of authored cutout poses, bending limbs and world-space stance foot locking. These are provisional interpolated puppets, not finished cinematic child animation, hand-drawn frame animation, mocap, or retargeted Quaternius animation. The companion is a presence beside the bed and has no following/carrying behavior.

Search now crouches and reaches into the crate. Deposit visibly lifts the carried cloth bundle toward the shelf and commits the inventory transfer during that action. The HUD occupies 49 pixels at top and bottom at 1600×900; contextual prompts and the search bar sit beside the target, away from the child. Shelter trims are thinner, repairs and window boards differ, and the damaged upstairs has grouped belongings and debris.

See `Docs/VERIFICATION.md` and `Evidence/BUILD_STATUS.json` for actual build/test status and measured video/runtime rates. Screenshots and the motion preview are genuine Unreal output; failed or preliminary runs are retained separately. No giant PDF is produced.

Seven downloaded Poly Haven models are imported as native meshes with complete materials/textures. Established WTSC paintings and raw source assets remain preserved. Source/license evidence remains in the asset folder and copied baseline receipts. Quaternius/KayKit animations were inspected but are not used in the cutout rig; no new paid/Fab/Mixamo acquisition occurred in this refinement.
