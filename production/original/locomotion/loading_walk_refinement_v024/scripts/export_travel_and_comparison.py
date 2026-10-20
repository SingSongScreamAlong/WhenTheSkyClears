from pathlib import Path
import csv,json,math,hashlib
from PIL import Image,ImageDraw,ImageFont
import motion_model as M
P=Path(__file__).resolve().parents[1]
rows=[]
for i in range(373):
    q=i/4;r=M.evaluate(q)
    row={'native_frame_30fps':q+1,'elapsed_seconds':q/30,'root_x_m':r['D'],'hip_world_x_m':r['H'][0],'hip_world_z_m':r['H'][1],'pelvis_rad':r['pelvis'],'chest_rad':r['chest'],'head_rad':r['head']}
    for side in ['near','far']:
        d=r['feet'][side];meta=d['meta']
        row.update({side+'_mode':d['mode'],side+'_ankle_world_x_m':d['A'][0],side+'_ankle_world_z_m':d['A'][1],side+'_boot_pitch_rad':d['angle'],side+'_sole_clearance_m':d['clearance'],side+'_anchor_x_m':meta.get('anchor_xz',[None,None])[0],side+'_sole_vertex':meta.get('vertex',-1),side+'_reach_margin_m':r['margins'][side]})
    rows.append(row)
with (P/'V024_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
contract={'units':'metres, seconds, radians','fps':30,'native_time':'q=frame-1','period_frames':31,'period_seconds':31/30,'stride_m':M.STRIDE,'speed_m_per_second':M.STRIDE*30/31,'travel':'D(q)=stride*q/31, positive X, unwrapped; one metre is one Blender unit','native_frames_authored':[1,94],'preview_frames':[1,93],'placement':'Identity coordinates in this native. Root travel is separate from world-space sole goals. Transform every imported hierarchy and every world foot goal through one common static placement transform. Do not move only the travel empty.','centred_stage':'If characters are held centred, subtract D(q) from the common character placement AND from world geometry/ground placement as appropriate to the chosen coordinate system. Equivalent stationary character pose has foot x=A_x(q)-D(q); ground/landscape translates -D(q). Do not add a second root displacement.','cycle_extension':'After one period evaluate local pose at q mod31 and add n*stride to root and world sole goals. For centred/world scrolling use an unwrapped D. Native F94 is the third bookend; the movie ends at F93. Timeline wrapping93->1 resets world travel and ruler marks.','production_mapping':'No production mapping or recovery-to-walk seam is approved. Do not paste this straight onto75-80s. Choose the seam contact, then time offset q=30*(t-t0)+q0 and apply D(q)-D(q0) consistently. Any retiming must retime all controls, sole goals and cloth together.'}
(P/'evidence/TRAVEL_CONTRACT.json').write_text(json.dumps(contract,indent=2))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
board=Image.new('RGB',(1440,1260),'#eee9dd');draw=ImageDraw.Draw(board)
draw.text((12,8),'v023 preserved -> v024 | exact same-clock normal-speed frames',font=font,fill='#292622')
for j,frame in enumerate([3,10,19,26]):
    for i,(ver,folder) in enumerate([('v023','continuous_coat_walk_v023'),('v024','loading_walk_refinement_v024')]):
        im=Image.open(P.parent/folder/'previews'/'CLOSE'/f'{frame:04d}.png').convert('RGB')
        # Comparison only: exact existing render resized uniformly, no paint changes.
        x=j*360;y=44+i*600;board.paste(im,(x,y+28));draw.text((x+8,y),f'{ver} F{frame}',font=small,fill='#292622')
board.save(P/'previews/WTSC_v023_v024_SAME_CLOCK_COMPARISON.jpg',quality=95)
print(json.dumps({'csv_rows':len(rows),'stride_m':M.STRIDE,'speed_m_s':contract['speed_m_per_second'],'comparison':'previews/WTSC_v023_v024_SAME_CLOCK_COMPARISON.jpg'}))
