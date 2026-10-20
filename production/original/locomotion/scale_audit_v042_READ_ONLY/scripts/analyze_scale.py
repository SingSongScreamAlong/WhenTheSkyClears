from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];L=P.parent;A=json.loads((P/'evidence/NATIVE_SCALE_AUDIT.json').read_text());VERS=['v028','v036','v039','v040','v041'];FONT='C:/Windows/Fonts/segoeui.ttf'
def label(d,p,s,n=22,fill='#e7e6dc'):d.text(p,s,font=ImageFont.truetype(FONT,n),fill=fill)
def stats(path):
 im=Image.open(path);ar=np.array(im.getchannel('A')).astype(float)/255;Y,X=np.indices(ar.shape);b={}
 for q in [.1,.5,.9]:
  yy,xx=np.nonzero(ar>=q);b[str(q)]=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None
 return {'file':str(path.relative_to(P)),'size':im.size,'bbox_by_alpha_threshold':b,'width_at_0p5':b['0.5'][2]-b['0.5'][0],'height_at_0p5':b['0.5'][3]-b['0.5'][1],'alpha_weighted_area_pixels':float(ar.sum()),'alpha_weighted_centroid_pixels':[float((X*ar).sum()/ar.sum()),float((Y*ar).sum()/ar.sum())]}
rows={}
for v in VERS:
 full=stats(P/f'images/{v}_FULL_CLOSE_F1.png');shot=stats(P/f'images/{v}_FULL_SHOT_F1.png');head=stats(P/f'images/{v}_HEAD_CLOSE_F1.png');parts=A[v]['frames']['1']['parts'];hands={};boots={}
 for n,r in parts.items():
  if 'hand_bone_aligned_bbox' in r:
   b=r['hand_bone_aligned_bbox'];hands[n]={'drawn_length_along_hand_bone_scene_units':b[1][1]-b[1][0],'drawn_width_along_hand_bone_scene_units':b[0][1]-b[0][0],'close_projected_geometry_bbox_pixels':r['close_projected_geometry_pixels']}
  if 'shoe_rest_bbox' in r:
   b=r['shoe_rest_bbox'];boots[n]={'rest_length_scene_units':b[0][1]-b[0][0],'rest_height_scene_units':b[2][1]-b[2][0],'close_projected_geometry_bbox_pixels':r['close_projected_geometry_pixels']}
 nearhand=next((r for n,r in hands.items() if n.endswith('near')),None);nearboot=next((r for n,r in boots.items() if 'near' in n),None);rows[v]={'actual_diagnostic_full_close':full,'actual_diagnostic_full_shot':shot,'actual_diagnostic_head_hair_neck_only':head,'head_hair_neck_height_over_full_height':head['height_at_0p5']/full['height_at_0p5'],'head_alpha_area_over_full_alpha_area':head['alpha_weighted_area_pixels']/full['alpha_weighted_area_pixels'],'full_character_fraction_of_native_close_height':full['height_at_0p5']/720,'full_character_fraction_of_native_shot_height':shot['height_at_0p5']/720,'saved_active_camera':A[v]['saved_camera'],'saved_render':A[v]['saved_render'],'hands':hands,'boots':boots,'near_boot_rest_length_over_near_hand_drawn_length':nearboot['rest_length_scene_units']/nearhand['drawn_length_along_hand_bone_scene_units'] if nearhand and nearboot else None}
build=json.loads((L/'character_design_finish_v040/evidence/NATIVE_PAINTED_BUILD.json').read_text());h=build['intentional_head_geometry_change'];b=h['rest_painted_occupancy_bounds'];g=h['atlas_head_pixel_bounds'];sx=(b[0][1]-b[0][0])/(g[2]-g[0]);sz=(b[1][1]-b[1][0])/(g[3]-g[1]);stretch={'source_head_paint_pixel_bbox':g,'mapped_rest_XZ_bbox':b,'scene_units_per_source_pixel_horizontal':sx,'scene_units_per_source_pixel_vertical':sz,'horizontal_over_vertical_scale_ratio':sx/sz,'horizontal_relative_stretch_percent':(sx/sz-1)*100,'meaning':'v040 maps the new independent head+neck painting to an old axis-aligned occupied box with unequal X/Z scale. This is relative to the generated source, not a10percent enlargement over the earlier rendered head.'}
camera={}
for cam in A['v028']['camera_data']:
 base=A['v028']['camera_data'][cam];camera[cam]={'baseline':base,'data_differences_from_v028':{v:{k:[base[k],r] for k,r in A[v]['camera_data'][cam].items() if r!=base[k]} for v in VERS},'matrix_max_difference_at_F1':{v:max(abs(A[v]['frames']['1']['camera_world'][cam][i][j]-A['v028']['frames']['1']['camera_world'][cam][i][j]) for i in range(4) for j in range(4)) for v in VERS}}
report={'scope':'Read-only proportion and framing audit. No assets rescaled or native files saved.','alpha_note':'Bounds use alpha>=0.5 with0.1/0.9 sensitivity available. Head mask includes hair and neck, so it is not an anatomical head count. Diagnostic cutouts remove stage only in RAM.','versions':rows,'camera_comparison':camera,'new_head_mapping':stretch,'v041_upper_coat_actual_change':{k:r for k,r in json.loads((L/'neck_collar_connection_v041/evidence/CONNECTION_BUILD.json').read_text()).items() if k in ['maximum_upper_coat_shift_m','new_collar_vertices','original_yoke_hidden_not_deleted','new_painting']},'scope_limit':'Review-camera comparisons do not establish the new design scale relative to the production environment. v040/v041 were not integrated into v046.'};(P/'evidence/RENDERED_SCALE_METRICS.json').write_text(json.dumps(report,indent=2))
ROOTS={'v028':L/'upper_body_pose_refinement_v028/previews','v036':L/'rigid_limb_continuity_v036/previews','v039':L/'full_color_coat_continuity_v039/previews','v040':L/'character_design_finish_v040/previews','v041':L/'neck_collar_connection_v041/previews'}
board=Image.new('RGB',(2400,1660),'#202725');d=ImageDraw.Draw(board);label(d,(24,12),'SCALE AUDIT ONLY | SAME CAMERA / SAME NATIVE PIXELS | no alignment or size normalization',27);label(d,(24,54),'Existing actual close renders, 480x720 each. Matching F1 and F20. Cosmetic development paused.',23)
for j,v in enumerate(VERS):
 x=j*480
 for i,f in enumerate([1,20]):
  y=124+i*786;folder='CANDIDATE_CLOSE' if v=='v041' else 'CLOSE';im=Image.open(ROOTS[v]/folder/f'{f:04d}.png').convert('RGB');assert im.size==(480,720);board.paste(im,(x,y));label(d,(x+16,y-34),v+f' | F{f:02d}',24)
board.save(P/'images/MATCHED_CLOSE_UNSCALED.png')
shotboard=Image.new('RGB',(2560,840),'#202725');ds=ImageDraw.Draw(shotboard);label(ds,(24,12),'NATIVE SHOT CAMERA | original1280x720 panels | no resizing',30)
for x,v in [(0,'v039'),(1280,'v041')]:
 label(ds,(x+24,60),v+' | F1',26);folder='CANDIDATE_SHOT' if v=='v041' else 'SHOT';im=Image.open(ROOTS[v]/folder/'0001.png').convert('RGB');assert im.size==(1280,720);shotboard.paste(im,(x,102))
shotboard.save(P/'images/MATCHED_SHOT_UNSCALED.png')
heads=Image.new('RGB',(1200,390),'#202725');dh=ImageDraw.Draw(heads);label(dh,(18,10),'HEAD + HAIR + NECK | native pixel crops; same camera, no scale normalization',24)
for i,v in enumerate(VERS):
 src=Image.open(P/f'images/{v}_HEAD_CLOSE_F1.png');tile=Image.new('RGBA',src.size,(213,213,204,255));tile.alpha_composite(src);crop=tile.convert('RGB').crop((150,30,390,270));heads.paste(crop,(i*240,98));label(dh,(i*240+12,60),v,23);label(dh,(i*240+10,344),f"H={rows[v]['actual_diagnostic_head_hair_neck_only']['height_at_0p5']} px",20)
heads.save(P/'images/HEAD_PAINT_MASS_UNSCALED.png')
summary={'head_mapping_stretch_percent':stretch['horizontal_relative_stretch_percent'],'camera_data_differences':{c:r['data_differences_from_v028'] for c,r in camera.items()},'rows':{v:{'full_close_h_px':r['actual_diagnostic_full_close']['height_at_0p5'],'full_shot_h_px':r['actual_diagnostic_full_shot']['height_at_0p5'],'head_hair_neck_h_px':r['actual_diagnostic_head_hair_neck_only']['height_at_0p5'],'head_alpha_area':r['actual_diagnostic_head_hair_neck_only']['alpha_weighted_area_pixels'],'head_centroid':r['actual_diagnostic_head_hair_neck_only']['alpha_weighted_centroid_pixels'],'boot_over_hand_length':r['near_boot_rest_length_over_near_hand_drawn_length'],'saved_camera':r['saved_active_camera'],'saved_render':r['saved_render']} for v,r in rows.items()}};(P/'evidence/COMPACT_SCALE_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
