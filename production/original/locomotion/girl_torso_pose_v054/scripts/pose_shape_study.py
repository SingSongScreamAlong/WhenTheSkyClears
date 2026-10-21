"""Key-pose visual proof only: RAM edits, no new native or inbetweens."""
import bpy,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews';src=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend'
digest='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b';assert hashlib.sha256(src.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);S=bpy.data.scenes['V053 | AUTHORED WALK BEATS | v051 grounded feet'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
r=bpy.data.objects['V044 GIRL | estimated joint centres'];C=bpy.data.collections['V046 | restored original painted wardrobe'];body=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='body');assert len(body.data.vertices)==1105 and not body.data.shape_keys
sleeves={side:next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='sleeve' and o.name.endswith(side)) for side in ('near','far')}
original=[v.co.copy() for v in body.data.vertices];frames={4:'loading_near',9:'passing_near',13:'push_near',20:'loading_far',25:'passing_far',29:'push_far'}
params={
 'loading_near':{'shoulder_rear':.014,'shoulder_front':-.008,'shoulder_z':-.005,'waist_rear':.010,'waist_front':-.015,'waist_z':.006,'cap_x':.003,'cap_z':-.004},
 'loading_far':{'shoulder_rear':.013,'shoulder_front':-.009,'shoulder_z':-.006,'waist_rear':.009,'waist_front':-.014,'waist_z':.006,'cap_x':.003,'cap_z':-.004},
 'passing_near':{'shoulder_rear':-.004,'shoulder_front':.004,'shoulder_z':.002,'waist_rear':-.004,'waist_front':.005,'waist_z':-.002,'cap_x':-.002,'cap_z':.001},
 'passing_far':{'shoulder_rear':-.003,'shoulder_front':.004,'shoulder_z':.002,'waist_rear':-.004,'waist_front':.004,'waist_z':-.002,'cap_x':-.002,'cap_z':.001},
 'push_near':{'shoulder_rear':-.007,'shoulder_front':.006,'shoulder_z':.003,'waist_rear':-.005,'waist_front':.005,'waist_z':-.002,'cap_x':-.003,'cap_z':.001},
 'push_far':{'shoulder_rear':-.006,'shoulder_front':.005,'shoulder_z':.002,'waist_rear':-.004,'waist_front':.005,'waist_z':-.002,'cap_x':-.003,'cap_z':.001},
}
def bump(t,a,b):return math.sin(math.pi*(t-a)/(b-a))**2 if a<t<b else 0.
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def deform_body(p):
 out=[]
 for i,v in enumerate(original):
  row,col=divmod(i,17);t=row/64;s=col/16;sh=bump(t,.02,.37) if row>2 else 0;wa=bump(t,.25,.66) if row<43 else 0
  q=v.copy();q.x+=sh*(p['shoulder_rear']*(1-s)+p['shoulder_front']*s)+wa*(p['waist_rear']*(1-s)+p['waist_front']*s);q.z+=sh*p['shoulder_z']+wa*p['waist_z'];out.append(q)
 return out
def cell_signs(verts):
 signs=[]
 for row in range(64):
  for col in range(16):
   a=verts[row*17+col];b=verts[row*17+col+1];c=verts[(row+1)*17+col]
   signs.append((b.x-a.x)*(c.z-a.z)-(b.z-a.z)*(c.x-a.x))
 return signs
before=cell_signs(original);assert min(abs(x) for x in before)>1e-9
folder=V/'key_shape_study';folder.mkdir(exist_ok=True);records=[];max_delta=0.;min_area=1e9
for f,kind in frames.items():
 p=params[kind];S.frame_set(f);bpy.context.view_layer.update();base=folder/('V053_BASE_F%03d.png'%f);S.render.filepath=str(base);bpy.ops.render.render(write_still=True,scene=S.name)
 changed=deform_body(p);areas=cell_signs(changed);assert all(a*b>0 for a,b in zip(before,areas));min_area=min(min_area,min(abs(x) for x in areas));max_delta=max(max_delta,max((x-y).length for x,y in zip(changed,original)))
 body.data.vertices.foreach_set('co',[c for q in changed for c in q]);body.data.update();cached=[]
 for side,o in sleeves.items():
  idx=4*(f-1);key=o.data.shape_keys.key_blocks[idx];points=[q.co.copy() for q in key.data];cached.append((key,points))
  altered=[]
  for j,q in enumerate(points):
   row,col=divmod(j,9);w=(1-smooth(row/17))**2 if row<17 else 0.;v=q.copy();v.x+=p['cap_x']*w;v.z+=p['cap_z']*w;altered.append(v)
  key.data.foreach_set('co',[c for q in altered for c in q]);o.data.update()
 bpy.context.view_layer.update();cand=folder/('V054_KEY_%s_F%03d.png'%(kind.upper(),f));S.render.filepath=str(cand);bpy.ops.render.render(write_still=True,scene=S.name)
 records.append({'frame':f,'phase':kind,'source':str(base),'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'key_study':str(cand),'key_study_sha256':hashlib.sha256(cand.read_bytes()).hexdigest(),'params_m':p})
 body.data.vertices.foreach_set('co',[c for q in original for c in q]);body.data.update()
 for key,points in cached:key.data.foreach_set('co',[c for q in points for c in q])
 for o in sleeves.values():o.data.update()
assert hashlib.sha256(src.read_bytes()).hexdigest()==digest
(E/'KEY_SHAPE_STUDY.json').write_text(json.dumps({'source':str(src),'source_sha256':digest,'saved_new_native':False,'source_unchanged':True,'frames':list(frames),'body_collar_rows_0_to_2_unchanged':True,'dress_skirt_rows_43_to_64_unchanged':True,'body_max_vertex_delta_m':max_delta,'minimum_cell_area_m2':min_area,'cell_inversions':0,'records':records},indent=2))
print('V054_GIRL_KEY_SHAPES_RENDERED_RAM_ONLY',max_delta,min_area)
