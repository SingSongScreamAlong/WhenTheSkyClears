import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];BASE=ROOT/'locomotion/painted_outfit_restoration_v046';old=BASE/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';new=P/'native/WTSC_Steady_Ordinary_Walk_v047.blend'
def painting():
 out={}
 for c in ['V044 | age10 editable profile anatomy','V046 | restored original painted wardrobe']:
  for o in bpy.data.collections[c].objects:
   if o.type!='MESH':continue
   value={'materials':[m.name for m in o.data.materials],'uv':{u.name:[tuple(p.uv) for p in u.data] for u in o.data.uv_layers}}
   out[o.name]=hashlib.sha256(repr(value).encode()).hexdigest()
 images={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file and i.source=='FILE' and i.users};return out,images
bpy.ops.wm.open_mainfile(filepath=str(old),load_ui=False,use_scripts=False);source=painting();bpy.ops.wm.open_mainfile(filepath=str(new),load_ui=False,use_scripts=False);current=painting();assert source==current,'Painting/material slot/UV changed';S=bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline'];bpy.context.window.scene=S;C=bpy.data.collections['V046 | restored original painted wardrobe'];cloth=[o for o in C.objects if o.get('wardrobe_role') in ['sleeve','leg']]
tree=ast.parse((BASE/'scripts/build_outfits.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rounded','smooth']];exec(compile(tree,'original_clothing_geometry','exec'),globals());errors={o.name:0. for o in cloth}
for i in range(257):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for o in cloth:
  r=o.parent;ev=r.evaluated_get(dg);side=o.name.split()[-1];kind=o['wardrobe_role'];n1=('upper_arm_' if kind=='sleeve' else 'thigh_')+side;n2=('forearm_' if kind=='sleeve' else 'shin_')+side;b1=ev.pose.bones[n1];b2=ev.pose.bones[n2];l1=r.data.bones[n1].length;total=l1+r.data.bones[n2].length;start=-.008 if kind=='sleeve' else -.025;end=l1+.027 if kind=='sleeve' else total-.030;rows=49 if kind=='sleeve' else 65;oe=o.evaluated_get(dg);to_r=ev.matrix_world.inverted()@oe.matrix_world
  for k in range(rows):
   d=start+(end-start)*k/(rows-1);expect,_=rounded(b1.head,b1.tail,b2.tail,l1,d,.018 if kind=='sleeve' else .022)
   if kind=='leg':w=smooth((d-(total-.095))/.065);rest=Vector((0,0,r.data.bones[n1].head_local.z-d));bound=ev.pose.bones['foot_'+side].matrix@r.data.bones['foot_'+side].matrix_local.inverted()@rest;expect=expect.lerp(bound,w)
   actual=to_r@oe.data.vertices[k*9+4].co;errors[o.name]=max(errors[o.name],math.hypot(actual.x-expect.x,actual.z-expect.z))
assert max(errors.values())<.0005,errors
report={'native_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'source_v046_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'all_original_uv_registrations_and_material_slots_identical':True,'all_used_packed_image_payload_hashes_identical':True,'image_hashes':current[1],'mesh_uv_and_material_slot_hashes':current[0],'garment_registration_samples':257,'garment_registration_max_errors_m':errors,'limit_m':.0005,'scope':'No new artwork, palette, cloth or braid follow-through. Cached sleeves/legs regenerated to the changed gait.'};(P/'evidence/PAINT_AND_CLOTHING_VALIDATION.json').write_text(json.dumps(report,indent=2));print('V047_ORIGINAL_PAINT_AND_NEW_CLOTHING_CACHE_PASS',max(errors.values()),flush=True)
