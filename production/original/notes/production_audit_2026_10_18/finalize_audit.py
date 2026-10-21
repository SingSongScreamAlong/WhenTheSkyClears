"""Assemble the human audit and bounded evidence index without promoting assets."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
read = lambda name: json.loads((OUT / name).read_text(encoding='utf-8'))
census = read('census.json')
runs = read('native_runs.json')
decodes = read('media_decodes.json')
headers = read('media_headers.json')
color = read('color_master_pixel_comparison.json')

findings = [
    {
        'id': 'A01', 'priority': 'P1', 'area': 'Assembly and production control',
        'finding': 'The current film and newer development components have no single promoted integration manifest.',
        'evidence': ['native_full_v040.json', 'native_world_v058.json', 'native_color_v063.json',
                     '../../work/color_arc_v063/START_HERE_v063.txt'],
        'impact': 'Work repeatedly advances in separate studies while the complete review movie continues to show held children and older world/color work.',
        'next_action': 'Create a versioned assembly candidate with explicitly selected world, character design, performance, effects, palette, title and audio dependencies. Pin paths, hashes, scenes, frame ranges and review status; keep the original v040 master frozen.',
        'done_when': 'A full 2544-frame edit resolves its declared components and matches its own exported review movie. Candidate, reviewed and artistically accepted remain separate states.'
    },
    {
        'id': 'A02', 'priority': 'P1', 'area': 'Story performance',
        'finding': 'The full film translates one held pair drawing instead of delivering the planned progression of paired acting.',
        'evidence': ['native_full_v040.json', 'full_cut_samples.jpg',
                     '../../work/production_review_v059/START_HERE_v059.txt',
                     '../../work/trailer_development_v060/START_HERE_v060.txt'],
        'impact': 'The audience cannot read the intended change from play to fear, protection, fatigue and mutual reassurance through the children.',
        'next_action': 'Build a timed performance map for the whole 100-second picture. Finish story-specific poses and transitions, including real gaze changes, anticipation, hand contact and the first resumed step after recovery. Reuse the working ordinary walk where it serves the beat.',
        'done_when': 'Each narrative interval has intentional, readable acting at normal playback speed in the full composition; held drawings are only deliberate dramatic holds.'
    },
    {
        'id': 'A03', 'priority': 'P1', 'area': 'Final composition',
        'finding': 'The moving title masks important faces, feet and hand-taking gestures.',
        'evidence': ['full_cut_samples.jpg', 'development_samples.jpg',
                     '../../work/production_review_v059/Title_Visibility_Review_CORRECTED_v059.jpg'],
        'impact': 'Animation can improve in an unmasked view while remaining unreadable in the actual trailer.',
        'next_action': 'Review every important acting beat through the exact moving glyph mask. Adjust staging and beat timing inside readable openings in a separate composition candidate, retaining the established wording and current timing unless the user directs a treatment change.',
        'done_when': 'Faces and the meaningful contact/reaction remain legible during their story beats in normal-speed masked playback.'
    },
    {
        'id': 'A04', 'priority': 'P1', 'area': 'Color and native export',
        'finding': 'The v063 native edit uses AgX while its world uses Standard, changing the rendered picture.',
        'evidence': ['color_master_check.json', 'color_master_pixel_comparison.json', 'color_pipeline_comparison.jpg'],
        'impact': 'The native review edit can darken and alter the palette relative to the world renders used to judge the artwork.',
        'next_action': 'Match the intended world/edit color pipeline in a new candidate, then verify direct-world, native Scene-strip and encoded output agreement at representative early/middle/late color states.',
        'done_when': 'The same source frame agrees within an explicit color/quantization tolerance through the native edit and the encoder. At G981/720p, changing only the edit view to Standard in RAM reduced maximum RGB error from 52 to 1 and mean error from 5.112 to 0.280 code values.'
    },
    {
        'id': 'A05', 'priority': 'P1', 'area': 'Camera, travel and time',
        'finding': 'The first-danger candidate cannot be spliced directly back into the old route without a camera/world discontinuity.',
        'evidence': ['camera_travel_samples.json', '../../work/trailer_development_v060/START_HERE_v060.txt'],
        'impact': 'The candidate begins at the old position but finishes about 3.779 metres behind it, producing a large jump at the outgoing join.',
        'next_action': 'Conform body travel, camera route and world progression as one continuous sequence. Preserve the source 30fps-to-production-24fps mapping F=1+(G-G0)*30/24, including garment caches; preserve the baked girl phase lead and apply root travel once.',
        'done_when': 'The adjacent shots have continuous camera/landmark positions and velocity, correct feet/ground contacts and stable color/effect clocks. The 32-source-frame cycle remains 25.6 production frames rather than being rounded.'
    },
    {
        'id': 'A06', 'priority': 'P2', 'area': 'Character craft and motion',
        'finding': 'The walking model is improved, but fixed profiles, rigid hand poses and highly regular torso/arm timing limit the performance.',
        'evidence': ['development_samples.jpg', '../../locomotion/face_hand_finish_v050/IMPORT_TIMING_AND_ASSESSMENT_v050.txt',
                     '../../locomotion/coat_fluidity_v051/evidence/ROBOTIC_MOTION_DIAGNOSIS.json'],
        'impact': 'Good contact measurements alone do not create convincing body intention, emotional expression or connected drawing construction.',
        'next_action': 'Develop registered head angles, eye/gaze and expression drawings, relaxed/reaching/clasping/supporting hands, and deliberate chest/pelvis/shoulder/elbow timing. Keep the age-ten proportions and established paintings. Distinguish reassuring contact from a grip bearing body weight.',
        'done_when': 'A normal-speed shot review confirms clear intent, connected shoulders/necks/wrists and motivated rhythm; technical foot-contact checks also pass.'
    },
    {
        'id': 'A07', 'priority': 'P2', 'area': 'Cloth, hair and drawing dependencies',
        'finding': 'Boy-coat follow-through now has a separate v051 native; girl cloth/braid work was deferred and is not established in the current shot.',
        'evidence': ['native_coat_v051.json', '../../locomotion/coat_fluidity_v051/evidence/COLD_COAT_VALIDATION.json',
                     '../../locomotion/girl_cloth_followthrough_v047/DEFERRED_NOT_BUILT.txt'],
        'impact': 'Secondary motion remains inconsistent and cached garment drawings can stop matching newly edited rig poses.',
        'next_action': 'Finish the v051 same-gait review before selecting it. Add restrained girl dress, braid and ribbon response after primary performance settles. Invalidate/rebuild dependent drawing caches when the rig or retiming changes.',
        'done_when': 'No contour gaps, intersections or cycle seam pops at fractional frames; cloth supports the body action without masking a robotic gait.'
    },
    {
        'id': 'A08', 'priority': 'P2', 'area': 'World and art resolution',
        'finding': 'The painted world is coherent, but detail and depth need selective refinement; many principal source paintings are 1672x941.',
        'evidence': ['native_color_v063.json', 'development_samples.jpg', '../../work/world_minimum_v058/START_HERE_v058.txt'],
        'impact': 'UHD output can still reveal soft source detail, flat facades, competing background texture or pasted-on contacts.',
        'next_action': 'Retain the v058d foreground fix and the restored layered 2D/2.5D direction. Quiet values behind faces/hands, ground firelight, and add separated painted edges/interiors only where parallax or contact reveals them. Repaint selected hero-facing source regions at sufficient detail after composition is settled.',
        'done_when': 'Actual UHD crops and moving-camera reviews show useful depth and stable world-space roots, while the final mask still lets the detail read. The withdrawn v061 forest is not reintroduced.'
    },
    {
        'id': 'A09', 'priority': 'P2', 'area': 'Effects',
        'finding': 'Painted main-impact and newer clod-silhouette experiments are separate candidates, not a single established full-film effect.',
        'evidence': ['native_impact_v015d.json', 'development_samples.jpg', '../../effects/squat_clods_v015/ROUGH_NOTES.txt'],
        'impact': 'Replacing one plume with the latest experiment can regress the drawn look, scale, attachment or settling behavior.',
        'next_action': 'Select the impact silhouette and timing in context first. Then connect flash, light, eruption, debris, landing and persistent ground response on the global clock. Use a separate append collection with an explicit root/timing contract; the empty scene in an append asset is expected.',
        'done_when': 'The effect is rooted, force-directed, visually compatible and readable through the title; it leaves a coherent disturbance and has normal-speed artistic review.'
    },
    {
        'id': 'A10', 'priority': 'P2', 'area': 'Sound and delivery record',
        'finding': 'The project has the real 100-second music source, but no separate local footsteps/cloth/impact ambience sources were found in the census.',
        'evidence': ['census.json', 'audio_signal_check.json', '../../notes/music_source.json'],
        'impact': 'Contacts and distant threats lack the additional restrained sound layer described in the source treatment.',
        'next_action': 'Add sparse contact and distant environmental sound after acting timing is stable, keeping the music dominant. Preserve the 90-100-second fade and silent credits; centralize the existing source/permission records before any public delivery.',
        'done_when': 'A listening review confirms restrained perspective, synchronized contacts, no extra terminal impact and silence in the credits. Local records still describe music release permissions as not established; this audit makes no licensing determination.'
    },
    {
        'id': 'A11', 'priority': 'P1', 'area': 'Version control and reproducibility',
        'finding': 'The repository has zero commits, zero tracked files and no .gitignore; 421 of 1070 Python files contain absolute Windows paths.',
        'evidence': ['census.json', 'source_hashes.json'],
        'impact': 'Directory copies preserve many checkpoints, but do not provide a reviewable source history or a portable, repeatable build.',
        'next_action': 'Establish source/version history with an explicit large-file policy and tested backup. Keep source art/native assets/manifests separate from generated caches. Consolidate launch/render/encode configuration, dependency versions and a project-root resolver; migrate the active path first.',
        'done_when': 'A clean restore can locate Blender/Python/FFmpeg, resolve the pinned inputs and reproduce a bounded shot. External backups are not established or disproved by this local audit.'
    },
    {
        'id': 'A12', 'priority': 'P2', 'area': 'Render and review workflow',
        'finding': 'Verification is extensive but fragmented among version-specific scripts and historical status files.',
        'evidence': ['census.json', 'media_headers.json', 'media_decodes.json', 'color_master_pixel_comparison.json'],
        'impact': 'A technically valid new proof can be mistaken for a complete film, and repeated UHD reviews consume time before acting/composition is resolved.',
        'next_action': 'Use one bounded render job record with input hashes, scene and global range, output color settings, exit state, expected/decoded frame count and review status. Write temporary outputs and publish them atomically after success. Render 720p acting and mask proofs first, UHD keys next, and the final UHD sequence after the relevant reviews.',
        'done_when': 'Every review clearly states its scope and exact native source. A decode pass remains distinct from normal-speed artistic acceptance, and unchanged historical proofs are not rerendered without reason.'
    },
    {
        'id': 'A13', 'priority': 'P3', 'area': 'Historical hygiene and navigation',
        'finding': 'Old entry points and abandoned outputs remain mixed with current work.',
        'evidence': ['census.json', 'media_headers.json', 'exact_duplicate_sources.json', '../../LIVING_WORLD_START_HERE.txt'],
        'impact': 'The old start file still points to v010/v011, while current work is v063; old failures can also confuse tooling or broad scans.',
        'next_action': 'Add one current entry point and component map, retaining historical documents. Label or exclude failed historical artifacts from active validation. Archive only after a verified restore; preserve intentional reference duplicates.',
        'done_when': 'A new collaborator reaches the current world/design/shot/palette sources unambiguously. Historical cleanup addresses one syntax-invalid v034 verifier, four non-JSON historical .json files and four 48-byte v019 MP4 stubs without presenting them as current-master failures.'
    },
]

baselines = {
    'status': 'Observed component map for audit only; no asset promotion or approval.',
    'production_method': 'Layered 2D/2.5D painted artwork; Blender assembly, rigging, camera and compositing.',
    'picture_contract': {'picture_seconds': 100, 'credit_seconds': 6, 'fps': 24, 'frames': 2544,
                         'music_fade_seconds': [90, 100], 'credits_start_frame': 2401},
    'full_cut': {'path': runs[0]['source'], 'status': 'Complete technical review cut with held pair'},
    'world': {'path': runs[1]['source'], 'status': 'v058d packed foreground/world development; not rendered as the newer full cut'},
    'recovery': {'path': runs[2]['source'], 'global_frames': [1801, 1920], 'status': '75-80s bounded candidate with older character construction; reassuring hand contact'},
    'current_shot_palette': {'path': runs[3]['source'], 'global_frames': [937, 1056],
                            'status': '39-44s layered painted first-danger action plus global shared color controller; palette movie is held-pose comparison'},
    'character_finish': {'path': runs[4]['source'], 'source_fps': 30, 'status': 'Face/hand finish candidate, retains v049 gait'},
    'boy_coat': {'path': runs[5]['source'], 'status': 'Separate v051 native; preview rendering observed during audit'},
    'impact': {'path': runs[6]['source'], 'status': 'Append asset; final artistic selection not inferred'},
    'withdrawn': 'work/production_look_v061; forest redesign is historical experiment only',
}

integrity = []
for item in runs:
    evidence = read('native_' + item['label'] + '.json')
    path = ROOT / item['source']
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    integrity.append({'path': item['source'], 'audited_sha256': evidence['sha256'],
                       'final_sha256': actual, 'unchanged_since_native_check': actual == evidence['sha256']})

# Record concurrent external work without claiming the census is a filesystem freeze.
with (OUT / 'file_inventory.csv').open(encoding='utf-8', newline='') as stream:
    prior = {r['path']: r for r in csv.DictReader(stream)}
added, changed = [], []
for p in ROOT.rglob('*'):
    if not p.is_file() or p.is_relative_to(OUT) or set(p.relative_to(ROOT).parts) & {'.git', '__pycache__'}:
        continue
    rel = p.relative_to(ROOT).as_posix()
    if rel not in prior:
        added.append(rel)
    elif p.stat().st_size != int(prior[rel]['bytes']):
        changed.append(rel)
drift = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'new_files_since_census': added,
         'size_changed_since_census': changed,
         'note': 'Other work was writing v051 preview/render evidence during the audit; new artifacts are outside the census/decode snapshot unless explicitly checked.'}
(OUT / 'snapshot_drift.json').write_text(json.dumps(drift, indent=2), encoding='utf-8')
(OUT / 'final_source_integrity.json').write_text(json.dumps(integrity, indent=2), encoding='utf-8')
(OUT / 'findings.json').write_text(json.dumps(findings, indent=2), encoding='utf-8')
(OUT / 'observed_components.json').write_text(json.dumps(baselines, indent=2), encoding='utf-8')

intro = f'''WHEN THE SKY CLEARS - PRODUCTION AUDIT
18 October 2026 | Project-local evidence snapshot

ASSESSMENT
The strongest production gain is to turn the existing studies into a continuously
acted, readable film. The painted world, actual native assets and render pipeline
already exist. Integration, story performance and final title composition are the
critical path. More isolated polish cannot by itself advance the full review cut.

The established method is layered 2D/2.5D. Preserve the painted artwork and age-ten
character identities, carry both children from full painted color to charcoal,
and retain the restored forest direction. The v061 forest redesign is withdrawn.
The current contract is 100 seconds of picture plus six seconds of silent credits.
The older 100-second handoff is not treated as a reason to remove those credits.

WHAT WAS CHECKED
- Census at {census['captured_utc']}: {census['files']:,} files,
  {census['bytes']/1e9:.2f} GB ({census['bytes']/1024**3:.2f} GiB), excluding .git, __pycache__
  and this audit folder. Includes 304 .blend files and 98 .blend1 backups.
- Parsed {census['json_files']:,} JSON files and syntax-checked all {census['python_files']:,} Python files.
  Project builders/verifiers were not executed as part of that source scan.
- SHA-256 recorded for {census['hashes_computed']:,} native/source/archive files,
  totalling {census['hash_bytes']/1e9:.2f} GB; file_inventory.csv covers the full census.
- Independently reopened seven selected native checkpoints in Blender 5.2.2,
  without saving them. No missing unpacked used file images were found in those
  samples. No invalid drivers were reported after representative frame samples.
- Two missing-target hand drivers in v050/v051/v063 were investigated: they belong
  to a hidden BEFORE reference hand, not the active rendered pair. This is historical
  cleanup, not evidence of a current visible hand failure.
- Inspected {len(headers)} MP4 container headers. Fully decoded eight selected movies,
  including the actual UHD v040 master: {sum(r['decoded_frames'] or 0 for r in decodes):,} total frames,
  all matching expected counts. The v040 master is 3840x2160, 24fps, 2544 frames/106s.
- Made and inspected actual decoded picture sheets; rendered v063's world and native
  edit at G981/1280x720; isolated a view-transform mismatch through a controlled
  Standard-view edit render made only in RAM.
- Measured native camera positions across the first-danger join. Measured decoded
  v040 audio: the end diminishes and 100.1-106s is digitally silent. Listening/mix
  quality was not assessed.
- All seven selected native source hashes still match at final readback.

LIMITS
This is a whole-project census plus focused deep checks, not a claim that every
one of the 304 native files or every frame of 221 movies received artistic review.
Visual assessment used decoded samples and native stills, not observed continuous
player playback. Existing project reports were checked against newer work so old
limitations are not automatically repeated as current defects. Technical tests
do not establish artistic acceptance or the requested Arcane-level craft.

The DCC-MCP CLI was absent from the selected PATH lookup and native MCP discovery
returned no matching inspection tool. Actual file checks therefore used the
project's installed Blender executable in separate background processes. This
verifies native file inspection, not a working live adapter or UI session.

The project remained active: v051 preview files were being written by other work.
snapshot_drift.json records {len(added)} new files and {len(changed)} size changes since
the census. Counts and review claims are timestamped snapshots; later files are
not silently included as audited. This audit writes only inside its own folder.

OBSERVED COMPONENTS AND WHY THE HIGHEST VERSION IS NOT A FULL FILM
v040: full 106-second review movie and editable master; pair drawing is held.
v058d: improved packed world/foreground. Keep its fix; do not repeat the old
       blanket recommendation to rebuild the mirrored foreground everywhere.
v059: separate 75-80-second recovery benchmark using earlier character design.
      Its improved touch is reassuring contact, not load-bearing assistance;
      recovery-to-walk and the outgoing step remain development work.
v060 -> v062 -> v063: 39-44-second first-danger action, restored painted continuity,
      then shared global color controller. The five-second color movie holds the
      composition while compressing 100 seconds of palette progression; it is not
      a full trailer or a real-time action proof.
v047 gait -> v048 loading -> v049 model fit -> v050 face/hand finish -> v051 boy coat:
      separate character lineage. v063 imports selected v050 materials, not its
      whole gait/model or the newer boy-coat response.
v015d main impact: append asset used by a recovery candidate. The newer v015 clod
      silhouette rough is a different experiment and is not automatically a replacement.
v061: withdrawn 3D-forest experiment; keep as history rather than the active look.

CONCRETE COLOR DEFECT
At identical G981 and 1280x720, the v063 world uses Standard and the native
WTSC_FIRST_DANGER_EDIT_v060 uses AgX. The latter changes 98.86% of pixels, with
maximum channel error 52/255 and mean absolute channel error 5.112/255.
Changing only the edit view transform to Standard in RAM reduces maximum error to
1/255 and mean error to 0.280/255. That residual is consistent with the sequencer's
quantization, rather than an artistic grade. No production native was saved.
This is one tested frame/resolution; verify representative states before release.

CONCRETE ROUTE/FRAME ISSUE
At G937 both old and new cameras are at X=51.373333m. At G1056, old v040/v058
is X=58.777779m while the newer candidate is X=54.999115m: a 3.778664m mismatch.
The following old frame G1057 is X=58.840000m, a 3.840885m transition from the
new final frame. A normal new-candidate step would be about .030469m/frame.
The newer camera is constant outside its authored interval. Extending that file's
timeline cannot produce the remaining 95 seconds of performance or route.

PRIORITIZED FINDINGS
P1 = blocks a dependable full-film result or its meaningful review.
P2 = substantial craft/workflow improvement after the relevant P1 dependency.
P3 = historical cleanup and navigation. No destructive cleanup is proposed.
'''
sections = []
for f in findings:
    sections.append(f"\n{f['id']} | {f['priority']} | {f['area']}\n{f['finding']}\nWhy it matters: {f['impact']}\nNext: {f['next_action']}\nCompletion evidence: {f['done_when']}\nEvidence: " + '; '.join(f['evidence']) + '\n')

tail = '''
RECOMMENDED PRODUCTION ORDER
1. Establish the component manifest and a separate integrated working master.
   Record current decisions in one entry point and preserve frozen originals.
   Establish source/large-file version history and a tested restore in parallel.
2. Fix/verify the edit color pipeline, then conform the 39-44s first-danger shot
   with at least one second of actual neighboring motion on each side. Solve
   camera/world travel and title visibility before adding more drawing detail.
3. Complete a 35-50s story passage around that shot: meaningful look-back, body
   reaction and hand-taking, with current designs and the shared global palette.
   Review unmasked and through the actual title at the same production clock.
4. Use the resulting assembly rules to develop the remaining narrative intervals.
   Bring the older recovery onto the chosen model and author its resumed step.
   Keep separate play/run/hunker/fatigue intentions rather than extending one walk.
5. Add secondary drawings, restrained grounded effects and selective world detail.
   Finish sparse sound, then review the full 106s continuity and timing.
6. Render approved-scope UHD keys, then the full UHD movie. Reopen the packaged
   native, decode the export, inspect joins and fades, listen, and review normal
   playback. Keep technical completion distinct from the user's artistic decision.

STORY COVERAGE REGISTER (current full cut versus bounded development)
0-18s   Individual play: full cut has held pair; walk sources do not establish
        authored skips, backward teasing, chase or puddle interactions.
18-35s  Unease: environment progression exists; paired behavior still needs a
        deliberate transition that can be read through the mask.
35-50s  First danger: 39-44s candidate exists. Actual gaze/head drawings, response,
        final mask readability and neighboring route continuity remain.
50-67s  Threat/protection/escape: isolated earlier proofs are retained. The current
        complete movie does not establish these as finished paired acting.
67-80s  Fatigue/recovery: 75-80s v059 candidate exists with older model and no
        completed recovery-to-travel transition.
80-90s  Title passage: exact moving typography exists; meaningful child action
        must be staged inside its readable openings.
90-100s Quiet ending: music fade exists; v063 reaches full charcoal at 96s in its
        global controller, but that controller is not in the full v040 movie.
100-106s Silent credits: complete technical output exists; retain exact wording.
This is a coverage/development register, not an assertion that older studies have
no useful motion, and not an approved percent-complete estimate.

NEXT PASS - REVIEWABLE DELIVERABLES
- A versioned native assembly candidate, with explicit component hashes and clocks.
- A short first-danger proof including both neighboring handles, using current
  designs and both unmasked and final-title views at identical timings.
- Direct-world/native-edit/encoded color comparisons at the chosen keys.
- Root/camera/landmark continuity, foot support and drawing-cache verification.
- A normal-speed review noting gaze, body intention, grip, silhouette, occlusion,
  costume continuity and the entry/exit of the beat.
- One updated full-cut development movie after the bounded integration is sound.

HISTORICAL AND STORAGE FINDINGS IN CONTEXT
One old verifier, scripts/verify_complete_trailer_v034.py:25, has a SyntaxError
from 'else2160' / 'else3840'. The current v040 output passed its independent decode;
this old script is not evidence that the current movie is corrupt.
Four historical .json files are invalid: three contain a plain-text failed Library
upload message and one is empty. Preserve those attempts but do not parse them as
successful structured receipts. Paths are listed in census.json.
Four old v019 part MP4s are each 48 bytes and have unreadable headers. The selected
current movies all decode. Paths are listed in media_headers.json.
Exact duplicate native/source/archive content totals about 448 MB beyond one copy
across 33 groups in the hashed subset. Many copies are intentional preserved
references. They are not automatic deletion candidates. Render/locomotion/effect
folders dominate storage; define retention and restore rules before any archive.

EVIDENCE TO OPEN
full_cut_samples.jpg              Actual v040 film samples, including final card.
development_samples.jpg           Separate newer sources, explicitly labeled.
color_pipeline_comparison.jpg     World, native edit, amplified difference, test.
findings.json                     Structured priority/action/completion register.
observed_components.json          Non-promoting component map and timing contract.
file_inventory.csv / census.json  Complete census plus source parsing findings.
source_hashes.json                SHA-256 of selected source/native/archive classes.
native_*.json / native_runs.json  Independent native structural checks and status.
camera_travel_samples.json        Evaluated old/new camera positions and matrices.
media_headers.json                All inspected MP4 headers; not all-frame decode.
media_decodes.json                Exact eight-movie full-decode results.
audio_signal_check.json           Signal measurements, not a listening judgment.
final_source_integrity.json       Final readback of seven native checkpoints.
snapshot_drift.json               Concurrent new/changed files after census.

All evidence names above are relative to this audit folder unless prefixed by
'../../', which resolves from this folder to the project root. Existing production
scenes, artwork, timing, soundtrack and historical files were not edited.
'''
(OUT / 'PRODUCTION_AUDIT.txt').write_text(intro + ''.join(sections) + tail, encoding='utf-8')
assert all(r['unchanged_since_native_check'] for r in integrity), integrity
assert all(r['passed'] for r in decodes), decodes
print(json.dumps({'report': str(OUT / 'PRODUCTION_AUDIT.txt'), 'findings': len(findings),
                  'native_hashes_unchanged': len(integrity), 'new_files_since_census': len(added),
                  'size_changed_since_census': len(changed)}, indent=2))
