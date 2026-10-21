from pathlib import Path
from PIL import Image
import json,sys
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import pose_design as D
old=json.loads((P.parent/'four_pose_silhouette_rebuild_v029/evidence/FOUR_POSE_ANATOMY_AND_SCOPE.json').read_text());new=json.loads((P/'evidence/FOUR_POSE_ANATOMY_AND_SCOPE.json').read_text())
def span(path):
    im=Image.open(path).convert('RGB');xs=[x for x in range(im.width) if max(im.getpixel((x,270)))<100];return xs[-1]-xs[0]+1
widths={'v029':span(P.parent/'four_pose_silhouette_rebuild_v029/previews/CLOSE/0001.png'),'v030':span(P/'previews/CLOSE/0001.png')}
report={'status':'ACTUAL_FOUR_POSE_COMPARISON_FOR_INDEPENDENT_REVIEW_NOT_A_PASS','inspected':['four individual480x720close renders','matched close comparison','matched shot-camera comparison'],'contact_upper_body_scanline':{'y':270,'threshold':'maxRGB<100','width_pixels':widths,'scope':'Pixel-size preservation/readability check only, not artistic acceptance'},
    'loaded_mass_drop_from_contact_mm':{'pelvis':26,'waist':35,'ribcage':33,'neck':37},'rise_from_passing_to_up_mm':{'pelvis':26,'waist':26,'ribcage':30,'neck':30},'passing_sole_clearance_m':{'v029':old['poses'][2]['legs']['far']['sole_clearance'],'v030':new['poses'][2]['legs']['far']['sole_clearance']},'passing_ankle_projection_x_m':{'v029':old['poses'][2]['legs']['far']['ankle'][0],'v030':new['poses'][2]['legs']['far']['ankle'][0]},
    'observed_improvements':['Shoulder/ribcage envelope is visibly fuller around the unchanged head.','Contact/down differ through whole-body mass, not just head/knee.','Knee edges are softer; useful passing leg separation retained.','Passing boot projects clear of support ankle more clearly without increasing minimum sole clearance.','Up combines forefoot roll, extended support and pelvis/ribcage rise.','Rear contact hand separates from hem; front gestures hang more calmly.'],
    'remaining_art':['Coat/ribcage still reads as broad armor-like graphic planes.','Pelvis value bridge may still look like a patch rather than mass.','Passing/up hands partly merge with hem or thigh.','The loaded-down may overstate crouching/fatigue; four static drawings cannot settle this.','Body surface is a structural value block-in against retained painted head/collar/boots.'],
    'no_cycle_or_animation_pass':True,'independent_review_routing':'Through parent, as requested; no direct cross-thread review message attempted.'}
assert widths=={'v029':78,'v030':112}
(P/'evidence/ACTUAL_RENDER_REVIEW.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['observed_improvements','remaining_art','inspected']},indent=2))
