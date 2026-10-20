import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]; R=P.parents[1]
for d in ['evidence','native','previews','scripts']: (P/d).mkdir(exist_ok=True)
files=['shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','renders/world_v016/integration_v046/WTSC_Supported_Recovery_v046_1080p_75_80.mp4','locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend','locomotion/head_turn_patch_v008/evidence/STATUS_REFERENCE_REQUIRED.json']
hashes={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in files}
(P/'evidence/protected_inputs.json').write_text(json.dumps(hashes,indent=2))
out={'version':bpy.app.version_string,'binary':bpy.app.binary_path,'files':hashes}
for mode,path in [('v046',files[0]),('v007',files[2])]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path),load_ui=False)
 s=next(s for s in bpy.data.scenes if any(o.get('motion_revision')=='v007_drawn_pose_corrections' for o in s.objects));bpy.context.window.scene=s
 root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
 info={'scenes':[(sc.name,sc.frame_start,sc.frame_end,len(sc.objects)) for sc in bpy.data.scenes],'scene':s.name,'objects':[],'frames':[]}
 for o in [root,*root.children_recursive]:
  item={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'props':{k:str(o[k]) for k in o.keys()},'hidden':o.hide_render,'location':list(o.location)}
  if o.type=='MESH': item.update(vertices=len(o.data.vertices),keys=[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [],groups=[g.name for g in o.vertex_groups],mods=[(m.type,m.object.name if hasattr(m,'object') and m.object else None) for m in o.modifiers])
  if o.type=='ARMATURE':item['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones]
  if o.animation_data:item['drivers']=[{'path':f.data_path,'expr':f.driver.expression} for f in o.animation_data.drivers]
  info['objects'].append(item)
 for f in [1,37,43,44,45,46,61,72,81,89,101,110,120]:
  s.frame_set(f if mode=='v007' else 1800+f);bpy.context.view_layer.update()
  row={'local':f,'camera':[list(v) for v in s.camera.matrix_world] if s.camera else None,'rigs':{},'travel':[(o.name,list(o.location),list(o.matrix_world.translation)) for o in root.children if o.type=='EMPTY']}
  for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
   row['rigs'][rig.get('character',rig.name)]={'world':list(rig.matrix_world.translation),'bones':{b.name:{'head':list(b.head),'tail':list(b.tail)} for b in rig.pose.bones}}
  info['frames'].append(row)
 out[mode]=info
(P/'evidence/source_inspection.json').write_text(json.dumps(out,indent=2))
print('SOURCE_INSPECTED',bpy.app.version_string,[(k,out[k]['scene']) for k in ['v046','v007']],flush=True)
