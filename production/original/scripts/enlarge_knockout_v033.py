import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
out=R/'shots/world/WTSC_Knockout_Ending_Editable_v033.blend';assert not out.exists()
prior=Path(bpy.data.filepath);prior_sha=hashlib.sha256(prior.read_bytes()).hexdigest()
e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v032'];bpy.context.window.scene=e;e.frame_set(2137)
line=next(o for o in e.objects if 'Moving knockout' in o.name)
def geometry_bounds(ob):
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
 xyz=[v.co.copy() for v in mesh.vertices];ev.to_mesh_clear()
 return [min(v.x for v in xyz),max(v.x for v in xyz),min(v.y for v in xyz),max(v.y for v in xyz)]
view=e.camera.data.view_frame(scene=e);W=max(v.x for v in view)-min(v.x for v in view);H=max(v.y for v in view)-min(v.y for v in view)
# Measure straight cap ink, not the whole string's curved-letter overshoot.
probe_data=line.data.copy();probe_data.body='H';probe=bpy.data.objects.new('TEMP_CAP_MEASURE',probe_data);e.collection.objects.link(probe)
hb=geometry_bounds(probe);bpy.data.objects.remove(probe,do_unlink=True);bpy.data.curves.remove(probe_data)
b=geometry_bounds(line);sc=.995*H/(hb[3]-hb[2]);line.scale=(sc,sc,sc);line.location.y=-(hb[2]+hb[3])*sc/2
line.animation_data_clear()
for f,x in [(1969,W/2-b[0]*sc),(2401,-W/2-b[1]*sc)]:line.location.x=x;line.keyframe_insert('location',index=0,frame=f)
for f,h in [(1,False),(2400,False),(2401,True)]:line.hide_render=h;line.keyframe_insert('hide_render',frame=f)
for layer in line.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR' if fc.data_path=='location' else 'CONSTANT'
# A real heavy condensed face fills three rows without stretching any glyph.
impact=bpy.data.fonts.load(r'C:\Windows\Fonts\impact.ttf');impact.pack()
card={suffix:next(o for o in e.objects if o.name.endswith('Final card | '+suffix)) for suffix in ['top','main','year']}
metrics={}
for key,ob in card.items():
 ob.data.font=impact;ob.scale=(1,1,1);b=geometry_bounds(ob);metrics[key]={'bounds':b}
for key in ['top','main']:
 b=metrics[key]['bounds'];metrics[key]['scale']=.98*W/(b[1]-b[0]);metrics[key]['height']=(b[3]-b[2])*metrics[key]['scale']
gap=.015*H
year_height=.99*H-metrics['top']['height']-metrics['main']['height']-2*gap
assert year_height>0
b=metrics['year']['bounds'];metrics['year']['scale']=year_height/(b[3]-b[2]);metrics['year']['height']=year_height
assert (b[1]-b[0])*metrics['year']['scale']<=.98*W
cursor=.495*H
for key in ['top','main','year']:
 ob=card[key];b=metrics[key]['bounds'];s=metrics[key]['scale'];h=metrics[key]['height'];ob.scale=(s,s,s);ob.location.x=-(b[0]+b[1])*s/2;ob.location.y=cursor-b[3]*s
 metrics[key]['ink_width_fraction']=(b[1]-b[0])*s/W;metrics[key]['ink_height_fraction']=h/H;metrics[key]['ink_top_fraction_from_top']=(H/2-cursor)/H
 cursor-=h+gap
for scene in bpy.data.scenes:
 if scene.name.endswith('_v032'):scene.name=scene.name[:-5]+'_v033'
for ob in [line]+list(card.values()):ob.name=ob.name.replace('v032','v033');ob.data.name=ob.data.name.replace('v032','v033')
e.compositing_node_group.name='v033 | EDGE FILLING REAL FONT ALPHA KNOCKOUT'
m=bpy.data.scenes['WTSC_MASTER_4K_103S_v033'];m.render.filepath='//../../renders/world_v016/WTSC_Knockout_Full_Edit_v033.mp4'
report={'source':str(out),'prior_v032_sha256':prior_sha,'change':'Only ending typography enlarged; no world rerender or timing/audio/crop changes','straight_cap_height_fraction':.995,'curved_letter_overshoot':'Round glyph overshoots may crop at top/bottom for edge-filling intent','scroll_font':'Arial Black, native uniform proportions','card_font':'Impact, native uniform proportions','card_full_ink_height_fraction':.99,'card_line_gap_fraction':.015,'card_metrics':metrics,'output':[3840,2160,24],'preview_global_seconds':[82,103],'last_S_clear_boundary_seconds':100,'solid_card_seconds':[100,103],'music_fade_global_seconds':[90,100],'clean_cached_world_seconds':[52,70],'cached_world_crop':{'scale':2,'effective_detail_pixels':[1920,1080],'centered_pair':True},'native_world_camera':'Shared root horizontal follow as v032; held poses unchanged'}
e['finishing_scope_v033']=json.dumps(report)
note=bpy.data.texts.new('CURRENT v033 | Edge filling knockout and final card');note.write(json.dumps(report,indent=2))
e.frame_set(2137);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'notes/world_v016/knockout_layout_v033.json').write_text(json.dumps(report,indent=2))
e.render.image_settings.media_type='IMAGE';e.render.image_settings.file_format='PNG';e.render.resolution_percentage=100
for f in [2033,2137,2257,2400,2401]:
 e.frame_set(f);e.render.filepath=str(R/f'renders/world_v016/ending_checks_4K_v033/{f}.png');bpy.ops.render.render(write_still=True,scene=e.name)
nt=e.compositing_node_group;output=next(n for n in nt.nodes if n.type=='GROUP_OUTPUT');rl=next(n for n in nt.nodes if n.bl_idname=='CompositorNodeRLayers');nt.links.new(rl.outputs['Alpha'],output.inputs['Image'])
e.frame_set(2137);e.render.filepath=str(R/'renders/world_v016/ending_checks_4K_v033/mask_2137.png');bpy.ops.render.render(write_still=True,scene=e.name)
print('EDGE_FILLING_ENDING_SAVED',str(out),flush=True)
