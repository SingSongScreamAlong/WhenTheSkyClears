import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];source=P/'reference/FINAL_DARK_v033.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];fore=S.view_layers['V025 | original foreground'];fg={o.name for o in bpy.data.collections['V025 | retained foreground identity'].all_objects};report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'version':bpy.app.version_string,'no_render_or_native_write':True,'objects':{},'frames':{},'rest_bone_lengths':{b.name:b.length for b in rig.data.bones if any(x in b.name for x in ['arm','hand','thigh','shin','chest','pelvis'])}}
names=[o.name for o in S.objects if (o.type=='MESH' and not o.hide_render and ('BOY' in o.name or 'V024 continuous' in o.name or 'V033' in o.name)) or o.name=='V025 | COAT drawings | editable GP']
for n in names:
    o=bpy.data.objects[n];r={'type':o.type,'collections':[c.name for c in o.users_collection],'render_hidden':o.hide_render,'parent':o.parent.name if o.parent else None,'foreground':n in fg,'materials':[]}
    for m in o.data.materials:
        if not m:continue
        d={'name':m.name}
        if m.is_grease_pencil:d.update({'fill':list(m.grease_pencil.fill_color),'stroke':list(m.grease_pencil.color),'show_fill':m.grease_pencil.show_fill,'show_stroke':m.grease_pencil.show_stroke})
        elif m.use_nodes:d.update({'nodes':[(x.name,x.type) for x in m.node_tree.nodes],'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name) for l in m.node_tree.links]})
        r['materials'].append(d)
    if o.type=='MESH':r.update({'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'groups':[g.name for g in o.vertex_groups],'shape_keys':[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [],'modifiers':[m.type for m in o.modifiers]})
    report['objects'][n]=r
for f in range(1,33):
    S.frame_set(f);bpy.context.view_layer.update();fore.update();row={'joints':{},'hands':{}}
    for side in ['near','far']:
        bones=rig.pose.bones;row['joints'][side]={key:list(rig.matrix_world@pos) for key,pos in [('shoulder',bones['upper_arm_'+side].head),('elbow',bones['forearm_'+side].head),('wrist',bones['hand_'+side].head),('hip',bones['thigh_'+side].head),('knee',bones['shin_'+side].head),('ankle',bones['foot_'+side].head)]};n='V007_BOY | articulated drawn hand '+side;o=bpy.data.objects[n];vl=fore if n in fg else bpy.context.view_layer;e=o.evaluated_get(vl.depsgraph);V=[e.matrix_world@v.co for v in e.data.vertices];h={'bounds_world':[[min(v[i] for v in V),max(v[i] for v in V)] for i in range(3)],'views':{}}
        for mode,camname,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
            S.render.resolution_x,S.render.resolution_y=size;cam=bpy.data.objects[camname];pv=[world_to_camera_view(S,cam,v) for v in V];bb=[min(v.x for v in pv)*size[0],(1-max(v.y for v in pv))*size[1],max(v.x for v in pv)*size[0],(1-min(v.y for v in pv))*size[1]];h['views'][mode]={'bbox_pixels':bb,'width_pixels':bb[2]-bb[0],'height_pixels':bb[3]-bb[1]}
        row['hands'][side]=h
    coat=bpy.data.objects['V025 | COAT drawings | editable GP'];fr=next(fr for fr in coat.data.layers[0].frames if fr.frame_number==f);rows=[]
    for i,st in enumerate(fr.drawing.strokes):
        VV=[coat.matrix_world@p.position for p in st.points];rows.append({'stroke':i,'material_index':st.material_index,'points':len(VV),'cyclic':st.cyclic,'fill_color':list(st.fill_color),'fill_opacity':st.fill_opacity,'bounds_xyz':[[min(v[k] for v in VV),max(v[k] for v in VV)] for k in range(3)]})
    row['coat_strokes']=rows;report['frames'][f]=row
(P/'evidence/ACTUAL_GEOMETRY_READABILITY_AUDIT.json').write_text(json.dumps(report,indent=2));print('V034_READABILITY_AUDIT',json.dumps({'objects':{n:{k:v for k,v in r.items() if k!='materials'} for n,r in report['objects'].items()},'materials':{n:r['materials'] for n,r in report['objects'].items() if 'hand ' in n or 'COAT' in n},'bone_lengths':report['rest_bone_lengths'],'selected_hands':{f:report['frames'][f]['hands'] for f in [1,11,20,27]}},indent=2),flush=True)
