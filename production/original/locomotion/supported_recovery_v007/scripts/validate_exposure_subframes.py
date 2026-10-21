import bpy,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Supported_Recovery_v007.blend'),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');cfg=runpy.run_path(str(P/'scripts/configure_v007.py'))['configure_v007'];cfg(start=201,duration_scale=2,root_motion=False,root=root);girl=next(o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')=='GIRL');heads=[o for o in girl.children if 'original head and attached braid' in o.name or o.get('v007_role')=='look_back_original_paint' or 'passing back-view drawing' in o.name];assert len(heads)==3;counts={o.name:0 for o in heads};bad=[]
for f in range(201,441):
 s.frame_set(f);bpy.context.view_layer.update();active=[o.name for o in heads if not o.hide_render]
 if len(active)!=1:bad.append({'frame':f,'visible':active})
 else:counts[active[0]]+=1
report={'duration_scale':2,'evaluated_output_frames':240,'head_counts':counts,'bad_frames':bad,'pass':not bad};(P/'evidence/retimed_exposure_every_frame.json').write_text(json.dumps(report,indent=2));assert not bad,bad;print('V007_240F_RETIMED_EXPOSURE_PASS',json.dumps(report),flush=True)
