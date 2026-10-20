import bpy,json,math,random
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S'];bpy.context.window.scene=world
assert bpy.data.filepath.endswith('WTSC_Living_World_v008.blend')
recipe=json.loads((ROOT/'work/living_world_details/details_recipe.json').read_text())
def move(obj,region):
    for col in list(obj.users_collection):col.objects.unlink(obj)
    bpy.data.collections['LW | '+region].objects.link(obj)
def curve_mat(name,source):
    mat=bpy.data.materials[source].copy();mat.name=name;nt=mat.node_tree
    for node in list(nt.nodes):
        if node.type=='VERTEX_COLOR':
            for link in list(node.outputs['Color'].links):link.to_socket.default_value=(1,1,1,1)
            nt.nodes.remove(node)
    geo=next(n for n in nt.nodes if n.type=='NEW_GEOMETRY')
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
    combo=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(sep.outputs['X'],combo.inputs['X']);nt.links.new(sep.outputs['Z'],combo.inputs['Y'])
    coord=next(n for n in nt.nodes if n.type=='TEX_COORD')
    for link in list(coord.outputs['UV'].links):nt.links.new(combo.outputs[0],link.to_socket)
    return mat
bark=curve_mat('LW | Continuous painted organic bark','LW | Painted Bark')
wiremat=curve_mat('LW | Metal curve without mesh attributes','LW | Painted Metal')
motion=[]
for index,(region,entry) in enumerate(recipe['tree_curves'].items()):
    obj=bpy.data.objects['LWC_'+region+'_OrganicTrees'];move(obj,region)
    for spline,radii in zip(obj.data.splines,entry['radii']):
        for point,radius in zip(spline.points,radii):point.radius=radius/.35
    obj.data.use_fill_caps=True;obj.data.materials.clear();obj.data.materials.append(bark)
    for old in bpy.data.collections['LW | '+region].objects:
        if old.type=='MESH' and '_Bark_' in old.name:old.hide_render=True;old.hide_viewport=True
    basis=obj.shape_key_add(name='Basis');wind=obj.shape_key_add(name='Wind on continuous branches')
    for point in wind.data:
        p=point.co;weight=max(0,min(1,(p.z-2.2)/4.5));p.x+=weight*.14*math.sin(p.x*.65+p.y*.2);p.y+=weight*.09*math.sin(p.z*.8+p.x*.2)
    wind.driver_add('value').driver.expression=f'.5+.5*sin(frame*.028+{index*.71})'
    motion.append({'object':obj.name,'splines':len(obj.data.splines),'key_points':len(wind.data)})
wire=bpy.data.objects['LWC_BarbedWire_Coil'];move(wire,'Battlefield');wire.data.materials.append(wiremat)

for kind,color in [('Bronze',(.23,.15,.055,1)),('Chalk',(.35,.37,.30,1)),('Bird',(.009,.014,.018,1))]:
    mat=bpy.data.materials.new('LW | Painted '+kind);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.82
    if kind=='Bronze':bs.inputs['Metallic'].default_value=.55
for entry in recipe['mesh_entries']:
    obj=bpy.data.objects[entry['name']];kind=entry['material'];region=entry['region'].replace('Props','')
    move(obj,'Atmosphere' if region.startswith('Bird') else region)
    mesh=obj.data;mesh.materials.clear();mesh.materials.append(bpy.data.materials['LW | Painted '+kind])
    uv=mesh.uv_layers.new(name='Paint UV metre scale')
    for face in mesh.polygons:
        axis=max(range(3),key=lambda a:abs(face.normal[a]));dims=(0,2) if axis==1 else ((1,2) if axis==0 else (0,1))
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p[dims[0]],p[dims[1]])
    attr=mesh.color_attributes.new(name='PaintVariation',type='FLOAT_COLOR',domain='CORNER');colors=[]
    for face,tint in zip(mesh.polygons,entry['face_tints']):
        for li in face.loop_indices:colors.extend((tint,tint,tint,1))
    attr.data.foreach_set('color',colors)
    if kind=='Bird':
        idx=int(entry['region'][4:]);obj.shape_key_add(name='Basis');flap=obj.shape_key_add(name='Wing flap')
        for v in flap.data:
            if abs(v.co.x)>.2:v.co.z-=.22
        flap.driver_add('value').driver.expression=f'.5+.5*sin(frame*.48+{idx})'
        obj.driver_add('location',0).driver.expression=f'-8+frame*.025+{idx*.65}'
        obj.location.y=30+idx*2;obj.driver_add('location',2).driver.expression=f'{7.6+idx*.3}+.07*sin(frame*.08+{idx})'
        for frame,scale in [(1,1),(601,1),(865,0),(2401,0)]:obj.scale=(scale,)*3;obj.keyframe_insert('scale',frame=frame)

# Continuous paint across wall pieces hides construction-cell color seams.
for obj in bpy.data.collections['20 | LIVING WORLD dimensional sets'].all_objects:
    if obj.type=='MESH' and '_Plaster_' in obj.name:
        attr=obj.data.color_attributes.get('PaintVariation')
        if attr:attr.data.foreach_set('color',[1.,1.,1.,1.]*len(attr.data))

# A small, gently rising chimney plume supplies domestic movement in the opening.
fx=bpy.data.collections['LW | Atmosphere']
smoke=bpy.data.materials['LW | Thin woodland air'].copy();smoke.name='LW | Bakery chimney soft smoke'
for node in smoke.node_tree.nodes:
    if node.type=='MATH' and node.operation=='MULTIPLY':node.inputs[1].default_value=.15
    if node.type=='PRINCIPLED_VOLUME':node.inputs['Color'].default_value=(.44,.46,.45,1)
for j in range(5):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(3.56,7.85,7.2))
    obj=bpy.context.object;move(obj,'Atmosphere');obj.name=f'LW Chimney rising soft smoke {j}';obj.data.materials.append(smoke)
    phase=j*.36;expr=f'((frame/60+{phase})%1.8)'
    obj.driver_add('location',0).driver.expression=f'3.56+.16*{expr}'
    obj.driver_add('location',2).driver.expression=f'7.2+{expr}'
    for axis,factor in enumerate([.36,.30,.39]):obj.driver_add('scale',axis).driver.expression=f'.002+{factor}*sin(3.14159265*{expr}/1.8)'

# The distant sky paint drifts slowly across a native UV transform.
sky=bpy.data.objects['Painted sky | warm left to cold right'].data.materials[0]
nt=sky.node_tree
for tex in [n for n in nt.nodes if n.type=='TEX_IMAGE']:
    coords=nt.nodes.new('ShaderNodeTexCoord');add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';nt.links.new(coords.outputs['UV'],add.inputs[0]);nt.links.new(add.outputs[0],tex.inputs['Vector']);tex.extension='EXTEND'
    add.inputs[1].driver_add('default_value',0).driver.expression='frame*.000004'

world.frame_set(1);master.frame_set(1);world.render.resolution_percentage=100
world.render.filepath='//../../renders/living_world/still_'
master.render.filepath='//../../renders/living_world/WTSC_Living_World_4K_v009.mp4'
world['production_stage']='Dimensional living-world iteration v009; editable curves and original meshes; artist review pending'
world['environment_motion']+=' Continuous tapered branch curves, flapping distant birds, chimney smoke and drifting painted sky.'
bpy.data.texts['READ ME | LIVING WORLD v008'].write('\nV009 refinement: continuous tapered branch curves replace the segmented bark meshes; wall paint is continuous; cart/barrels, school bell, bedrolls, wire, distant birds, chimney smoke and slow sky drift are added. The previous sources are preserved.\n')
target=ROOT/'shots/world/WTSC_Living_World_v009.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
(ROOT/'notes/living_world/native_details_v009.json').write_text(json.dumps({'source':str(target),'tree_motion':motion,'detail_meshes':len(recipe['mesh_entries']),'character_motion':'Held GP drawing; location keys only. Reference-guided character motion deferred.'},indent=2))
print(json.dumps({'saved':str(target),'tree_motion':motion,'objects':len(world.objects)}))
