# WTSC survival-game source assets

Acquired and verified on 2026-10-19 UTC.

Folder: `WTSC_LOCAL_WORKSPACE\WTSC_Survival_Game_Assets`

The existing production at `WTSC_LOCAL_WORKSPACE` was inspected at its top level only. This asset collection is separate. No existing production files, Blender scenes, Rod & Staff work, or Unreal editors were changed. No software was installed, no purchase or paid tier was acquired, no private files were uploaded, and no login or explicit EULA acceptance was submitted.

## Result

10 of the 14 requested entries are downloaded and verified. The three Fab entries and the bounded Mixamo selection remain blocked. Total archive bytes: **92,463,739** (92.46 MB; 88.18 MiB). Unpacked original source payload: 222,960,552 bytes. Both archives and unpacked files are retained. See `SUMMARY.json` for machine-readable totals.

The seven Poly Haven ZIPs were assembled locally from the publisher API files. The three animation ZIPs are unchanged publisher downloads. `SHA256SUMS.txt` lists every archive hash. `ASSET_FILE_INVENTORY.tsv` lists downloaded source-file sizes and SHA-256 hashes. `ANIMATION_CLIPS.tsv` lists actual names parsed from GLB containers. Per-pack `verification.json` files retain additional evidence.

## Downloaded packs

| Source | Selected content / license evidence | Archive | Bytes | SHA-256 |
|---|---|---|---:|---|
| [vintage_day_bed](https://polyhaven.com/a/vintage_day_bed) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\vintage_day_bed_gltf_2k.zip` | 8,762,461 | `7e4075f548135852b80841dad5b5d72c7948509f7f6cae06a598a9db6283c556` |
| [barrel_stove](https://polyhaven.com/a/barrel_stove) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\barrel_stove_gltf_2k.zip` | 7,189,693 | `3bcc651b53020d7cfce9f3293866fc4d1b1aeb725532ab10204bffd94f1c9413` |
| [wooden_table_02](https://polyhaven.com/a/wooden_table_02) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\wooden_table_02_gltf_2k.zip` | 1,908,664 | `d4fa82282b1d901a3456719b03cc55f695ed6a75b678d5740917f430c7dc3166` |
| [bench_vice_01](https://polyhaven.com/a/bench_vice_01) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\bench_vice_01_gltf_2k.zip` | 9,152,601 | `ccba869f9d46c690482abc120c06f16ee25fca71a51dff770f4dfd244c687cbe` |
| [medical_box](https://polyhaven.com/a/medical_box) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\medical_box_gltf_2k.zip` | 6,910,368 | `6f6d35bd9f1ea9e10f958c3d268dc32f43e8cb38ec85f5cba9d66ee11766d5c8` |
| [russian_food_cans_01](https://polyhaven.com/a/russian_food_cans_01) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\russian_food_cans_01_gltf_2k.zip` | 4,731,933 | `553b11c4673d14b03d925a0570e315162c4a3be35b67b493f3d5cceef5bda84c` |
| [plastic_bottle_gallon](https://polyhaven.com/a/plastic_bottle_gallon) | glTF 2.0, complete 2K JPG textures and binary buffer; CC0 per [Poly Haven](https://polyhaven.com/license) | `PolyHaven\plastic_bottle_gallon_gltf_2k.zip` | 4,309,126 | `6d6deb10ed874a5a098910b8b37ca5e64f9b9e96a17294dd6ebe757852107d38` |
| [KayKit](https://kaylousberg.itch.io/kaykit-character-animations) | Free 1.1; FBX and GLB; CC0 in bundled License.txt and source page | `Animations\KayKit\KayKit_Character_Animations_Free_1.1.zip` | 14,858,957 | `65882f31f905ad2e953819648a59287cdeab8f623908d5ef701971d3758be20f` |
| [Quaternius_Universal_Animation_Library](https://quaternius.itch.io/universal-animation-library) | Universal Animation Library[Standard].zip; FBX and GLB; Bundled CC0; current website QAL conflict (see below) | `Animations\Quaternius_Universal_Animation_Library\Universal Animation Library[Standard].zip` | 15,904,933 | `cc73fc4e495b82958207316596317a3f40b9fa38065bde1027937452da537724` |
| [Quaternius_Universal_Animation_Library_2](https://quaternius.itch.io/universal-animation-library-2) | Universal Animation Library 2[Standard].zip; FBX and GLB; Bundled CC0; current website QAL conflict (see below) | `Animations\Quaternius_Universal_Animation_Library_2\Universal Animation Library 2[Standard].zip` | 18,735,003 | `4008ea208a604773a2b2177d965f0f5d3195498b5bf838c3f5785d68e95f2a68` |

## Formats and completeness

- Poly Haven: every selected glTF dependency exists locally, all 35 source files match the publisher size and MD5, and all ZIP CRC checks pass. Each package includes base color, OpenGL normal, packed ambient-occlusion/roughness/metallic maps, geometry buffer, and glTF scene. Full API metadata in `evidence/*_files.json` preserves available higher-resolution and alternate-format URLs, hashes, and sizes for later hero-texture selection; those redundant versions were not downloaded.
- KayKit Free 1.1: 37 archive files, including 14 animation sets in FBX and 14 in GLB, medium/large mannequins and their texture, and the original CC0 license. GLB inspection found 173 animation entries across both rigs, of which 14 are T-poses (159 motion entries; overlapping names/rig variants are not unique actions). This is the entire free download as delivered; the source page advertises 161 animations. No paid Blender-source tier was acquired.
- Universal Animation Library Standard: 9 archive files. Two FBX exports for Unity and two GLB exports for Unreal/Godot. Each GLB contains the same 42 motion names plus `A_TPose`; `_RM` contains root motion and the other export disables it, per the archive README. The advertised 120+ catalogue is not the free subset.
- Universal Animation Library 2 Standard: 13 archive files. The same format and root-motion/in-place structure, with 42 motion names plus `A_TPose` per GLB. The free archive additionally includes a female mannequin in Blender/FBX/GLB formats; its README says it has no duplicated animations. This included mannequin is not the paid animation-source tier.
- All 28 downloaded GLB/glTF containers were parsed; binary headers, chunk bounds, buffer lengths/views, image dependencies, and animation sampler references were validated. FBX magic headers and ZIP member CRCs were checked. No render or retargeting validation was performed in a production editor.

## License evidence and conflict

Poly Haven license HTML is saved in `evidence/polyhaven_license.txt`, and every model folder has `SOURCE_AND_LICENSE.txt`. KayKit and Quaternius original archive licenses/READMEs remain in the extracted folders, with readable copies beside each ZIP. Source-page snapshots are in `evidence/`.

Both Quaternius archives explicitly label the content **CC0 1.0 Universal** in `License.txt` and `README.txt`, and their itch.io pages also say CC0. The current [Quaternius license page](https://quaternius.com/license.html), saved in `evidence/quaternius_license.txt`, instead publishes **QAL v1.0, updated 2026-08-28**, which permits use in products and restricts standalone redistribution. This is an unresolved source conflict. Do not label this entire collection CC0 or assume unrestricted Quaternius redistribution. The downloads remain local source assets; no legal conclusion about which statement controls is asserted.

## Remaining blockers

Detailed evidence and resume boundary: [Fab and Mixamo checks](evidence/Fab_and_Mixamo_check.md).
The [interactive capability recheck](evidence/interactive_capability_recheck.md) records installed Edge/Epic Launcher and actual DCC-CUA backend failures; the issue is an unavailable working control session, not missing applications.

| Requested item | Target | Exact blocker / action state |
|---|---|---|
| 1. PurePolygons_Modular_Building_Set | https://www.fab.com/listings/474a0598-ed86-40b6-baa1-c801d96ef4ab | Edge and Epic Launcher are installed, but no working control session is exposed: unified Edge provider unavailable; DCC-CUA 1.9.4 exact Launcher snapshot backend_unavailable and Host ping host_transport_failed. Existing account state is unverified. Public local listing requests returned HTTP 403; acquisition/license-selection flow inaccessible. Not executed; no asset acquisition, login, or EULA acceptance submitted. |
| 2. Neon_Grid_Debris_14_A | https://www.fab.com/listings/b25a9e59-9064-4b97-87c7-7faae00ec656 | Edge and Epic Launcher are installed, but no working control session is exposed: unified Edge provider unavailable; DCC-CUA 1.9.4 exact Launcher snapshot backend_unavailable and Host ping host_transport_failed. Existing account state is unverified. Public local listing requests returned HTTP 403; acquisition/license-selection flow inaccessible. Not executed; no asset acquisition, login, or EULA acceptance submitted. |
| 3. Industry_Props_Pack_6 | https://www.fab.com/listings/b5603e44-e1b0-4346-9c3d-04887aa9f87d | Edge and Epic Launcher are installed, but no working control session is exposed: unified Edge provider unavailable; DCC-CUA 1.9.4 exact Launcher snapshot backend_unavailable and Host ping host_transport_failed. Existing account state is unverified. Public local listing requests returned HTTP 403; acquisition/license-selection flow inaccessible. Not executed; no asset acquisition, login, or EULA acceptance submitted. |
| 14. Mixamo_civilian_set | https://www.mixamo.com/ | Edge and Epic Launcher are installed, but no working control session is exposed: unified Edge provider unavailable; DCC-CUA 1.9.4 exact Launcher snapshot backend_unavailable and Host ping host_transport_failed. Existing account state is unverified. Adobe ID session required to select and download; no new login attempted. Not executed; no asset acquisition, login, or EULA acceptance submitted. |

No account or license prompt was denied by the user or submitted with uncertain outcome: those acquisition steps were not reached. Local HTTP 403 responses are service request failures, not automatic approval-review rejections. Restore an authorized browser surface, inspect the exact acquisition prompt, and request approval if a new login or explicit EULA acceptance is required. Fab per-listing licenses are still unverified, and no Mixamo clip names are claimed as downloaded.

## Scope for later game work

These are source assets for civilian shelter, scavenging, and survival development. They have not been imported into Unreal and are not a finished cinematic style or animation solution. They do not provide verified ten-year-old leads or companion-carrying animations. Retargeting, proportions, child motion, interaction alignment, and painterly art direction need separate review.
