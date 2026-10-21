"""Cold native preservation and exact route/clock checks, without source saves."""
import bpy,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
SOURCE=R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'
build=json.loads((O/'evidence/BUILD.json').read_text());NATIVE=Path(build['native']);H=hashlib.sha256(NATIVE.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def frame(s,g):s.frame_set(math.floor(g),subframe=g-math.floor(g));bpy.context.view_layer.update()
def is_contact(o):return any(c.name.startswith('V060 | evaluated boot contact paint') for c in o.users_collection)
def snapshot(path,name):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 s=bpy.data.scenes[name];bpy.context.window.scene=s;frame(s,981)
 root=bpy.data.objects['V047 | shared travel | steady .73125mps']
 geom=digest({o.name:{'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'uv':[[list(v.uv) for v in uv.data] for uv in o.data.uv_layers]} for o in s.objects if o.type=='MESH' and not is_contact(o)})
 images={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
 rest=digest({o.name:[{'name':b.name,'matrix':[list(v) for v in b.matrix_local],'length':b.length} for b in o.data.bones] for o in root.children_recursive if o.type=='ARMATURE'})
 boots=[o for o in root.children_recursive if o.type=='MESH' and o.get('proportion_role')=='boot' and not o.hide_render]
 boots_by_frame={};hands={}
 for g in sorted(set([913+i*3 for i in range(56)]+[936.75,937,937.25,957,981,1033,1055.75,1056,1056.25,1079.75,1080])):
  frame(s,g);dg=bpy.context.evaluated_depsgraph_get()
  boots_by_frame[g]={o.name:[list(o.evaluated_get(dg).matrix_world@v.co) for v in o.evaluated_get(dg).data.vertices] for o in boots}
 return {'geometry':geom,'images':images,'rest':rest,'boots':boots_by_frame}
before=snapshot(SOURCE,'WTSC_SHARED_COLOR_TO_CHARCOAL_v063');after=snapshot(NATIVE,'WTSC_FIRST_DANGER_WORLD_v065')
max_boot_error=0.
for g,objects in before['boots'].items():
 for name,verts in objects.items():
  other=after['boots'][g][name];assert len(verts)==len(other)
  max_boot_error=max(max_boot_error,max(math.sqrt(sum((x-y)**2 for x,y in zip(a,b))) for a,b in zip(verts,other)))
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];master=bpy.data.scenes['WTSC_FIRST_DANGER_REVIEW_MASTER_v065'];edit=bpy.data.scenes['WTSC_FIRST_DANGER_UNMASKED_EDIT_v065']
bpy.context.window.scene=w;ctrl=bpy.data.objects['V065 | both children | global full-cut color time']
samples=[]
for g in range(913,1081):
 frame(w,g);p=ctrl['charcoal_progress'];u=max(0.,min(1.,((g-1)/24)/96));expected=3*u*u-2*u*u*u
 samples.append({'frame':g,'camera_x':w.camera.matrix_world.translation.x,'color_progress':p,'expected_progress':expected,'color_error':abs(p-expected)})
camera_values={row['frame']:row['camera_x'] for row in samples}
core_step=.73125/24;core_error=max(abs((camera_values[g+1]-camera_values[g])-core_step) for g in range(937,1056))
boundary=[]
for g in [912.75,913,913.25,936.75,937,937.25,1055.75,1056,1056.25,1079.75,1080,1080.25]:
 frame(w,g);boundary.append({'frame':g,'x':w.camera.matrix_world.translation.x})
fonts={o.name:o.data.body for o in m.objects if o.type=='FONT'}
views={s.name:s.view_settings.view_transform for s in [w,m,master,edit]}
missing=[i.name for i in bpy.data.images if i.source=='FILE' and i.users and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()]
checks={'mesh_geometry_and_uvs_preserved_except_contact_quads':before['geometry']==after['geometry'],
 'original_packed_images_preserved':before['images']==after['images'],'rest_bones_preserved':before['rest']==after['rest'],
 'evaluated_boots_preserved':max_boot_error<.000001,'constant_core_tracking_matches_actual_travel':core_error<.00002,
 'global_palette_matches_full_cut_clock':max(x['color_error'] for x in samples)<.000001,
 'view_transform_standard_in_all_delivery_scenes':all(v=='Standard' for v in views.values()),
 'no_missing_used_unpacked_file_images':not missing,'native_source_unchanged_after_readback':hashlib.sha256(NATIVE.read_bytes()).hexdigest()==H,
 'v063_source_preserved':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==build['source_sha256'],
 'credits_and_title_bodies_preserved':sorted(fonts.values())==sorted(['WHEN THE SKY CLEARS','WHEN THE','SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'])}
report={'checks':checks,'all_checks_pass':all(checks.values()),'native_sha256':H,'maximum_evaluated_boot_deviation_m':max_boot_error,'boot_frame_samples':len(before['boots']),'core_camera_step_max_error_m':core_error,'boundary_quarter_frame_samples':boundary,'view_transforms':views,'missing_images':missing,'global_clock_samples':samples,'full_route_downstream_offset_m':build['camera_route']['downstream_offset_m'],'limits':'This validates a conformed route and bounded first-danger passage. Old downstream movie frames still require rerender from that route. No full-film acting or artistic acceptance inferred.'}
(O/'evidence/COLD_NATIVE_VALIDATION.json').write_text(json.dumps(report,indent=2));assert all(checks.values()),checks
print('V065_COLD_NATIVE_VALIDATION_PASSED',flush=True)
