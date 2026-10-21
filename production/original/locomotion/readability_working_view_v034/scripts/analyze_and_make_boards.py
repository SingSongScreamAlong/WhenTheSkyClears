import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parents[1];OLD=P.parent/'preferred_walk_consistent_footwear_v033';audit=json.loads((P/'evidence/ACTUAL_GEOMETRY_READABILITY_AUDIT.json').read_text());rows=[]
def mask(a,side):
    r,g,b=[a[:,:,i].astype(float) for i in range(3)]
    return (r>g+45)&(r>b+10)&(r>110) if side=='near' else (b>r+45)&(g>r+30)&(b>110)
for view in ['CLOSE','SHOT']:
    for f in [1,11,20,27]:
        full=np.array(Image.open(P/f'previews/ID_FULL_{view}/{f:04d}.png').convert('RGB'));dark=np.array(Image.open(OLD/f'previews/{view}/{f:04d}.png').convert('RGB'));lum=dark.mean(2)
        for side in ['near','far']:
            iso=np.array(Image.open(P/f'previews/ID_ISO_{side.upper()}_{view}/{f:04d}.png').convert('RGB'));m=mask(full,side);mi=mask(iso,side);ring=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0;ring &=~(mask(full,'near')|mask(full,'far'));cloth=ring&(lum<130);visible=int(m.sum());isolated=int(mi.sum());assert isolated>0;hmedian=float(np.median(lum[m])) if visible else None;cmedian=float(np.median(lum[cloth])) if cloth.any() else None
            rows.append({'view':view,'frame':f,'hand':side,'full_scene_hand_ID_pixels':visible,'isolated_hand_geometry_ID_pixels':isolated,'approx_visible_fraction':visible/isolated,'dark_hand_median_RGB_luma':hmedian,'adjacent_dark_garment_median_luma':cmedian,'dark_value_difference_against_adjacent_garment':abs(hmedian-cmedian) if hmedian is not None and cmedian is not None else None,'garment_fraction_of_adjacent_ring':float(cloth.sum()/max(1,ring.sum())),'projected_geometry_bbox':audit['frames'][str(f)]['hands'][side]['views'][view]})
report={'scope':'Actual full-vs-isolated opaque hand-ID still comparison at unchanged depth, plus dark-pigment contrast. Estimates are raster-sensitive, especially at shot size; not an artistic score.','method':'Distinct near/far hand IDs rendered with all body/cloth present and one hand alone. A lower colored-pixel count in the full scene indicates occlusion. Original hand opacity nodes are1; hand geometry exists. Dark value uses matching final-dark pixels under the visible ID mask and adjacent non-paper pixels.','rows':rows};(P/'evidence/HAND_VISIBILITY_AND_VALUE_MEASUREMENTS.json').write_text(json.dumps(report,indent=2));print(json.dumps([{k:r[k] for k in ['view','frame','hand','approx_visible_fraction','dark_value_difference_against_adjacent_garment']} for r in rows],indent=2))
BG=(228,226,217)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def text(b,xy,s,n=23,c=(24,27,28)):ImageDraw.Draw(b).text(xy,s,font=font(n),fill=c)
def annotated_guide(f,view):
    b=Image.open(P/f'previews/GUIDE_{view}/{f:04d}.png').convert('RGB');d=ImageDraw.Draw(b);r=audit['frames'][str(f)];h=r['hands']['near'];bb=h['views'][view]['bbox_pixels'];bounds=h['bounds_world'];sx=(bb[2]-bb[0])/(bounds[0][1]-bounds[0][0]);sy=(bb[3]-bb[1])/(bounds[2][1]-bounds[2][0]);tx=bb[0]-sx*bounds[0][0];ty=bb[3]+sy*bounds[2][0]
    for side in ['far','near']:
        c=(25,75,165) if side=='far' else (165,61,12);items=[]
        for key in ['shoulder','elbow','wrist','hip','knee','ankle']:
            p=r['joints'][side][key];items.append((key,sx*p[0]+tx,ty-sy*p[2]))
        previous=-100
        for key,x,y in sorted(items,key=lambda v:v[2]):
            yy=max(y-7,previous+(18 if view=='CLOSE' else 21));previous=yy;label=('F ' if side=='far' else 'N ')+key;fs=12 if view=='CLOSE' else 16;w=d.textlength(label,font=font(fs));lx=6 if side=='far' and view=='CLOSE' else 480-8-w if view=='CLOSE' else 415-w if side=='far' else 835;edge=lx+w+3 if side=='far' else lx-3;d.line([(x,y),(edge,yy+7)],fill=c,width=1);d.text((lx,yy),label,font=font(fs),fill=c)
    folder=P/f'previews/ANNOTATED_GUIDE_{view}';folder.mkdir(exist_ok=True);b.save(folder/f'{f:04d}.png');return b
for f in [1,11,20,27]:
    b=Image.new('RGB',(2560,1740),BG);text(b,(18,12),f'V034 | BODY / CLOTH READABILITY DIAGNOSTIC | F{f:02d} | preferred V028 movement unchanged',35)
    text(b,(14,68),'Final dark art',23);text(b,(494,68),'Separated values — actual depth',23);text(b,(974,68),'Joint/cloth guides + HAND X-RAY',23)
    for x,path in [(0,OLD/f'previews/CLOSE/{f:04d}.png'),(480,P/f'previews/WORK_CLOSE/{f:04d}.png')]:b.paste(Image.open(path).convert('RGB'),(x,100))
    b.paste(annotated_guide(f,'CLOSE'),(960,100))
    text(b,(1480,95),'Actual hand meshes, isolated and reframed',28)
    for i,side in enumerate(['near','far']):
        x=1480+i*475;text(b,(x,140),side.upper()+' hand | 98 vertices / 45 faces',23);b.paste(Image.open(P/f'previews/DETAIL_{side.upper()}/{f:04d}.png').convert('RGB'),(x,178));r=next(r for r in rows if r['view']=='SHOT' and r['frame']==f and r['hand']==side);dims=r['projected_geometry_bbox'];text(b,(x,575),f'Shot bbox: {dims["width_pixels"]:.0f} x {dims["height_pixels"]:.0f} px',23);text(b,(x,610),f'Visible ID area: ~{min(100,100*r["approx_visible_fraction"]):.0f}%',23)
    text(b,(1480,670),'Orange circles: near joints | blue diamonds: far joints',24);text(b,(1480,705),'S shoulder  E elbow  W wrist  H hip  K knee  A ankle',24);text(b,(1480,740),'Teal: drawn attachment region | purple: drawn hem',24);text(b,(1480,775),'Guided view projects actual hands forward as x-rays.',23)
    text(b,(18,840),'Actual shot size — 1280 x720 pixels per panel; dark art versus working guides / labelled hand x-ray',29)
    b.paste(Image.open(OLD/f'previews/SHOT/{f:04d}.png').convert('RGB'),(0,890));b.paste(annotated_guide(f,'SHOT'),(1280,890))
    text(b,(18,1640),'Diagnostic colours and overlays only. Original motion, mesh shapes, camera and lighting preserved; final dark source remains separate.',27)
    text(b,(18,1683),'Upper-arm / forearm rig split: near290 /126mm; far282 /134mm. Cloth guides mark existing drawing samples, not physical constraints.',25)
    b.save(P/f'previews/WTSC_v034_Readability_F{f:02d}_Close_and_Shot.png')
    pair=Image.new('RGB',(2560,800),BG);text(pair,(18,12),f'F{f:02d} | Actual1280x720 shot panels | FINAL DARK / LIGHT WORKING VALUES AT TRUE DEPTH | no x-ray',28);pair.paste(Image.open(OLD/f'previews/SHOT/{f:04d}.png').convert('RGB'),(0,65));pair.paste(Image.open(P/f'previews/WORK_SHOT/{f:04d}.png').convert('RGB'),(1280,65));pair.save(P/f'previews/WTSC_v034_True_Depth_Shot_Comparison_F{f:02d}.png')
