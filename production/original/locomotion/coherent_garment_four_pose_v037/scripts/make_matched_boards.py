from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json
P=Path(__file__).resolve().parents[1];BASE=P.parent/'rigid_limb_continuity_v036/previews';BG='#e8e4db';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',38);F=[1,4,11,20,27];rows=[]
def im(mode,view,f):return Image.open((BASE/view if mode=='SOURCE' else P/'previews'/(mode+'_'+view))/f'{f:04d}.png').convert('RGB')
labels=[('SOURCE','A  v036 retained source'),('CONSTRUCTION','B  Connected coat / construction values'),('PAINTED','C  Same construction / retained fabric')]
for f in F:
 b=Image.new('RGB',(3840,1640),BG);d=ImageDraw.Draw(b);role='CONTACT' if f==1 else 'LOADED DOWN' if f==4 else 'PASSING' if f==11 else 'LOADED RECOVERY' if f==20 else 'EXTRA HAND / HEM CHECK';d.text((25,12),f'F{f:02d} / {role} / identical body pose, head, wrists, limbs and shoes',font=title,fill='#19262c')
 for j,(mode,label) in enumerate(labels):
  x=j*1280;d.text((x+25,70),label,font=font,fill='#19262c');b.paste(im(mode,'CLOSE',f),(x+400,112));d.text((x+25,842),'Original shot camera / native 1280 x 720 pixels',font=small,fill='#19262c');b.paste(im(mode,'SHOT',f),(x,886))
  if f==27:
   detail=im(mode,'CLOSE',f).crop((218,380,282,455)).resize((256,300),Image.Resampling.NEAREST);b.paste(detail,(x+45,425));d.text((x+25,355),'Hand / hem detail',font=font,fill='#19262c');d.text((x+25,392),'4x actual pixels; no overlay',font=small,fill='#19262c')
 d.text((25,1610),'Static garment study only. No hand x-rays, new lighting or movement changes. Four primary poses; F27 checks overlap.',font=small,fill='#19262c');dest=P/'previews'/f'WTSC_v037_Matched_F{f:02d}_Close_and_Shot.png';b.save(dest);rows.append(dest)
big=Image.new('RGB',(3840,220+len(rows)*1640),BG);d=ImageDraw.Draw(big);d.text((25,20),'v037 / Connected garment construction and retained fabric / ACTUAL BLENDER STILL COMPARISON',font=title,fill='#19262c');d.text((25,80),'A: v036 source   B: connected shoulder–ribcage–waist–hem without fabric   C: same surface using the original packed fabric painting',font=font,fill='#19262c');d.text((25,122),'F1 / F4 / F11 / F20 plus F27 hand–hem check. Same character motion and painting assets; garment vertical length preserved.',font=font,fill='#19262c');d.text((25,164),'Five static samples. Inbetweens and moving fabric continuity are not authored or approved. Source trouser-root triangle remains visible at F20.',font=font,fill='#19262c')
for i,p in enumerate(rows):big.paste(Image.open(p),(0,220+i*1640))
out=P/'previews/WTSC_v037_Four_Pose_Garment_Comparison.png';big.save(out)
# Compact clean-art close overview for inspection; all actual source pixels.
b=Image.new('RGB',(1440,5*770),BG);d=ImageDraw.Draw(b)
for i,f in enumerate(F):
 for j,(mode,label) in enumerate(labels):d.text((j*480+10,i*770+8),f'F{f:02d} / '+label.split('  ')[-1],font=small,fill='#19262c');b.paste(im(mode,'CLOSE',f),(j*480,i*770+43))
b.save(P/'previews/WTSC_v037_Close_Overview.png')
full=np.array(Image.open(P/'previews/F27_ID/FULL.png').convert('RGB')).astype(float);iso=np.array(Image.open(P/'previews/F27_ID/ISOLATED.png').convert('RGB')).astype(float)
def mask(a):return (a[:,:,0]>a[:,:,1]+45)&(a[:,:,0]>a[:,:,2]+10)&(a[:,:,0]>110)
m=mask(full);mi=mask(iso);ring=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0;ring &=~m;values={}
for mode in ['SOURCE','CONSTRUCTION','PAINTED']:
 a=np.array(im(mode,'CLOSE',27)).mean(2);dark=ring&(a<130);values[mode]={'near_hand_median_RGB_luma':float(np.median(a[m])),'adjacent_dark_garment_trouser_median_RGB_luma':float(np.median(a[dark])),'ring_dark_fraction':float(dark.sum()/max(1,ring.sum()))}
r={'scope':'Actual opaque hand-ID raster counts and pixel values; not artistic acceptance','F27_full_near_hand_pixels':int(m.sum()),'F27_isolated_near_hand_pixels':int(mi.sum()),'F27_visible_fraction_raster_sensitive':float(m.sum()/mi.sum()),'F27_readability_values':values,'board':{'file':str(out.relative_to(P)),'dimensions':big.size,'bytes':out.stat().st_size},'actual_images_unaltered':'Board layouts paste actual native stills at original dimensions. F27 inset is explicitly labelled4x nearest-neighbor actual pixels. No generated/retouched character artwork.'};(P/'evidence/HAND_HEM_READABILITY_AND_BOARDS.json').write_text(json.dumps(r,indent=2));assert out.stat().st_size<20_000_000 and m.sum()/mi.sum()>.97;print('V037_BOARDS_READY',json.dumps(r),flush=True)
