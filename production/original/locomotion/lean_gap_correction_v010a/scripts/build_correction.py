import bpy,runpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];V10=P.parent/'stumble_polish_continuation_v010'
for folder in ['native','evidence','previews']:(P/folder).mkdir(exist_ok=True)
inputs=[V10/'native/WTSC_Stumble_Polish_Continuation_v010.blend',V10/'native/WTSC_v010_Matched_Review_Copy.blend',V10/'WTSC_v010_Matched_5s_Polish_PLUS_Separate_2s_Continuation.mp4',V10/'evidence/travel_original_5s_v010.csv',V10/'evidence/travel_extension_80_82s_v010.csv']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};(P/'evidence/protected_inputs.json').write_text(json.dumps(hashes,indent=2))
apply=runpy.run_path(str(P/'scripts/apply_correction.py'))['apply_correction'];reports={}
for mode,source in [('native',inputs[0]),('matched',inputs[1])]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('motion_revision')=='v010_polish_continuation');start=1 if mode=='native' else 1801
 reports[mode]=apply(s,root,start);root.users_collection[0].name='WTSC_STUMBLE_POLISH_CONTINUATION_v010a';s.name='V010a | narrow boy lean correction | '+mode
 # Same clocks and helper interface; only the revision lookup/name changes.
 cfg=(V10/'scripts/configure_v010.py').read_text().replace('configure_v010','configure_v010a').replace('v010_polish_continuation','v010a_lean_gap_correction')
 for text in list(bpy.data.texts):
  if text.name=='configure_v010.py':bpy.data.texts.remove(text)
 text=bpy.data.texts.new('configure_v010a.py');text.write(cfg)
 if mode=='native':(P/'scripts/configure_v010a.py').write_text(cfg)
 name='WTSC_Stumble_Polish_Continuation_v010a.blend' if mode=='native' else 'WTSC_v010a_Matched_Review_Copy.blend';s.frame_set(start);s.render.filepath=str(P/'previews/OWNED_REVIEW_ONLY');bpy.ops.wm.save_as_mainfile(filepath=str(P/'native'/name),compress=True);reports[mode]['saved']=str(P/'native'/name)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
(P/'evidence/correction_recipe.json').write_text(json.dumps(reports,indent=2));print('V010a_CORRECTION_SAVED',json.dumps(reports),flush=True)
