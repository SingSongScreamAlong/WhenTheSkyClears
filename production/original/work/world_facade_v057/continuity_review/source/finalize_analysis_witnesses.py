from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
O=Path(__file__).parent;render=json.loads((O/'ENVIRONMENT_RENDER_VERIFICATION.json').read_text());analysis=json.loads((O/'TEMPORAL_REGISTRATION_ANALYSIS.json').read_text());rows=render['rows'];byframe={r['frame']:r for r in rows};ims={r['frame']:Image.open(r['file']).convert('RGB') for r in rows}
def extract(im,cx,cy,w,h):return np.asarray(im.transform((w,h),Image.Transform.AFFINE,(1,0,cx-w/2,0,1,cy-h/2),Image.Resampling.BICUBIC),dtype=np.float32)
def ncc(a,b):
 a=a-a.mean();b=b-b.mean();return float((a*b).sum()/(np.linalg.norm(a)*np.linalg.norm(b)+1e-8))
band=[];c=byframe[1225]['anchors']['plaster_shadow']['projected_center'];base=extract(ims[1225],c[0]+48,c[1]+10,128,128)
for r in rows:
 c=r['anchors']['plaster_shadow']['projected_center'];p=extract(ims[r['frame']],c[0]+48,c[1]+10,128,128);d=np.abs(p-base);band.append({'frame':r['frame'],'ncc':ncc(base,p),'mean_absolute_channel_difference':float(d.mean()),'fraction_pixels_channel_difference_above45':float((d.max(2)>45).mean())})
analysis['unobstructed_facade_band']=band;analysis['band_sampling_note']='128x128 camera-tracked area above the source characters. The earlier180x180 diagnostic band intersected their normal foreground occlusion near its lower edge and was replaced by this unobstructed witness.'
changes=render['state_variation_diagnostics'];allowed=all('/node/' not in k and k.startswith('node/') and any(t in k for t in ['/Hue/Saturation/Value/input1/Saturation','/Math.003/input1/Value','/Math.004/input1/Value','fire_beat/output0/Value']) for k in changes)
assert allowed and len(changes)==15
render['fixed_facade_geometry_uv_visibility_all49frames']=True;render['state_variation_classification']='Only inherited saturation and v040 emitter fire-beat node values vary. No object matrix, visibility, UV or newly added facade-node default changes were detected.'
window=[];previous=None;panels={}
for r in rows:
 x0,y0,x1,y1=r['window_review_box'];w=round(x1-x0);h=180;p=extract(ims[r['frame']],(x0+x1)/2,90,w,h);panels[r['frame']]=Image.fromarray(np.uint8(np.clip(p,0,255)))
 if previous is not None:
  d=np.abs(p-previous);window.append({'frame_pair':[r['frame']-1,r['frame']],'adjacent_camera_registered_ncc':ncc(previous,p),'mean_absolute_channel_difference':float(d.mean()),'fraction_pixels_channel_difference_above35':float((d.max(2)>35).mean())})
 previous=p
analysis['upper_window_layer_adjacent_frame_checks']=window
analysis['window_sampling_note']='Native preview upper window band y0..180, above source character occlusion; card-camera registered. Existing3Dwindow parallax is expected and not forced to zero.'
analysis['fixed_facade_geometry_uv_visibility_all49frames']=True;analysis['inherited_material_animation_classified']=True
(O/'ENVIRONMENT_RENDER_VERIFICATION.json').write_text(json.dumps(render,indent=2));(O/'TEMPORAL_REGISTRATION_ANALYSIS.json').write_text(json.dumps(analysis,indent=2))
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
im=Image.new('RGB',(1350,408),'#192124');d=ImageDraw.Draw(im);d.text((16,10),'CAMERA-TRACKED WINDOW LAYERS / native preview pixels',font=font(24,True),fill='white')
for i,f in enumerate([1201,1213,1225,1237,1249]):
 x0,y0,x1,y1=byframe[f]['window_review_box'];y0=max(0,y0);w=round(x1-x0);h=round(y1-y0);a=extract(ims[f],(x0+x1)/2,(y0+y1)/2,w,h);im.paste(Image.fromarray(np.uint8(np.clip(a,0,255))),(i*270+8,78));d.text((i*270+8,48),str(f),font=font(21),fill='#c1cec5')
im.save(O/'WINDOW_LAYER_CONTINUITY_CONTACT_SHEET.jpg',quality=96,subsampling=0)
W=1890;H=1558;im=Image.new('RGB',(W,H),'#192124');d=ImageDraw.Draw(im);d.text((16,12),'ALL 49 FRAMES / CAMERA-TRACKED UPPER WINDOW / native preview pixels',font=font(29,True),fill='white');d.text((16,49),'Above foreground characters; existing depth/parallax and lighting retained. No temporal interpolation.',font=font(23),fill='#c1cec5')
for i,r in enumerate(rows):
 x=(i%7)*270+8;y=90+(i//7)*208;d.text((x,y),str(r['frame']),font=font(18),fill='#c1cec5');im.paste(panels[r['frame']],(x,y+25))
im.save(O/'WINDOW_ALL_49_FRAMES.jpg',quality=96,subsampling=0)
print(json.dumps({'inherited_variation_classified':allowed,'facade_band_min_ncc':min(x['ncc'] for x in band),'facade_band_max_large_difference_fraction':max(x['fraction_pixels_channel_difference_above45'] for x in band),'window_min_adjacent_ncc':min(x['adjacent_camera_registered_ncc'] for x in window),'window_max_large_difference_fraction':max(x['fraction_pixels_channel_difference_above35'] for x in window),'max_track_residual_pixels':max(x['max_residual_shift_preview_pixels'] for x in analysis['detail_tracks'])}))
