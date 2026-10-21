import bpy,json,time,shutil,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];gate=json.loads((P/'evidence/PREFERRED_WHOLE_CYCLE_PRESERVATION.json').read_text());assert not gate['unexpected_channel_changes'];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Limb_Volume_and_Hand_Readability_v036.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;start=time.time();records=[];newrenders=0
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;p=P/'previews'/view;p.mkdir(exist_ok=True)
 for f in range(1,94):
  old=P/'previews'/('PROOF_'+view)/f'{f:04d}.png';dest=p/f'{f:04d}.png'
  if old.exists():shutil.copyfile(old,dest)
  else:S.frame_set(f);S.render.filepath=str(dest);bpy.ops.render.render(write_still=True);newrenders+=1
  if f%31==0:print('V036_MOTION_PROGRESS',view,f,round(time.time()-start,1),flush=True)
 records.append({'view':view,'frames':[1,93],'native_size':size})
# One bounded opaque mask pair to verify the intended far-side F20 overlap.
S.frame_set(20);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;o=bpy.data.objects['V007_BOY | articulated drawn hand far'];m=bpy.data.materials.new('V036 diagnostic far hand ID');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.01,1,.01,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);o.material_slots[0].link='OBJECT';o.material_slots[0].material=m;p=P/'previews/F20_OVERLAP';p.mkdir(exist_ok=True)
for name,hide in [('FULL',False),('NO_NEAR_TROUSER',True)]:
 bpy.data.objects['V024 continuous near trouser drawing'].hide_render=hide;S.render.filepath=str(p/(name+'.png'));bpy.ops.render.render(write_still=True)
old=json.loads((P/'evidence/HAND_AND_SHOE_GEOMETRY.json').read_text())['shoe']['coords'];new=[list(v.co) for v in bpy.data.objects['V033 | near | canonical painted shoe'].data.vertices];mx=0
for i in range(3401):
 a=math.radians(-85+i*.05);mn=lambda V:min(-math.sin(a)*v[0]+math.cos(a)*v[2] for v in V);mx=max(mx,abs(mn(old)-mn(new)))
assert mx<1e-9
report={'actual_clean_candidate_frames':186,'additional_new_motion_renders':newrenders,'same_frame_proof_stills_reused':186-newrenders,'far_hand_diagnostic_renders':2,'fps':30,'cycle_frames':31,'cycles_per_view':3,'seconds_per_view':3.1,'records':records,'threads':2,'elapsed_seconds':time.time()-start,'matching':'Source v033 actual saved renders1-93; same native frame/time/camera; no retiming, interpolation or phase alignment','upper_shoe_edits_max_sole_envelope_change_m_over_minus85_to85_degrees':mx,'observation_limit':'Actual frames and encoded preview can be inspected; export success is not visual or animation acceptance.'};(P/'evidence/MOTION_RENDER_RECORD.json').write_text(json.dumps(report,indent=2));print('V036_MOTION_RENDER_COMPLETE',json.dumps(report),flush=True)
