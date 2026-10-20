WHEN THE SKY CLEARS / WHOLE-POSE BLOCKING v013 / STOP FOR REVIEW

STATUS AND AUTHORING METHOD
v012 is artistically rejected. This is a separate three-second unpainted study.
The v012 native armatures and plain proxy meshes are retained as infrastructure;
ALL previous motion Actions are removed in this copy. Performance is authored
as15 boy whole-body poses and11 girl whole-body poses on separate key clocks.
Each pose specifies hips, lower trunk, chest, head, feet, wrist targets, elbow
direction and intent together. Existing fixed-length IK only constructs limbs
from those choices. There is no recurring gait, sinusoidal phase generator,
automatic hip-height clamp, walking extension or generated curve polish.
Native channels use CONSTANT interpolation: the deliberate poses/breakdowns
hold and then jump. This is a blocking movie, not final smooth animation.
No painted assets or production files have been changed.

WHAT TO JUDGE BEFORE ANY POLISH
Boy: loss of balance rather than an ordinary step; catching foot placed ahead
of the falling chest; heel arrival before the deep load; near hand braced on
the front thigh; a low gather of the trailing foot before the effortful push;
hips recovering while chest still hangs, followed by brace release and settling.
Girl: interrupt her own stride, brake independently, collect the trailing foot,
put BOTH heels down by27, then incline toward him and keep an offered hand
available while following his rise. There is no hand clasp or helping force.
The hand/thigh brace is a proxy staging cue, not a calibrated contact/force solve.
Source reference and authoring notes are in reference/REFERENCE_OBSERVATIONS.txt.

LOCAL CLOCK / EDITABILITY
72frames at24fps =3seconds. Frame1=0s, frame72=2.958333s, boundary73=3s.
Boy keys:1,7,10,13,16,19,22,26,32,38,43,49,56,64,72.
Girl keys:1,8,12,17,22,27,34,43,54,64,72.
Boy toe interruption10, clear imbalance13, catch-foot breakdown16,
heel19, load22, head/shoulder counter-action26, foot gather32,
effort/preload38, push43, hips/chest follow49, release56, supported pause64.
Girl brake12, controlled load17, trailing-foot collection22,
both heels flat27..72, attend34, follow his rise43/54, offer softens64.
End holds the supported pause; there are no continuation walking steps.

Open native/WTSC_Whole_Pose_Blocking_v013.blend in verified Blender5.2.2LTS,
buildd13f752e3b9c. Native bone lengths and bindings are retained from v012.
Append WTSC_WHOLE_POSE_BLOCKING_v013 into an EMPTY review scene if needed:
44objects,2armatures, plain bound meshes, no camera/light or external image.
Set24fps,1..72, metre units and scale1. Root Object location and native pose
channels belong together. Existing action curves hold the authored key poses;
do not spline them automatically before the blocking review.
Timeline markers and evidence/authored_story_poses.json retain all intentions.
scripts/story_poses.py is the complete pose recipe; build_blocking.py applies
it to a new copy of the retained rig. Both are also embedded as native Texts.
Rebuild scripts refer to the original v012 rig in this project; the saved
native itself opens without external assets or scripts.

HEAD-ATTENTION SHORTHAND
At girl key12, one stepped local-X reflection changes the plain proxy from
right to left profile. Its head volume, nose cue and braid cue remain attached.
There is NO edge-on flat-card rotation, interpolated turnaround or v008 reuse.
This is a two-profile BLOCKING SUBSTITUTION to inspect attending intent.
It does not validate a painted left profile, hair/braid design or turn continuity.
Do not transplant the reflected proxy head into production or call this a
solved painted head turn. The source painting and rejected patch stay untouched.

CAMERAS / ROUTES / INTEGRATION LIMIT
TEST | INSPECTION: fixed orthographic width4.8m; TEST | SHOT_SIZE:10.4m,
approximately original shot character size. Both are fixed atX=.94,Y=-12,Z=.8.
No camera follow/travel smoothing is used to sell these poses. Floor ticks and
the4cm test obstacle remain world-fixed. Primary previews have no pose labels.
evidence/world_motion_samples.csv lists the exposed pose, local clock, root
and support state every frame. These are stepped blocking routes only.
Do not combine with production DISTANCE_CURVE or map72 frames silently into
75..80s. This is not a replacement production shot/travel contract.

ACTUAL REVIEW AND LIMITS
Inspect WTSC_v013_Whole_Pose_Blocking_3s.mp4 and the separate shot-size movie.
WTSC_v013_INSPECTION_Key_Poses.jpg and WTSC_v013_SHOT_SIZE_Key_Poses.jpg show
the important story keys, at actual cropped pixel scale for their respective
cameras. Captions name intentions; the unlabeled movies must carry the read.
Technical checks establish native binding, fixed lengths, floor/contact holds,
constant exposures, fresh append and source preservation. They do not prove
naturalness, appealing acting, dynamic balance or artistic acceptance.
Continuous/full-speed playback is unavailable to the agent/reviewer. Actual
decoded frames and chronological progression are inspected; normal-speed
artistic verification is NOT claimed. Timing remains provisional.
Stepped jumps, the abrupt profile substitution, simplified masses and proxy
surface intersections need to be judged as blocking limitations, not polished
animation. No facial acting, clothing, hair dynamics or lateral balance solved.

STOPPING POINT
This handoff stops at whole-pose blocking for review. No curve polish, new walk,
paint, production integration, duration/music/title/FX changes are included.
If the story poses fail, change them before adding inbetweens or smoothing.
