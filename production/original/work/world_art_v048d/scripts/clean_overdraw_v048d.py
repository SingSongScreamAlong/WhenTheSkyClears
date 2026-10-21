import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048');p=O/'WTSC_World_Art_Checkpoint_v048d.blend';assert not p.exists()
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_World_Art_Checkpoint_v048c.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_ART_v048c_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('v048 |') and o.type=='CURVE':removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
m=bpy.data.materials['v048b | peaceful original painted earth'];n=next(n for n in m.node_tree.nodes if n.type=='MIX_RGB');n.inputs[0].default_value=.55;n.inputs[2].default_value=(1.65,1.13,.55,1)
s.name='WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC';s['v048d_final']='Three-region painted earth and material hierarchy checkpoint. All diagrammatic native line overdraw rejected. Architecture improvement remains a separate unmet art gate. Title/edit/character/FX retained.'
s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.frame_set(1849)
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);(O/'native_4k_after_d').mkdir(exist_ok=True)
for label,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_after_d'/f'WTSC_v048d_{label}_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('CLEAN_4K_AFTER',label,flush=True)
q=json.loads((O/'FINAL_VERIFICATION_v048c.json').read_text());q['native']=str(p);q['native_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();q['world_scene']=s.name;q['retained_new_objects']=sum(o.name.startswith('v048') for o in s.objects);q['removed_diagrammatic_line_objects']=len(removed);q['final_art_change']='Painted earth propagation, quieter repeated path foliage, region-aware warm/cool material/light fields. Architectural native overdraw rejected after actual4K crop review.';q['limits'].append('All added native architecture curves removed after1:1 review; higher-detail architectural painting remains unfulfilled.');(O/'FINAL_VERIFICATION_v048d.json').write_text(json.dumps(q,indent=2));print('V048D_READY',q['native_sha256'],q['retained_new_objects'],flush=True)
