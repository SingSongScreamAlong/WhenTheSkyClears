import bpy,json,sys,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import color_materials as CM
SRC=P/'reference/PRESERVED_GARMENT_v037.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;report={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'root_repairs':{},'materials':{},'palette':CM.PALETTES,'scope':'Isolated full-color character art study with five retained static coat poses. Original dark sources and production preserved.'}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
# Round/tuck only the original upper trouser root, ending the correction before
# 30percent down the leg drawing. Joint axes, pose curves and lower leg stay fixed.
for side in ['near','far']:
 o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];a=o.data.attributes['V036_width_scale'];old=[v.value for v in a.data];factors=[smooth((i//7)/96/.15)*(.75+.25*smooth((i//7)/96/.30)) for i in range(len(old))];a.data.foreach_set('value',[v*w for v,w in zip(old,factors)]);o['V038_root_repair']='Rounded hidden root cap and tucked upper-hip width; multiplicative contour field ends at30percent. No bone, pelvis, leg-center, foot path or garment-length change.';report['root_repairs'][side]={'field':'V036_width_scale','root_factors_by_row':factors[::7],'rows_from_30percent_down_unchanged':all(abs(w-1)<1e-9 for i,w in enumerate(factors) if (i//7)/96>=.30)}
S['V038_scope']='Full-color readability study; five static coat poses1,4,11,20,27. Preferred v028/v036 movement and original head/profile geometry retained. No permanent replacement of the dark treatment.';S.frame_set(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Trouser_Root_Repair_Dark_v038.blend'),compress=True)
shared={}
for o in list(S.objects):
 if o.type!='MESH' or o.hide_render:continue
 role=None;head=False;garment=False
 if o.name=='PERF_BOY | original head':role='hair';head=True
 elif o.name=='LOCO_BOY | PAINT body' or 'drawn source gray cuff' in o.name:role='linen'
 elif 'articulated drawn hand' in o.name or 'drawn skin' in o.name:role='skin'
 elif 'drawn sleeve' in o.name:role='coat'
 elif 'V024 continuous' in o.name:role='trousers'
 elif 'V033 |' in o.name and 'canonical painted shoe' in o.name:role='shoes'
 elif o.name.startswith('V037 | coherent charcoal coat'):role='coat';garment=True
 if role is None:continue
 for i,slot in enumerate(o.material_slots):
  orig=slot.material
  if not orig:continue
  key=(orig.name,role,head,garment)
  if key not in shared:shared[key]=CM.recolor(orig,role,role+' | '+orig.name,head=head,garment=garment)
  slot.link='OBJECT';slot.material=shared[key];report['materials'][o.name]={'role':role,'original_material':orig.name,'color_material':slot.material.name,'shared_palette':role}
S['V038_status']='FULL COLOR CHARACTER CANDIDATE. Natural skin/hands, dark brown hair, restrained slate coat, linen collar/cuffs, olive trousers and matching brown shoes. Original identity/profile and preferred motion retained; static coat study only. No silhouette treatment replacement or production integration.'
t=bpy.data.texts.new('READ_FIRST_v038');t.write('Full-color material/shape-readability study only. Native material copies retain original image bytes and alpha. F1hero +F4/F11/F20/F27 static coat samples. Original body actions unchanged; missing coat inbetweens are not authored. The dark study and all production files remain separate. Upper trouser root contour is rounded/tucked; no joint or foot path changes.');bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Boy_Full_Color_Readability_v038.blend'),compress=True);(P/'evidence/FULL_COLOR_BUILD.json').write_text(json.dumps(report,indent=2));print('V038_FULL_COLOR_BUILT',json.dumps({'roles':len(report['materials']),'native_material_copies':len(shared),'blender':bpy.app.version_string}),flush=True)
