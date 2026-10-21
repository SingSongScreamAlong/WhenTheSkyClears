from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,json
P=Path(__file__).resolve().parents[1];rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader((P/'evidence/BARE_BODY_AND_FOOT_ARCS.csv').open())]
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);board=Image.new('RGB',(1920,792),'#eee9dd');d=ImageDraw.Draw(board)
for i in range(16):
    x=(i%8)*240;y=(i//8)*396;board.paste(Image.open(P/f'previews/BARE_CLOSE/{i+17:04d}.png').convert('RGB').resize((240,360)),(x,y+36));d.text((x+7,y+6),'F'+str(i+17),font=font,fill='#292622')
board.save(P/'evidence/BARE_BODY_ALL_16_FRAMES.jpg',quality=95)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="840" viewBox="0 0 1200 840"><rect width="1200" height="840" fill="#eee9dd"/><g font-family="sans-serif" font-size="18" fill="#292622"><text x="20" y="30">v025 bare-body paths | 61 quarter-frame samples | root travel removed | metres</text>']
for panel,(names,title) in enumerate([(['pelvis','sternum'],'Torso'),(['knee_near','knee_far'],'Knees'),(['near_heel','near_toe'],'Near actual boot'),(['far_heel','far_toe'],'Far actual boot')]):
    x0=40+(panel%2)*600;y0=80+(panel//2)*370;xx=[r[n+'_x'] for r in rows for n in names];zz=[r[n+'_z'] for r in rows for n in names];xmin,xmax=min(xx),max(xx);zmin,zmax=min(zz),max(zz)
    svg.append(f'<text x="{x0}" y="{y0-15}">{title}: X[{xmin:.3f},{xmax:.3f}] Z[{zmin:.3f},{zmax:.3f}]</text><rect x="{x0}" y="{y0}" width="510" height="280" fill="none" stroke="#aaa397"/>')
    for j,n in enumerate(names):
        color=['#84613f','#366f80'][j];coords=[(x0+15+480*(r[n+'_x']-xmin)/max(.001,xmax-xmin),y0+265-250*(r[n+'_z']-zmin)/max(.001,zmax-zmin)) for r in rows];poly=' '.join(f'{x:.2f},{y:.2f}' for x,y in coords);svg.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.5"/><text x="{x0+j*250}" y="{y0+309}" fill="{color}">{n}</text>');svg.extend(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2" fill="{color}"/>' for x,y in coords)
svg.append('<text x="20" y="815">Measured paths and frame review; not proof of natural weight/cadence at continuous playback.</text></g></svg>');(P/'evidence/BARE_BODY_AND_FOOT_ARCS.svg').write_text(''.join(svg))
stats={key:{'minimum':min(r[key] for r in rows),'minimum_frame':min(rows,key=lambda r:r[key])['frame'],'maximum':max(r[key] for r in rows)} for key in ['pelvis_z','sternum_z','knee_near_z','knee_far_z']};(P/'evidence/BARE_BODY_ARC_OBSERVATIONS.json').write_text(json.dumps({'samples':len(rows),'stats':stats,'scope':'Measured paths and viewed bare-body poses; no claim of believable weight at playback speed'},indent=2));print(json.dumps(stats))
