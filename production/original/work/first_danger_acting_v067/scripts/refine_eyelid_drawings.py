"""Replace weak blink compression with native 2D lids using the original paint."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());P=Path(B.get('pilot_native',B['native']));oldhash=hashlib.sha256(P.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def interp(t,ks):
 if t<=ks[0][0]:return ks[0][1]
 if t>=ks[-1][0]:return ks[-1][1]
 for (a,x),(b,y) in zip(ks,ks[1:]):
  if a<=t<=b:return x+(y-x)*ease((t-a)/(b-a))
new=[]
for rec in B['head_changes']:
 w=rec['who'];r=bpy.data.objects['V044 '+w+' | estimated joint centres'];head=next(o for o in S.objects if o.parent==r and o.get('proportion_role')=='head' and not o.hide_render)
 eye=Vector(rec['eye_rest_coordinate'])+Vector((-.004,0,0) if w=='BOY' else (.0015,0,.008))
 # Preserve the original open painting; the separate skin/ink drawings close it.
 blink=next(k for k in head.data.shape_keys.key_blocks if 'eyelid close' in k.name)
 blink.value=0
 ad=head.data.shape_keys.animation_data
 for l in ad.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in list(bag.fcurves):
     if 'local eyelid close' in fc.data_path:bag.fcurves.remove(fc)
 skinpx=(330,285) if w=='BOY' else (1058,242);size=(1254,1254) if w=='BOY' else (1672,941)
 for kind in ['skin lid','closed lid line']:
  material=head.data.materials[0].copy();material.name='V067 '+w+' | '+kind+' | original face pigment'
  if kind=='closed lid line':
   em=next(n for n in material.node_tree.nodes if n.type=='EMISSION');src=em.inputs[0].links[0].from_socket
   mul=material.node_tree.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.22,.18,.16,1);material.node_tree.links.new(src,mul.inputs[1]);material.node_tree.links.new(mul.outputs[0],em.inputs[0])
  V=[];F=[];UV=[];width=.012 if w=='BOY' else .0115;height=.0085 if w=='BOY' else .008
  for row in range(3):
   t=row/2
   for col in range(17):
    x=-width+2*width*col/16;curve=max(0,1-(x/width)**2)**.5
    if kind=='skin lid':z=eye.z+(2*t-1)*height*curve
    else:z=eye.z-.0007+.0014*(x/width)**2+(t-.5)*.0020*curve
    V.append((eye.x+x,0,z));UV.append((skinpx[0]/size[0],1-skinpx[1]/size[1]))
  for row in range(2):
   for col in range(16):i=row*17+col;F.append((i,i+1,i+18,i+17))
  me=bpy.data.meshes.new('V067 '+w+' | '+kind);me.from_pydata(V,[],F);me.update();uv=me.uv_layers.new(name=head.data.uv_layers.active.name)
  for lp in me.loops:uv.data[lp.index].uv=UV[lp.vertex_index]
  me.materials.append(material);ob=bpy.data.objects.new(me.name,me);S.collection.objects.link(ob);ob.parent=r;ob.matrix_local=head.matrix_local.copy();ob.location.y-=.003 if kind=='skin lid' else .004
  gr=ob.vertex_groups.new(name='head');gr.add(list(range(len(V))),1,'REPLACE');mod=ob.modifiers.new('Existing native head bone','ARMATURE');mod.object=r
  basis=ob.shape_key_add(name='Basis | open eye | invisible lid')
  for p in basis.data:p.co.z=eye.z+height
  key=ob.shape_key_add(name='V067 | closed native '+kind)
  for i,p in enumerate(V):key.data[i].co=p
  for i in range(335):
   g=913+i*.5;key.value=interp(g,rec['blink_schedule']);key.keyframe_insert('value',frame=g)
  for l in ob.data.shape_keys.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
  ob['V067_lid']='Native flat lid drawing, original face material/pigment sampling and global color clock; no new raster painting.'
  new.append(ob.name)
crypto=S.compositing_node_group.nodes['V065 | existing children | visible drawing matte']
crypto.matte_id+=','+','.join(new)
S.frame_set(957);bpy.context.view_layer.update();newpath=O/'native/WTSC_First_Danger_Acting_v067c.blend';bpy.ops.wm.save_as_mainfile(filepath=str(newpath),compress=True)
if not (O/'evidence/BUILD_PILOT_v067.json').exists():(O/'evidence/BUILD_PILOT_v067.json').write_text(json.dumps(B,indent=2))
B['pilot_native']=str(P);B['pilot_native_sha256']=oldhash;B['native']=str(newpath);B['native_sha256']=hashlib.sha256(newpath.read_bytes()).hexdigest();B['new_lid_objects']=new;B['blink_refinement']='The first compression-only blink read as a squint. Separate native skin/ink lid drawings now close the eye using the original face pigment and corrected registration; the weak compression keys were disabled.'
(O/'evidence/BUILD.json').write_text(json.dumps(B,indent=2));print('V067B_LIDS_SAVED',new,flush=True)
