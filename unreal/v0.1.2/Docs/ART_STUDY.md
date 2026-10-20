# v0.1.2 west-room art study

This pass targets one sleeping/heating room in the existing shelter. ObjectiveFix and its original eleven replay checks are preserved in the sibling v0.1.1 folder. The child rig, source paintings, inventory rules, map extent and supply loop are retained.

The actual room uses one authored native multi-material assembly: bevelled timber/masonry, extruded chipped plaster, a true casement opening and deep reveals, joined joists/floorboards, a supported pendant, joined flue/elbow, open bowls, stool and bedside cabinet. Existing CC0 bed, stove, table, vice and supplies are reused. Two meal settings, a repair surface and bedside care supplies form a deliberate domestic arrangement.

Material sources live in SourceAssets/AuthoredWestRoom: editable Python, recipe JSON, SVG surfaces, PNG rasterizations and glTF geometry. Surface marks are code-authored graphics for paint wear, soot, water tracks and grain; they are not hand-painted artist work or AI concept images. Publisher texture pixels and the established backdrop are unchanged. Room-only lit material grades desaturate diffuse textures and reduce micro-normal contrast. A restrained 6.5% albedo ambient term preserves painted shadow color in this no-GI prototype; it is a stylized shader choice, not a baked room beauty image. other rooms and the shop keep their prior materials.

Lighting uses broad cool dawn at the actual casement, a visible warm pendant, local stove spill and low open-cut fill. No new bloom/noise overlay or replacement concept backdrop is used. The room is judged at an actual engine camera, not from its source texture sheets.

Matched room study: 1600x900, orthographic width 600, camera (-500,2350,285), target (-500,-100,160), boy at (-420,0,66.15) before movement. After the matched still, the short test-only study uses real simulated walking and a small camera arc to expose depth/contact/light response. Normal gameplay camera and controls are unchanged. The art-study completion flag is not an art approval or a gameplay-regression pass.

Build, packaged regression and final media measurements will be appended after the actual runs. Character shoulder gaps, cutout stiffness, limited expression and companion behavior remain unresolved. Areas outside this single room remain at the prior prototype quality.
