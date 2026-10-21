import json,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1]
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',23);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
paths={}
for old,new in [('WTSC_Girl_Head_Turn_Patch_v008.blend','WTSC_Girl_Head_Turn_STUDY_v008_NOT_APPROVED.blend'),('WTSC_Head_Patch_v008_Critical_Comparison_Copy.blend','WTSC_Head_STUDY_v008_Comparison_NOT_APPROVED.blend')]:
 a=P/'native'/old;b=P/'native'/new
 if a.exists():a.rename(b)
 paths[old]=str(b)
sheet=Image.new('RGB',(1220,1320),(22,24,27));d=ImageDraw.Draw(sheet);d.text((12,10),'HEAD-TURN STUDY REJECTED / REFERENCE NEEDED / NOT FOR INTEGRATION',font=font,fill=(255,176,148))
for row,f in enumerate([1844,1845]):
 y=50+row*632
 for col,(folder,label) in enumerate([('v046_before','v046 disc defect'),('v008_after','v008 study - hair/braid fail')]):
  x=col*610;d.text((x+8,y),f'{label} / {f} / {(f-1)/24:.3f}s',font=small,fill=(234,232,221));im=Image.open(P/f'previews/{folder}/{f}.png').convert('RGB');sheet.paste(im,(x,y+30))
sheet.save(P/'HEAD_TURN_STUDY_v008_REFERENCE_NEEDED.jpg',quality=95)
continuity=Image.new('RGB',(4*610,680),(22,24,27));d=ImageDraw.Draw(continuity);d.text((12,8),'REJECTED DRAWING STUDY / ACTUAL EEVEE NATIVE4K BORDER PIXELS / NO FULL MOVIE',font=font,fill=(255,176,148))
for col,f in enumerate([1843,1844,1845,1846]):
 x=col*610;d.text((x+8,43),f'{f} / {(f-1)/24:.3f}s',font=small,fill='white');continuity.paste(Image.open(P/f'previews/v008_after/{f}.png').convert('RGB'),(x,72))
continuity.save(P/'HEAD_TURN_STUDY_v008_Chronology.jpg',quality=95)
pixel=[]
import numpy as np
for f in [1843,1846]:
 a=np.array(Image.open(P/f'previews/v046_before/{f}.png'));b=np.array(Image.open(P/f'previews/v008_after/{f}.png'));pixel.append({'frame':f,'max_channel_difference':int(np.max(np.abs(a.astype(int)-b.astype(int)))),'changed_pixel_count':int(np.count_nonzero(np.any(a!=b,axis=2)))})
critical=json.loads((P/'evidence/critical_verification.json').read_text());build=json.loads((P/'evidence/build_patch.json').read_text());source=Path(critical['source']);native_source=Path(build['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==critical['source_sha256'];assert hashlib.sha256(native_source.read_bytes()).hexdigest()==build['source_sha256']
status={'status':'NOT FIXED - REJECTED STUDY; additional drawing reference required. No production-ready patch released.','blocked_action':'Release/apply a faithful girl head-turn correction for global frames1844 and1845(local44,45).','target':'Girl passing-head mesh in the accepted v007 performance on production v046.','reason':'Profile/reflected-profile source paint does not supply the missing quarter-view hairline, cheek/jaw and braid attachment. Authored native face studies removed the disc but introduced cropped-cap/attachment design drift; they failed visual review.','action_state':'Pending additional matching head drawing reference; not a permission denial and no uncertain production write.','needed_reference':['Three-quarter view between the existing right profile and front view, matching original charcoal girl, swept fringe, skull/cheek/jaw proportions and braid root','Corresponding three-quarter view toward the boy/left profile, with the same scale and resolved fringe/braid attachment'],'completed':['Inspected independent native4K exposure evidence and productionv046 read-only','Built editable native two-frame face/hair/braid study and narrow in-memory apply helper','Rendered only four before/after native4K EEVEE head-border crops; no whole movie rerender','Verified every rig bone matrix,camera and root travel across all120 frames unchanged; only passing-head mesh data changed in isolated comparison copy'],'all120_unchanged_errors':critical['all120_frame_unchanged_errors'],'unchanged_adjacent_frame_pixels':pixel,'production_preserved':{'path':str(source),'sha256':critical['source_sha256']},'accepted_v007_preserved':{'path':str(native_source),'sha256':build['source_sha256']},'rejected_study_paths':paths,'comparison':'HEAD_TURN_STUDY_v008_REFERENCE_NEEDED.jpg','scope_remaining_unchanged':'Hands remain the accepted light offered touch. Restart remains unresolved. No foot/root/body/FX/full-trailer changes.','next_step':'Author/obtain the two matching quarter-view head references, then replace only local44/45 head drawings. Stop this correction until those views are available.'}
(P/'evidence/STATUS_REFERENCE_REQUIRED.json').write_text(json.dumps(status,indent=2))
(P/'STATUS_REFERENCE_REQUIRED.txt').write_text('NOT FIXED - REJECTED DRAWING STUDY. DO NOT INTEGRATE.\n\nThe polygonal disc was replaced in an isolated study, but the replacement hairline and braid attachment failed design-fidelity review. No production-ready patch is released.\n\nNeeded: two matching three-quarter head drawings for local44 and45(global1844/1845), preserving this girl\'s swept charcoal fringe, skull/cheek/jaw shape, eye style and braid root. Existing right-profile43 and left-profile46 are the boundary references.\n\nProductionv046 and acceptedv007 hashes are unchanged. All120 rig-bone matrices,camera and root travel were unchanged in the study. Only head crops were rendered; no full movie. Hands, restart and all other accepted work remain untouched.\n\nSee HEAD_TURN_STUDY_v008_REFERENCE_NEEDED.jpg and evidence/STATUS_REFERENCE_REQUIRED.json. Native files named STUDY_NOT_APPROVED are retained for inspection, not integration.\n')
evidence=[P/'STATUS_REFERENCE_REQUIRED.txt',P/'HEAD_TURN_STUDY_v008_REFERENCE_NEEDED.jpg',P/'HEAD_TURN_STUDY_v008_Chronology.jpg',P/'evidence/STATUS_REFERENCE_REQUIRED.json',P/'evidence/critical_verification.json',P/'evidence/build_patch.json']
zip_path=P/'WTSC_Head_Turn_v008_REJECTED_STUDY_EVIDENCE.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in evidence:z.write(p,p.relative_to(P))
print('V008_STOPPED_REFERENCE_REQUIRED',json.dumps({'evidence':str(zip_path),'bytes':zip_path.stat().st_size,'status':status['status'],'unchanged_adjacent_frames':pixel}),flush=True)
