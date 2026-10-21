from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math
O=Path(__file__).parent;q=json.loads((O/'ENVIRONMENT_RENDER_VERIFICATION.json').read_text());rows=q['rows'];assert len(rows)==49
images={r['frame']:Image.open(r['file']).convert('RGB') for r in rows};rowmap={r['frame']:r for r in rows};ref=1225
def patch(im,center,size,dx=0,dy=0):
 cx,cy=center;return np.asarray(im.transform((size,size),Image.Transform.AFFINE,(1,0,cx-size/2+dx,0,1,cy-size/2+dy),Image.Resampling.BICUBIC),dtype=np.float32)
def ncc(a,b):
 aa=a-a.mean();bb=b-b.mean();return float((aa*bb).sum()/(np.linalg.norm(aa)*np.linalg.norm(bb)+1e-8))
measure=[]
for name,anchor in rowmap[ref]['anchors'].items():
 size=anchor['patch_size'];base=patch(images[ref],anchor['projected_center'],size);checks=[]
 for r in rows:
  xy=r['anchors'][name]['projected_center'];assert size/2<=xy[0]<=1280-size/2 and size/2<=xy[1]<=720-size/2,(name,r['frame'],xy)
  current=patch(images[r['frame']],xy,size);best=(ncc(base,current),0.,0.)
  # Track residual displacement after the actual camera projection. This is
  # an analysis-only resampling of rendered pixels, not a texture/image edit.
  for dy in np.arange(-1,1.001,.25):
   for dx in np.arange(-1,1.001,.25):
    score=ncc(base,patch(images[r['frame']],xy,size,float(dx),float(dy)))
    if score>best[0]+1e-7:best=(score,float(dx),float(dy))
  checks.append({'frame':r['frame'],'camera_registered_ncc':ncc(base,current),'mean_absolute_channel_difference':float(np.abs(base-current).mean()),'best_ncc':best[0],'residual_translation_preview_pixels':[best[1],best[2]]})
 measure.append({'name':name,'patch_size':size,'min_camera_registered_ncc':min(c['camera_registered_ncc'] for c in checks),'max_mean_absolute_channel_difference':max(c['mean_absolute_channel_difference'] for c in checks),'max_residual_shift_preview_pixels':max(math.hypot(*c['residual_translation_preview_pixels']) for c in checks),'checks':checks})
# A larger unobstructed facade band catches local flashes or gaps beyond the
# five individual detail tracks. It is above the unchanged source characters.
band=[];sz=180;refcenter=rowmap[ref]['anchors']['plaster_shadow']['projected_center'];refcenter=[refcenter[0]+48,refcenter[1]+35];base=patch(images[ref],refcenter,sz)
for r in rows:
 center=r['anchors']['plaster_shadow']['projected_center'];center=[center[0]+48,center[1]+35];a=patch(images[r['frame']],center,sz);d=np.abs(base-a);band.append({'frame':r['frame'],'ncc':ncc(base,a),'mean_absolute_channel_difference':float(d.mean()),'fraction_pixels_channel_difference_above45':float((d.max(2)>45).mean())})
xs=np.array([r['camera_matrix'][0][3] for r in rows]);steps=np.diff(xs)
result={'status':'ANALYSIS COMPLETE; visual review pending','frame_count':49,'source_fps':24,'preview_dimensions':[1280,720],'source_native_unchanged':q['source_unchanged'],'source_objects_actions_children_timing_preserved':q['source_objects_actions_children_timing_preserved'],'fixed_facade_and_window_signature_unchanged_all49frames':q['fixed_facade_and_window_signature_unchanged_all49frames'],'new_character_motion_authored':False,'camera_x_step_range_world_units':[float(steps.min()),float(steps.max())],'camera_max_step_change_world_units':float(np.abs(np.diff(steps)).max()),'detail_tracks':measure,'unobstructed_facade_band':band,'sampling_notes':'All49rendered frames compared after actual camera projection. Normal interpolation/AA can vary edge pixels. Residual search is quarter-preview-pixel within±1;visual contact sheets and layer witnesses reviewed separately.'}
(O/'TEMPORAL_REGISTRATION_ANALYSIS.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'tracks':[{k:v for k,v in m.items() if k!='checks'} for m in measure],'band_min_ncc':min(b['ncc'] for b in band),'band_max_large_difference_fraction':max(b['fraction_pixels_channel_difference_above45'] for b in band),'camera_step_range':result['camera_x_step_range_world_units']}))
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
sample=list(range(1201,1250,6));im=Image.new('RGB',(1326,918),'#192124');d=ImageDraw.Draw(im);d.text((18,12),'ENVIRONMENT CONTINUITY REVIEW / v057 / original24fps',font=font(27,True),fill='white');d.text((18,49),'49 consecutive frames; existing character animation unchanged. Sampled compositions below.',font=font(20),fill='#c1cec5')
for i,f in enumerate(sample):
 x=12+(i%3)*438;y=91+(i//3)*274;d.text((x,y),f'FRAME {f} / source {(f-1)/24:.3f}s',font=font(20),fill='#c1cec5');im.paste(images[f].resize((426,240),Image.Resampling.LANCZOS),(x,y+27))
im.save(O/'ENVIRONMENT_COMPOSITION_CONTACT_SHEET.jpg',quality=95,subsampling=0)
im=Image.new('RGB',(1350,408),'#192124');d=ImageDraw.Draw(im);d.text((16,10),'CAMERA-TRACKED WINDOW LAYERS / native preview pixels',font=font(24,True),fill='white')
for i,f in enumerate([1201,1213,1225,1237,1249]):
 r=rowmap[f];x0,y0,x1,y1=r['window_review_box'];w=round(x1-x0);h=round(y1-y0);c=images[f].transform((w,h),Image.Transform.AFFINE,(1,0,x0,0,1,y0),Image.Resampling.BICUBIC);im.paste(c,(i*270+8,78));d.text((i*270+8,48),str(f),font=font(21),fill='#c1cec5')
im.save(O/'WINDOW_LAYER_CONTINUITY_CONTACT_SHEET.jpg',quality=96,subsampling=0)
im=Image.new('RGB',(878,570),'#192124');d=ImageDraw.Draw(im);d.text((12,8),'CAMERA-TRACKED FACADE DETAILS / native preview pixels',font=font(23,True),fill='white')
for j,name in enumerate(rowmap[ref]['anchors']):
 y=76+j*95;d.text((12,y+20),name,font=font(19),fill='#c1cec5')
 for i,f in enumerate(sample):
  anchor=rowmap[f]['anchors'][name];a=patch(images[f],anchor['projected_center'],anchor['patch_size']);c=Image.fromarray(np.uint8(np.clip(a,0,255)));x=182+i*76;im.paste(c,(x,y));d.text((x,y+67),str(f),font=font(14),fill='#c1cec5')
im.save(O/'FACADE_TRACKED_DETAILS_CONTACT_SHEET.jpg',quality=96,subsampling=0)
