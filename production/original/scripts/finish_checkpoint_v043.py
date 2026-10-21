import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];export=json.loads((R/'notes/world_v016/combined_export_completed_v043.json').read_text());build=json.loads((R/'notes/world_v016/combined_trial_build_v043.json').read_text());qa=json.loads((R/'notes/world_v016/combined_media_qa_v043.json').read_text());stage=json.loads((R/'notes/world_v016/frozen_staging_v043.json').read_text());checks={}
for path,sha in [(export['source'],export['source_sha256']),(export['master'],export['master_sha256']),(export['view'],export['view_sha256']),(export['before_after'],export['comparison_sha256']),(build['motion_snapshot']['sealed_source'],build['motion_snapshot']['source_sha256']),(build['motion_snapshot']['snapshot'],build['motion_snapshot']['snapshot_sha256']),(build['fx_snapshot']['sealed_source'],build['fx_snapshot']['source_sha256']),(build['fx_snapshot']['snapshot'],build['fx_snapshot']['snapshot_sha256'])]:
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert actual==sha,(path,actual);checks[path]=actual
old=json.loads((R/'notes/world_v016/full_completed_v040.json').read_text())
for path,sha in [(old['source'],old['source_sha256']),(old['movie'],old['movie_sha256'])]:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha;checks[path]=sha
review={'checkpoint':'v043 open-frame integration checkpoint; NOT approved cinematic performance','actual_review':'All40actual8fps decoded actor samples inspected through five chronological native-pixel crop sheets, plus actual1080shot keys1801/1825/1830/1843/1852/1881/1920 and nativeScene+Soundmaster1830check. No real-time playback claim; Codexmoviepreview request returnedqueued.','what_works':['Near-age charcoal identities retained, boy slightlytaller','Floor projection corrected for newrig depth; no new detachedwaist/shoe noticed ininspected motion samples','Live single-scene eruption behindcharacters, short hotphase followedbycold evolving/thinning smoke','Foreground repeating lowerplantstrip reduced withnativebank edge','NativepackedScene+Sound5sexport fromcoldreopenedsource,120frames4K24fps,original75–80audioalignmentcorrelation>.999'],'weakest_art_issue':'At76.5–77.4s the foldedknee/boot andrigidhand/cuff shapes, combinedwithparallelcrouch/reach, stillread asconstructedcutout performance. Localroundoverlaps/wristcurl/timingoffsetdidnotresolve thefundamentaldrawnpose/acting problem.','settle':'Subdegree localchest/head/braid movement was added, but after78.3s the resultstillreads largelyheld andneeds strongerlivingweight/settle correction.','fx_limits':'Fourunderlying2.5Dsmoke forms; no evolvingvolumetricselfshadow. Latecoreheat isoff; coldplume texture reuse/dissipation remainartist-reviewitems.','route_assessment':'0.562m localreaction route isabout19times smallerthan original04010.76m; camera stopsnear78.3s. Works asreaction/stop butwouldcreate suddennearfreeze if droppedintoongoingjourney. Stagefuturedeceleration/continuation separately. Existingcomparisonexplicitlylabels differentroutes/cameras.','foot_scope':'Bootcontacts useevaluatedgeometry andsourcegroundray. No blanketpixel-perfectscreen-ground/skatingapproval isclaimed.','decision':'Keep v043 fixed asintegration checkpoint. DoNOTpropagate tofullfilm. Await parent-sealed correctedmotion handoff; nexttest mustkeep thiscamera,travel,world,lighting,FXandframing fixed.','next_test_staging':'notes/world_v016/frozen_staging_v043.json','upload_status':'Localreviewonly. No alternatetransfer orLibraryuploadworkaround attempted.'}
(R/'notes/world_v016/combined_visual_review_v043.json').write_text(json.dumps(review,indent=2));manifest={**export,'status':'PRESERVED INTEGRATION CHECKPOINT - awaiting corrected performance handoff','visual_review':review,'native_media_qa':qa,'preserved_hashes':checks,'staging_snapshot':'notes/world_v016/frozen_staging_v043.json','full_v040_changed':False,'full_trailer_render_started':False,'title_scope_changed':False,'new_upload_attempted':False};(R/'notes/world_v016/integration_checkpoint_v043.json').write_text(json.dumps(manifest,indent=2))
guide=f'''WHEN THE SKY CLEARS - OPEN INTEGRATION CHECKPOINT v043
Status: preserved local5s integration checkpoint, NOT cinematic acceptance.
Global75–80s /frames1801–1920 /120frames /24fps /3840x2160.

4K MOVIE
{export['master']}
Bytes {export['master_bytes']}
SHA256 {export['master_sha256']}

1080 VIEW
{export['view']}

BEFORE / AFTER
{export['before_after']}
Actualpixels label v040original10.76m held route versus v043local0.562m
performance+FX. Same75–80globaltime, DIFFERENT camera/route; not a perfectly
matchedcameraA/B. Nootherdifferent-route comparison should be made for nexttest.

EDITABLE NATIVE
{export['source']}
SHA256 {export['source_sha256']}
Master WTSC_OPEN_5S_MASTER_v043, world WTSC_OPEN_BATTLEFIELD_COMBINED_TRIAL_v043.
NativeScene+packedSound strips give a direct5s4Kexport. Originalmusic75–80;
no additionalexplosion sound design. All usedpaint ispacked; no heldplates/maps.
Cold native reopening/export verified. Native render script:
scripts/render_native_combined_v043.py (choose new outputpath for a rerender).

IMPORTED SEALED SNAPSHOTS
Motionv005 SHA1efe45b192913504cf9007e5616aec77063905fd8771107e9e219173f44548f4.
FXv003 SHAd089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868.
Ownedsnapshots under shots/integration/v042/imports andv043/imports.
Specialist files preserved. Rejectedv001 andfailedv002a collections excluded.

WHAT WAS INSPECTED
40actualdecoded8fpsactor phases, actualshotkeys includingcatch/deeplean/recovery,
hot/coldFXandnative master output. Allmoviefilesdecoded120frames.
Originalmusic samplealignment correlation {qa['native_audio_75_80_correlation']:.6f}.
This does not establish humanartisticacceptance or perfectcontact at everypixel.

WEAKEST ART ISSUE
76.5–77.4s foldedknee/bootandrigidhand/cuff contours plus parallelcrouch/reach
stillread asconstructedcutoutanimation. The post78.3settle stillreads largely
held despite subtle localbreathing. Parent has sent exactcorrectionranges to
the locomotionspecialist. Fourunderlying2.5Dsmoke forms and no volumetricselfshadow
remainFXlimitations. Do NOT propagate thischeckpoint into thefullfilm.

LOCKED NEXT TEST
Await parent-sealed correctedmotion. Clonev043 andkeep camera,0.562mtravel,
world,lighting,FX,framingfixed socharacterperformance changes canbeisolated.
Full120frame numericstaging snapshot: notes/world_v016/frozen_staging_v043.json.
Do notautomaticallystack currentownedposecorrections on an alreadycorrectedsource.
Fullv040 andits unsettledtitle/cut timing remainunchanged. No full-lengthrender,
newdifferent-route comparison, uploadortransferworkaround isauthorized.

RECORDS
notes/world_v016/integration_checkpoint_v043.json
notes/world_v016/combined_visual_review_v043.json
notes/world_v016/combined_media_qa_v043.json
notes/world_v016/combined_trial_build_v043.json
''';(R/'WHEN_THE_SKY_CLEARS_INTEGRATION_CHECKPOINT_v043.txt').write_text(guide,encoding='utf8');print('V043_CHECKPOINT_PRESERVED_WAITING_CORRECTED_MOTION',json.dumps({'source_sha256':export['source_sha256'],'movie_sha256':export['master_sha256'],'review_samples':40}),flush=True)
