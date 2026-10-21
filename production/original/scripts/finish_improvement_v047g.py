"""Seal the reviewed working checkpoint and candid next-pass findings."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047'
def read(name):return json.loads((N/name).read_text())
def write(name,data):(N/name).write_text(json.dumps(data,indent=2)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
build=read('build_v047g.json');qa=read('media_qa_v047g.json');cold=read('cold_verification_v047g.json');assembly=read('assembly_v047g.json')
assert qa['actual_frames_decoded']==120 and qa['resolution']==[3840,2160]
assert max(cold['all120_staging_errors'].values())==0
for key in ['native','movie4K','view1080p']:assert sha(qa[key]['path'])==qa[key]['sha256']
base=json.loads((R/'notes/world_v016/motion_trial_build_v046.json').read_text())
for path,expected in base['preserved_inputs'].items():assert sha(path)==expected,path
review={
 'completed_utc':datetime.now(timezone.utc).isoformat(),
 'selected_working_revision':'v047g',
 'result':'Visible head/hand/foreground gains, retained as a working refinement. The trailer is not artistically finished.',
 'review_method':{
  'first_review':'Actual native4K key crops, full1901 image, all40 chronological actor samples,12 consecutive turn frames and8 whole-shot samples from v047f.',
  'followup':'Actual v047g1847/1848 native4K key crops, changed tail24 chronological samples, six turn frames1845..1850 and eight whole-shot samples. Unchanged prefix key images1842/1844/1846 match v047f exactly.',
  'before_after':'Actual native4K head and lower-ground before/after comparisons.',
  'limits':'Chronological decoded-frame review and full-file decode; no claim of continuous normal-speed artistic playback or full-trailer acceptance.'
 },
 'iterations':[
  {'revision':'v047a','finding':'New turn drawings improve head readability; added round arm caps look mechanical.','action':'Caps rejected.'},
  {'revision':'v047b','finding':'Earlier backward hand silhouettes improve, but late hand correction weakens offered-touch read.','action':'Limit correction window.'},
  {'revision':'v047c','finding':'Early direction corrections retained; original later hand orientations restored. Tapered cuff/wrist shapes read cleaner.','action':'Retained as character foundation.'},
  {'revision':'v047d','finding':'New bank earth detail and rooted wind wisps improve foreground variety; repeat row remains.','action':'Inspect the upper ground layers.'},
  {'revision':'v047e','finding':'Bank alpha change does not solve repeated plants embedded in the lower path paint.','action':'Do not select; return to v047d and correct the path layer.'},
  {'revision':'v047f','finding':'Lower path and bank repeats substantially reduced. Full4K movie reveals a hair-shape/texture pop when returning to older reflected profile at1848.','action':'Generate and register a matching true-left-profile painting.'},
  {'revision':'v047g','finding':'Matching profile carries the turn style into the late pose, with subtle damped braid settle.','action':'Selected working checkpoint after native keys and changed-tail review.'}
 ],
 'improvements':[
  'Four original imagegen head paintings: right quarter, frontal, left quarter, matching left profile. Original disc is excluded.',
  'Painted turn exposed on2s at1842..1847, matching profile1848..1920. Editable contour meshes, four native Grease Pencil contour guides and SVG outlines retained.',
  'Backward early hand silhouettes redirected about fixed wrists; corrections fade out at local67..80 to preserve the late light offered touch. Forearm and cuff outlines tapered.',
  'Bespoke fixed-projection bank/lower-path paint reduces repeated plant borders and adds quieter, varied soil detail.',
  'Nine fixed roots with53 native animated blade curves; up to6.38mm sampled tip motion, no root drift.'
 ],
 'remaining_work':[
  'Body/shoulder/elbow construction still reads planar and angular. Stumble, weight and recovery need stronger whole-body acting before production propagation.',
  'Turn is still a quick sequence of replacement drawings; some facial/skin-value variation and secondary hair continuity need further craft review.',
  'A few clipped lower-path leaf tips/paint transitions remain; foreground is improved, not fully finished.',
  'Existing FXv003 remains too cloud-like; larger impulse/expansion, ground damage, readable debris landings and depth remain needed.',
  'FXv013 compact study was inspected but is too small/subdued to replace the main eruption. It remains unaccepted and unintegrated.',
  'Later hands remain a light offered touch, not a load-bearing clasp. Restart/first new step remains unresolved.',
  'Other village/woods/school/camp sections have not received this new pass; full trailer remains at preserved v040.'
 ],
 'artistic_acceptance':False,'full_trailer_propagated':False
}
write('visual_review_v047g.json',review)
qa['visual_inspection_complete']=True;qa['visual_review']=str(N/'visual_review_v047g.json');qa['review_scope']=review['review_method'];write('media_qa_v047g.json',qa)
f=read('media_qa_v047f.json');f['visual_inspection_complete']=True;f['superseded_for_selected_review']='v047g matching-profile correction';write('media_qa_v047f.json',f)
assets=json.loads((R/'characters/head_turn_v047/provenance.json').read_text());assets['purpose']='Four matching head drawings for the existing charcoal girl, including turn intermediates and the new continuing left profile.';(R/'characters/head_turn_v047/provenance.json').write_text(json.dumps(assets,indent=2))
checkpoint={'status':'Completed review/fix cycle; v047g is the selected working checkpoint, still artistically unfinished.',
 'native':qa['native'],'movie4K':qa['movie4K'],'view1080p':qa['view1080p'],
 'resolution':[3840,2160],'fps':24,'frames':120,'global_range':[1801,1920],'seconds':5,
 'review':str(N/'visual_review_v047g.json'),'cold_verification':str(N/'cold_verification_v047g.json'),
 'assembly':str(N/'assembly_v047g.json'),'media_qa':str(N/'media_qa_v047g.json'),
 'prompts_and_reuse':str(N/'reuse_and_prompts.json'),
 'imagegen_assets':[item['path'] for item in assets['assets']]+[build['foreground']['source']],
 'native_paint_resolution_limit':'Head and bank source paintings are below4K; the output frames/movie are natively3840x2160.',
 'unchanged_inputs_checked':len(base['preserved_inputs']),
 'owned_render_jobs_remaining':0,'artistic_acceptance':False,'full_trailer_propagated':False,
 'next_priorities':['Whole-body weight and shoulder/elbow acting','Main explosion and persistent ground interaction','Remaining paint transition tips','Other trailer environments']}
write('checkpoint_v047g.json',checkpoint)
write('render_status.json',{'phase':checkpoint['status'],'selected_revision':'v047g','owned_render_jobs_remaining':0,
 'native':qa['native']['path'],'movie4K':qa['movie4K']['path'],'view1080p':qa['view1080p']['path'],
 'artistic_acceptance':False,'full_trailer_propagated':False})
oldpath=R/'notes/world_v016/integration_hold_after_v046.json';old=json.loads(oldpath.read_text());old['current_refinement']=qa['native']['path'];old['current_refinement_receipt']=str(N/'checkpoint_v047g.json');oldpath.write_text(json.dumps(old,indent=2))
guide=f"""WHEN THE SKY CLEARS -- REFINEMENT v047g

CURRENT WORKING CHECKPOINT
{qa['native']['path']}
Master scene: {build['master_scene']}
World scene: {build['world_scene']}
Saved defaults3840x2160,24fps, global1801-1920 /75-80seconds.

ACTUAL4K FIVE-SECOND REVIEW (10.70MB)
{qa['movie4K']['path']}
Small viewing copy1080p (2.83MB):
{qa['view1080p']['path']}
Both movies decoded120actual frames. Original75-80second music retained.
This is the five-second battlefield refinement, not the complete trailer.
The4K review combines47 unchanged actual nativeF frames and73 newly rendered
nativeG frames; three native prefix key renders match exactly. No scaling or
interpolated frames. The small viewing copy is downsampled from that4K movie.

CHANGES KEPT AFTER REVIEW / FIX / RENDER / REVIEW
Four original built-in GPT imagegen head paintings replace the disc and carry
the turn into a matching profile. Painterly fills render on editable native
contour meshes; four real Grease Pencil outline guides are retained as hidden
editing layers, alongside SVG outlines. These guides are not the visible paint.
Early hands that pointed into forearms are redirected at fixed wrists. Later
offered-touch orientations are retained. Tapered forearms/cuffs replace the
failed circular-cap idea, which was rejected after actual key review.
New world-fixed bank and lower-path paint reduces repetitive leaf rows. Nine
rooted tufts /53 native blade curves add subtle independently phased wind.
No root drift; camera, route, existing FX clock/light and foot actions preserved.

WHAT STILL NEEDS WORK
Body weight/acting and angular shoulder/elbow constructions remain below the
intended cinematic target. The turn is a short replacement-drawing sequence,
not final polished acting. Some facial-value variation and tiny clipped path
leaf tips remain. Main FXv003 is still too cloud-like and lacks a strong ground
disturbance. The inspected compactFXv013 study is not a suitable principal
blast replacement. No new FX version has been integrated.
Late touch is light offered contact, not a load-bearing grip. Restart remains
unresolved. Other village/woods/school/camp sections await their next pass.
The full v040 trailer and older checkpoints remain preserved; no full-film
propagation or title/FPS/duration change was made. Artistic acceptance is false.

REVIEW / SOURCE PROVENANCE
{N/'visual_review_v047g.json'}
{N/'checkpoint_v047g.json'}
{N/'cold_verification_v047g.json'}
{N/'reuse_and_prompts.json'}
Source paintings and original generation paths/hashes:
{R/'characters/head_turn_v047/provenance.json'}
{R/'sets/refinement_v047/Foreground_Bank_Paintover_v047.png'}
Generation returned sub4K texture assets; actual output is native4K.
Review used decoded chronological samples and actual4K crops, not a claim of
continuous normal-speed artistic playback. Technical checks are not art approval.

ACTUAL COMPARISONS / CHRONOLOGY
{R/'renders/refinement_v047g/review_evidence'}
"""
path=R/'WHEN_THE_SKY_CLEARS_REFINEMENT_v047g.txt';path.write_text(guide)
print(json.dumps({'status':checkpoint['status'],'guide':str(path),'movie4K':qa['movie4K'],'native':qa['native']},indent=2))
