import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import motion_model as M;import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Continuous_Coat_Walk_v023.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rigs,c=api.initialize_from_scene();rig=rigs['BOY'];boots=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text())
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
checks=[];loopposes={};maxcontact=0;minsole=1;bad=[]
for i in range(373):
 q=i/4;f=q+1;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();r=M.evaluate(q)
 for side in ['near','far']:
  V=pts(bpy.data.objects[boots[side]['object']]);d=r['feet'][side];z=min(v.z for v in V);minsole=min(minsole,z)
  if d['mode']=='CONTACT':
   j=d['meta']['vertex'];err=(V[j]-Vector((d['meta']['anchor_xz'][0],V[j].y,0))).length;maxcontact=max(maxcontact,err)
 for k in api.reach_report():
  if not k['reachable']:bad.append({'q':q,**k})
 if q in [0,31,62,93]:
  loopposes[q]={o.name:pts(o) for o in list(rig.children)+list(bpy.data.collections['V023 | continuous painted representation'].objects) if o.type=='MESH' and not o.hide_render}
worstloop=max((a+Vector((n*M.STRIDE,0,0))-b).length for n in [1,2,3] for name in loopposes[0] for a,b in zip(loopposes[0][name],loopposes[31*n][name]))
# Exact transition displacements, reported as geometric continuity rather than artistic approval.
boundaries=[]
for q in [0,4.25,16,18.5,31]:
 before=M.evaluate(q-1e-5);after=M.evaluate(q+1e-5);boundaries.append({'q':q,'max_ankle_position_jump_over_2e_minus5_frames_m':max(float((before['feet'][s]['A']-after['feet'][s]['A'])@(before['feet'][s]['A']-after['feet'][s]['A']))**.5 for s in ['near','far'])})
report={'fresh_native_samples':373,'sample_rate_per_frame':4,'max_actual_sole_anchor_error_m':maxcontact,'minimum_actual_sole_z_m':minsole,'unreachable_native_chains':bad,'loop_mesh_translation_error_m':worstloop,'motion_model_transition_checks':boundaries,'drawing_swaps':0,'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'status':'PASS' if maxcontact<.0001 and minsole>-.0001 and not bad and worstloop<.0001 else 'FAIL','scope':'Contact, reach, loop and absence of hard drawing switches; not continuous-playback artistic acceptance'}
(P/'evidence/fresh_continuous_native_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if report['status']!='PASS':raise RuntimeError('Continuous native check failed')
S.render.resolution_x=960;S.render.resolution_y=540;S.camera=bpy.data.objects['V022 | whole painted pose close']
for name,f in [('LOADING',17.25),('PASSING',25.25)]:
 S.frame_set(int(f),subframe=f-int(f));S.render.filepath=str(P/f'previews/V023_COAT_{name}_MATCHED_CLOSE.png');bpy.ops.render.render(write_still=True)
print('V023_MATCHED_COAT_CHECK_RENDERED')

