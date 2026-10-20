import bpy,json,hashlib,math,struct
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');target=R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v037.blend';assert not target.exists()
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v036'];e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v035'];master=bpy.data.scenes['WTSC_MASTER_4K_103S_v035'];bpy.context.window.scene=w;w.frame_set(1)
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');position=pair.data.layers[0].frames[0].drawing.attributes['position'].data
sole=min((pair.matrix_world@p.vector).z for p in position);depth=min((pair.matrix_world@p.vector).y for p in position)
floor_slope=(3-sole)/(16+depth);grounded=[]
for root in [o for o in w.objects if o.type=='EMPTY' and o.name.startswith('v036 | ') and 'fixed emitter' in o.name]:
 oldz=root.location.z;newz=3-floor_slope*(root.location.y+16);delta=newz-oldz;root.location.z=newz;label=root.name.split(' | ')[1]
 for o in w.objects:
  if o.name.startswith('v036 | '+label+' | charred hearth stone '):o.location.z+=delta
 for m in bpy.data.materials:
  if not m.node_tree:continue
  for n in m.node_tree.nodes:
   if n.type=='VECT_MATH' and n.operation=='DISTANCE' and abs(n.inputs[1].default_value[0]-root.location.x)<.001 and abs(n.inputs[1].default_value[1]-root.location.y)<.001:n.inputs[1].default_value[2]+=delta
 label_old={'Camp hearth':'Camp smoke','Battlefield burn':'Battlefield smoke','Distant ruin burn':'Far battlefield smoke'}.get(label)
 if label_old:
  flameh=next(o.data.vertices[-1].co.z for o in w.objects if o.name.startswith('v036 | '+label+' | painted flame 0'))
  for o in w.objects:
   if o.name.startswith('v016 | '+label_old+' | wisp '):o.location.z=newz+flameh*.55
 grounded.append({'emitter':root.name,'old_z':oldz,'grounded_z':newz,'x_y':list(root.location[:2]),'method':'World floor ray aligned with existing painted foot contact at native depth; hearth, light, smoke and flame remain attached.'})
# Static edge masks belong to each whole painting, never to timeline visibility.
edge_materials=[]
for m in set(o.data.materials[0] for o in w.objects if o.type=='MESH' and any('Regional painted sets' in c.name for c in o.users_collection)):
 nt=m.node_tree;mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');old=mix.inputs[0].links[0].from_socket
 uv=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0]);r=nt.nodes.new('ShaderNodeValToRGB');r.name='STATIC paint edge overlap | no time input';r.color_ramp.elements[0].position=0;r.color_ramp.elements[0].color=(0,0,0,1);r.color_ramp.elements[1].position=1;r.color_ramp.elements[1].color=(0,0,0,1)
 for p in [.035,.965]:el=r.color_ramp.elements.new(p);el.color=(1,1,1,1)
 r.color_ramp.interpolation='EASE';nt.links.new(sep.outputs['X'],r.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(r.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0]);edge_materials.append(m.name)
w.name='WTSC_WORLD_CORRECTED_v037';w['duration_status']='100s confirmed; full-film knockout and6s silent credits in106s master.'
e.name='WTSC_FULL_FILM_KNOCKOUT_v037';e.frame_start=1;e.frame_end=2544;e.render.resolution_percentage=100;e.render.resolution_x=3840;e.render.resolution_y=2160;e.render.fps=24
bpy.context.window.scene=e;e.frame_set(1)
line=next(o for o in e.objects if 'Moving knockout' in o.name);line.name='v037 | Entire film | WHEN THE SKY CLEARS'
for ob in list(e.objects):
 if 'Final card' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
def bounds(ob):
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();v=[p.co.copy() for p in mesh.vertices];ev.to_mesh_clear();return [min(p.x for p in v),max(p.x for p in v),min(p.y for p in v),max(p.y for p in v)]
view=e.camera.data.view_frame(scene=e);W=max(v.x for v in view)-min(v.x for v in view);H=max(v.y for v in view)-min(v.y for v in view)
b=bounds(line);scale=line.scale.x;line.animation_data_clear()
for f,x in [(1,W/2-b[0]*scale),(2401,-W/2-b[1]*scale)]:line.location.x=x;line.keyframe_insert('location',index=0,frame=f)
for f,hidden in [(1,False),(2400,False),(2401,True)]:line.hide_render=hidden;line.keyframe_insert('hide_render',frame=f)
display=bpy.data.fonts.load(r'C:\Windows\Fonts\impact.ttf');support=bpy.data.fonts.load(r'C:\Windows\Fonts\arial.ttf')
mat=line.data.materials[0]
def text(name,body,font):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.font=font;d.align_x='LEFT';d.align_y='BOTTOM_BASELINE';d.resolution_u=12;d.materials.append(mat);o=bpy.data.objects.new(name,d);e.collection.objects.link(o);return o
spec=[('WHEN THE',display,'width',.96*W),('SKY CLEARS.',display,'width',.96*W),('The Animated Series.',support,'height',.065*H),('2027.',display,'height',.10*H),('A Two Truck Productions project.',support,'height',.040*H)]
card=[];heights=[]
for i,(body,font,kind,target_value) in enumerate(spec):
 ob=text('v037 | Credits | '+str(i)+' | '+body,body,font);b=bounds(ob);sc=target_value/(b[1]-b[0] if kind=='width' else b[3]-b[2]);ob.scale=(sc,sc,sc);card.append((ob,b,sc));heights.append((b[3]-b[2])*sc)
gap=(.97*H-sum(heights))/4;assert gap>.01*H
cursor=.485*H;card_metrics=[]
for (ob,b,sc),height in zip(card,heights):
 ob.location.x=-(b[0]+b[1])*sc/2;ob.location.y=cursor-b[3]*sc;cursor-=height+gap
 for f,hidden in [(1,True),(2400,True),(2401,False)]:ob.hide_render=hidden;ob.keyframe_insert('hide_render',frame=f)
 card_metrics.append({'body':ob.data.body,'font':ob.data.font.filepath,'width_fraction':(b[1]-b[0])*sc/W,'height_fraction':height/H})
def interpolate(id):
 if not id.animation_data or not id.animation_data.action:return
 for l in id.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR' if fc.data_path=='location' else 'CONSTANT'
for ob in [line]+[x[0] for x in card]:interpolate(ob)
old_nt=e.compositing_node_group
nt=bpy.data.node_groups.new('v037 | Entire100s true native world through Font alpha','CompositorNodeTree');e.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
glyph=nt.nodes.new('CompositorNodeRLayers');glyph.scene=e;glyph.name='NATIVE GLYPH ALPHA | entire0–100';glyph.location=(-650,200)
world=nt.nodes.new('CompositorNodeRLayers');world.scene=w;world.name='CORRECTED NATIVE WORLD | no cached fading movie';world.location=(-900,-180)
glare=nt.nodes.new('CompositorNodeGlare');glare.inputs['Type'].default_value='Fog Glow';glare.inputs['Quality'].default_value='High';glare.inputs['Threshold'].default_value=1.45;glare.inputs['Strength'].default_value=.22;glare.inputs['Size'].default_value=.18;glare.name='Contained fire glow | masked after lighting';glare.location=(-650,-100);nt.links.new(world.outputs['Image'],glare.inputs['Image'])
def mix(name):n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type='MIX';n.name=name;return n
fill=mix('Live world0–100 / white credits100–106');fill.location=(-350,-40);nt.links.new(glare.outputs['Image'],fill.inputs[6]);fill.inputs[7].default_value=(1,1,1,1)
for f,v in [(1,0),(2400,0),(2401,1)]:fill.inputs[0].default_value=v;fill.inputs[0].keyframe_insert('default_value',frame=f)
mask=mix('EXACT BLACK OUTSIDE NATIVE LETTERS');mask.location=(-50,120);mask.inputs[6].default_value=(0,0,0,1);nt.links.new(glyph.outputs['Alpha'],mask.inputs[0]);nt.links.new(fill.outputs[2],mask.inputs[7]);output=nt.nodes.new('NodeGroupOutput');output.location=(200,120);nt.links.new(mask.outputs[2],output.inputs['Image']);interpolate(nt)
if old_nt.users==0:bpy.data.node_groups.remove(old_nt)
for image in list(bpy.data.images):
 if image.source=='MOVIE' and image.users==0:bpy.data.images.remove(image)
master.name='WTSC_MASTER_4K_106S_v037';master.frame_start=1;master.frame_end=2544;master.render.filepath='//../../renders/world_v016/WTSC_Full_Knockout_Trailer_4K_v037.mp4'
seq=master.sequence_editor
for strip in list(seq.strips):
 if strip.type=='SCENE':seq.strips.remove(strip)
picture=seq.strips.new_scene('PICTURE | native full-film knockout0–100 + credits100–106',e,channel=2,frame_start=1);picture.scene_input='CAMERA'
assert picture.frame_final_duration==2544
sound=next(x for x in seq.strips if x.type=='SOUND');assert sound.frame_final_duration==2400
for marker in list(master.timeline_markers):master.timeline_markers.remove(marker)
for name,f in [('Knockout begins |0s',1),('Music fade |90s',2161),('LastS clears / credits |100s',2401),('Silent credits end |106s',2545)]:master.timeline_markers.new(name,frame=f)
font_rows=[]
for p in [Path(r'C:\Windows\Fonts\ariblk.ttf'),Path(r'C:\Windows\Fonts\impact.ttf'),Path(r'C:\Windows\Fonts\arial.ttf')]:
 raw=p.read_bytes();n=struct.unpack_from('>H',raw,4)[0];fs=None
 for i in range(n):
  tag,checksum,offset,length=struct.unpack_from('>4sIII',raw,12+i*16)
  if tag==b'OS/2':fs=struct.unpack_from('>H',raw,offset+8)[0]
 font_rows.append({'installed_path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'fsType':fs})
report={'source':str(target),'world_scene':w.name,'picture_scene':e.name,'master_scene':master.name,'resolution':[3840,2160],'fps':24,'moving_seconds':100,'silent_credits_seconds':6,'total_seconds':106,'total_frames':2544,'entire_world_masked':True,'scroll_keys_frames':[1,2401],'last_S_clear_boundary_seconds':100,'card_exact_lines':[a[0] for a in spec],'card_geometry':card_metrics,'card_height_fraction':.97,'static_edge_overlap_materials':edge_materials,'grounded_fire_roots':grounded,'fonts':font_rows,'font_video_rights':'https://learn.microsoft.com/en-us/typography/fonts/font-faq','font_scope':'Installed Windows fonts render into movie pixels; native editable source stays local; no raw font redistribution requested.','audio':'Original supplied100sWAV unchangedstart0; single90–100fade; silent100–106.','picture_source':'Fresh corrected native world all0–100. No obsolete cached fading-world footage.','scope':'Held near-age pair; whole-pair route only. No gait/acting. All prior versions preserved.'}
e['v037_scope']=json.dumps(report);note=bpy.data.texts.new('CURRENT v037 | FULL100s knockout + exact6s credits');note.write(json.dumps(report,indent=2));bpy.context.window.scene=master;master.frame_set(1);w.frame_set(1);e.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/full_knockout_build_v037.json').write_text(json.dumps(report,indent=2));(R/'notes/world_v016/font_verification_v037.json').write_text(json.dumps({'fonts':font_rows,'rights_source':report['font_video_rights'],'scope':report['font_scope']},indent=2));print('FULL_FILM_NATIVE_MASTER_SAVED',str(target),flush=True)
# Readback at native4K. Cross-scene RenderLayers must supply the corrected world.
bpy.context.window.scene=e;e.render.image_settings.media_type='IMAGE';e.render.image_settings.file_format='PNG';e.render.resolution_percentage=100
for f in [241,841,1201,1609,2161,2400,2401]:
 e.frame_set(f);e.render.filepath=str(R/f'renders/world_v016/full_knockout_checks_v037/{f}.png');bpy.ops.render.render(write_still=True,scene=e.name)
