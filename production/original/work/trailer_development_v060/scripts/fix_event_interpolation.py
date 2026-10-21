import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060');P=O/'native/WTSC_First_Danger_Trailer_Development_v060.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060'];bpy.context.window.scene=s
e=s.objects['V060 | one offscreen distant flash | painted response']
for prop in ['pulse','settle']:
 value=float(e[prop]);del e[prop];e[prop]=value;e.id_properties_ui(prop).update(default=0.,min=0.,max=1.)
for l in e.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:fc.update_autoflags(e);fc.update()
rows=[]
for f,pulse in [(955,0),(956,.15),(956.5,.575),(957,1),(958,.8),(960,.23),(965,0)]:
 n=int(f);s.frame_set(n,subframe=f-n);bpy.context.view_layer.update()
 assert abs(e['pulse']-pulse)<1e-6,(f,e['pulse'],pulse)
 rows.append({'frame':f,'pulse':e['pulse']})
s.frame_set(984);bpy.context.view_layer.update();assert abs(e['settle']-.5)<1e-6,e['settle']
s.frame_set(981);m.frame_set(981)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
r=json.loads((O/'evidence/WORLD_BUILD.json').read_text());r['event_float_curve_fix']={'pulse_and_settle_properties':'FLOAT; integer FCurve flags cleared','intermediate_settle_at984':.5,'pulse_samples':rows}
(O/'evidence/WORLD_BUILD.json').write_text(json.dumps(r,indent=2))
print('V060_FLOAT_EVENT_INTERPOLATION_VERIFIED',json.dumps(rows),flush=True)
