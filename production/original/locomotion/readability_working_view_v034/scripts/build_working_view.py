"""Readability diagnostic only. Material separation and measured guides; no motion edits."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];SRC=P/'reference/FINAL_DARK_v033.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];fg=bpy.data.collections['V025 | retained foreground identity'];fg_names={o.name for o in fg.all_objects};coat=bpy.data.objects['V025 | COAT drawings | editable GP'];handnames={s:'V007_BOY | articulated drawn hand '+s for s in ['near','far']}
def action_hash(a):
    return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
def mesh_hash(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[[tuple(v.co) for v in k.data] for k in m.shape_keys.key_blocks] if m.shape_keys else [])).encode()).hexdigest()
actions={a.name:action_hash(a) for a in bpy.data.actions};meshes={m.name:mesh_hash(m) for m in bpy.data.meshes};cache={};templates={}
for f in range(1,33):
    S.frame_set(f);bpy.context.view_layer.update();fore.update();inv=T.matrix_world.inverted();r={'joints':{},'hands':{},'cloth':[]}
    for side in ['near','far']:
        b=rig.pose.bones;r['joints'][side]={k:inv@(rig.matrix_world@p) for k,p in [('S',b['upper_arm_'+side].head),('E',b['forearm_'+side].head),('W',b['hand_'+side].head),('H',b['thigh_'+side].head),('K',b['shin_'+side].head),('A',b['foot_'+side].head),('TIP',b['hand_'+side].tail)]};o=bpy.data.objects[handnames[side]];vl=fore if o.name in fg_names else bpy.context.view_layer;e=o.evaluated_get(vl.depsgraph);r['hands'][side]=[inv@(e.matrix_world@v.co) for v in e.data.vertices]
        if f==1:
            tmp=e.to_mesh(preserve_all_data_layers=True,depsgraph=vl.depsgraph);templates[side]=tmp.copy();e.to_mesh_clear()
    fr=next(fr for fr in coat.data.layers[0].frames if fr.frame_number==f);r['cloth']=[inv@(coat.matrix_world@p.position) for p in fr.drawing.strokes[0].points];cache[f]=r
cloth=cache[1]['cloth'];top=max(v.z for v in cloth);low=min(v.z for v in cloth);upper=[i for i,v in enumerate(cloth) if v.z>=top-.12];lower=[i for i,v in enumerate(cloth) if v.z<=low+.11];indices={'collar':max(range(len(cloth)),key=lambda i:cloth[i].z),'attach_back':min(upper,key=lambda i:cloth[i].x),'attach_front':max(upper,key=lambda i:cloth[i].x),'hem_back':min(lower,key=lambda i:cloth[i].x),'hem_front':max(lower,key=lambda i:cloth[i].x),'hem_low':min(range(len(cloth)),key=lambda i:cloth[i].z)}
def color_copy(orig,name,color):
    m=orig.copy();m.name='V034 DIAGNOSTIC | '+name;orig.use_fake_user=True
    for n in m.node_tree.nodes:
        inp=n.inputs.get('Color') if n.type=='EMISSION' else n.inputs.get('Base Color') if n.type=='BSDF_PRINCIPLED' else None
        if inp:
            for l in list(inp.links):m.node_tree.links.remove(l)
            inp.default_value=(*color,1)
    return m
def matte(name,color):
    m=bpy.data.materials.new('V034 DIAGNOSTIC | '+name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
colors={};originals={};workmats={};opacity={}
for o in list(S.objects):
    if o.type!='MESH' or o.hide_render:continue
    side='near' if 'near' in o.name else 'far'
    if o.name in handnames.values():role='hand';c=(.76,.50,.32) if side=='near' else (.64,.55,.43)
    elif 'drawn skin' in o.name:role='forearm';c=(.62,.42,.29) if side=='near' else (.52,.46,.37)
    elif 'drawn sleeve' in o.name:role='sleeve';c=(.46,.54,.57) if side=='near' else (.32,.41,.44)
    elif 'source gray cuff' in o.name:role='sleeve cuff';c=(.82,.77,.58)
    elif 'V024 continuous' in o.name:role='trouser';c=(.24,.31,.35) if side=='near' else (.42,.47,.49)
    elif o.name=='LOCO_BOY | PAINT body':role='retained collar';c=(.57,.60,.57)
    else:continue
    originals[o.name]=[s.material.name for s in o.material_slots];colors[o.name]=c
    for i,slot in enumerate(o.material_slots):
        orig=slot.material
        if not orig:continue
        m=color_copy(orig,o.name+' '+role,c);slot.link='OBJECT';slot.material=m
        if role=='hand':opacity[side]={n.name:n.outputs[0].default_value for n in orig.node_tree.nodes if n.type=='VALUE'};workmats[side]=m.name
    if role=='trouser':
        cuff=color_copy(o.data.materials[0],o.name+' mapped rolled cuff',(.72,.70,.56));idx=len(o.data.materials);o.data.materials.append(cuff)
        for p in o.data.polygons:
            t=sum((v//7)/96 for v in p.vertices)/len(p.vertices)
            if .79<=t<=.927:p.material_index=idx
gpcolors=[(.36,.40,.41,1),(.16,.21,.23,.60),(.65,.69,.67,.72),(.62,.66,.62,.7),(.08,.13,.15,.75),(.20,.24,.25,.14),(.8,.8,.8,.75)]
for i,orig in enumerate(list(coat.data.materials)):
    m=orig.copy();orig.use_fake_user=True;m.name='V034 DIAGNOSTIC | coat value '+str(i);m.grease_pencil.fill_color=gpcolors[i];m.grease_pencil.color=gpcolors[i];coat.data.materials[i]=m
guidecol=bpy.data.collections.new('V034 | DIAGNOSTIC joint and cloth guides');fg.children.link(guidecol);xraycol=bpy.data.collections.new('V034 | DIAGNOSTIC hand xray overlay');fg.children.link(xraycol)
gp=bpy.data.grease_pencils.new('V034 | measured joint and cloth drawings');go=bpy.data.objects.new('V034 | guides | actual joints and drawn cloth samples',gp);guidecol.objects.link(go);go.parent=T;gp.stroke_depth_order='3D';layer=gp.layers.new('Measured guides on native source frames',set_active=True);layer.use_lights=False
def gpmat(name,color,fill,stroke):
    m=bpy.data.materials.new('V034 GUIDE | '+name);bpy.data.materials.create_gpencil_data(m);m.grease_pencil.show_fill=fill;m.grease_pencil.show_stroke=stroke;m.grease_pencil.fill_color=(*color,1);m.grease_pencil.color=(*color,1);gp.materials.append(m);return len(gp.materials)-1
mi={k:gpmat(k,c,True,False) for k,c in [('near',(.95,.24,.055)),('far',(.025,.40,.92)),('attach',(.02,.60,.46)),('hem',(.65,.06,.55))]};line={k:gpmat(k+' line',c,False,True) for k,c in [('near',(.95,.24,.055)),('far',(.025,.40,.92)),('attach',(.02,.60,.46)),('hem',(.65,.06,.55))]}
def draw(d,V,mat,closed=False,radius=.002):
    d.add_strokes([len(V)]);s=d.strokes[-1];s.cyclic=closed;s.material_index=mat;s.fill_id=len(d.strokes) if closed else 0;s.fill_opacity=1;s.fill_color=(0,0,0,0)
    for p,v in zip(s.points,V):p.position=(v.x,-.31,v.z);p.radius=radius;p.opacity=1
def dot(d,p,k,shape='circle',r=.009):
    if shape=='circle':V=[p+Vector((r*math.cos(i*math.tau/20),0,r*math.sin(i*math.tau/20))) for i in range(20)]
    else:V=[p+Vector((r,0,0)),p+Vector((0,0,r)),p+Vector((-r,0,0)),p+Vector((0,0,-r))]
    draw(d,V,mi[k],True)
def clothpath(a,b,upperpath):
    n=len(cloth);paths=[]
    for sg in [1,-1]:
        path=[a];j=a
        while j!=b:j=(j+sg)%n;path.append(j)
        paths.append(path)
    return (max if upperpath else min)(paths,key=lambda p:sum(cloth[i].z for i in p)/len(p))
topPath=clothpath(indices['attach_back'],indices['attach_front'],True);hemPath=clothpath(indices['hem_back'],indices['hem_front'],False)
for f in range(1,32):
    d=layer.frames.new(f).drawing;r=cache[f]
    for side in ['far','near']:
        j=r['joints'][side]
        for chain in [['S','E','W','TIP'],['H','K','A']]:draw(d,[j[k] for k in chain],line[side],radius=.002)
        for key in ['S','E','W','H','K','A']:dot(d,j[key],side,'circle' if side=='near' else 'diamond')
    V=r['cloth'];draw(d,[V[i] for i in topPath],line['attach'],radius=.0025);draw(d,[V[i] for i in hemPath],line['hem'],radius=.0025)
    for key,i in indices.items():dot(d,V[i],'attach' if key.startswith('attach') or key=='collar' else 'hem','diamond',.008)
    d.tag_positions_changed()
for f in range(32,281):layer.frames.copy(1+(f-1)%31,f,instance_drawing=True)
for side in ['near','far']:
    mesh=templates[side];coords=[]
    for f in range(1,32):coords.append([Vector((v.x,-.27,v.z)) for v in cache[f]['hands'][side]])
    mesh.vertices.foreach_set('co',[x for v in coords[0] for x in v]);ob=bpy.data.objects.new('V034 | XRAY actual '+side+' hand | diagnostic only',mesh);xraycol.objects.link(ob);ob.parent=T;mesh.materials.clear();mesh.materials.append(matte('xray '+side+' actual hand',(.83,.57,.34) if side=='near' else (.62,.64,.75)));ob.shape_key_add(name='Basis')
    for i in range(1,31):
        kb=ob.shape_key_add(name='Actual source pose '+str(i+1));kb.data.foreach_set('co',[x for v in coords[i] for x in v])
        for f in range(1,33):kb.value=float((f-1)%31==i);kb.keyframe_insert('value',frame=f)
    for l in mesh.shape_keys.animation_data.action.layers:
        for st in l.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
                    fc.modifiers.new('CYCLES')
changed_actions=[n for n,h in actions.items() if action_hash(bpy.data.actions[n])!=h];changed_meshes=[n for n,h in meshes.items() if mesh_hash(bpy.data.meshes[n])!=h];assert not changed_actions and not changed_meshes
report={'diagnostic_only':True,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'original_motion_actions_changed':changed_actions,'original_mesh_vertex_or_shape_coordinates_changed':changed_meshes,'working_materials':colors,'original_materials':originals,'working_hand_materials':workmats,'original_hand_opacity_value_nodes':opacity,'cloth_guide_indices_on_actual_outer_contour':indices,'cloth_guide_meaning':'Samples on the existing drawn upper attachment region and free hem; not newly invented physical cloth constraints. Same point indices tracked through31drawings.','anatomical_guides':'Actual source rig shoulder/elbow/wrist/hip/knee/ankle; near orange circles, far blue diamonds. Short continuation from wrist shows native hand-bone axis.','xray_hands':'Exact evaluated source hand vertex shapes projected forward at unchanged X/Z solely for diagnostic guided view. WORKING view retains actual depth/occlusion.','no_lighting_change':True}
(P/'evidence/WORKING_VIEW_BUILD.json').write_text(json.dumps(report,indent=2));text=bpy.data.texts.new('V034_DIAGNOSTIC_README');text.write('Diagnostic only. V028/v033 motion and final art preserved in reference/FINAL_DARK_v033.blend. Working values are temporary. Hide V034 hand xray overlay and joint/cloth guide collections for actual-depth lighter view. Xray projects original hand meshes forward at identical X/Z; it is not new anatomy or final layering. Cloth diamonds are measured outline samples, not physical constraints.');S['V034_status']='READABILITY DIAGNOSTIC ONLY. Temporary values, measured joints/cloth guides and explicitly labelled hand xray. No movement, lighting or final-art change.';S.frame_set(20);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Readability_Working_View_v034.blend'),compress=True);print('V034_WORKING_VIEW_BUILT',json.dumps(report),flush=True)
