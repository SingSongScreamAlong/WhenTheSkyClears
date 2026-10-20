import bpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'scripts'))
ROOT=P.parents[1]
F=P/'native/WTSC_Continuous_Coat_Walk_v024.blend'
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meshhash(o):
    values={'v':[list(v.co) for v in o.data.vertices],'p':[list(p.vertices) for p in o.data.polygons],'uv':[[list(u.uv) for u in layer.data] for layer in o.data.uv_layers]}
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()
def original_data():
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.get('rig_revision')=='v016 painted linkage audit']
    return {'meshes':{o.name:meshhash(o) for r in rigs for o in r.children if o.type=='MESH'},'rests':{r.name:{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(v) for v in b.matrix_local]} for b in r.data.bones} for r in rigs},'packed_images':{im.name:{'size':list(im.size),'sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest()} for im in bpy.data.images if im.packed_file}}
def geom_signature():
    S=bpy.context.scene;rows=[]
    for f in [1,3.25,9,17,19.25,25.25,32,63,94]:
        S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        for o in sorted(S.objects,key=lambda o:o.name):
            if o.type=='MESH' and not o.hide_render:
                e=o.evaluated_get(dg);rows.append((f,o.name,[[round(x,7) for x in e.matrix_world@v.co] for v in e.data.vertices]))
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/BASE_PAINTED_v022_COPY.blend'),load_ui=False,use_scripts=False)
original=original_data()
bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False)
current=original_data();S=bpy.context.scene
preserved={'original_rig_child_mesh_coordinates_topology_uv':original['meshes']==current['meshes'],'original_rest_bones':original['rests']==current['rests'],'packed_original_images':original['packed_images']==current['packed_images'],'mesh_count':len(original['meshes']),'packed_images':current['packed_images']}
assert all(preserved[k] for k in ['original_rig_child_mesh_coordinates_topology_uv','original_rest_bones','packed_original_images'])
before=geom_signature()
for name in ['V024_IMPORT_TIMING_AND_EDIT_GUIDE.txt','V024_VISUAL_ASSESSMENT.txt','V024_COAT_REPLACEMENT_ART_BRIEF.txt']:
    t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write((P/name).read_text())
S['V024_acceptance']='TECHNICAL PASS; ART OPEN / coat unresolved, continuous playback unobserved'
S['V024_private_preview']='[PRIVATE_LIBRARY_REFERENCE_REMOVED] version0'
S['V024_travel_contract']='D=0.9524437384576381*(F-1)/31m;30fps;world-foot goals must follow common placement'
S.frame_set(19,subframe=.25);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False)
after=geom_signature();assert before==after
S=bpy.context.scene
objects=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection]} for o in S.objects if o.get('v016_control') or 'SOLE_BONE_GOAL' in o.name or 'CHILD_SUPPORT_TRAVEL' in o.name]
inventory={'Blender_version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'body_vertex_count':len(bpy.data.objects['LOCO_BOY | PAINT body'].data.vertices),'objects':objects,'camera':{n:{'type':bpy.data.objects[n].data.type,'lens':bpy.data.objects[n].data.lens,'shift_x':bpy.data.objects[n].data.shift_x,'shift_y':bpy.data.objects[n].data.shift_y,'ortho_scale':bpy.data.objects[n].data.ortho_scale} for n in ['V024 | CLOSE portrait','V020 | CHILD | SHOT']},'preservation_vs_v022_base':preserved,'metadata_save_geometry_signature_before':before,'metadata_save_geometry_signature_after':after,'metadata_save_geometry_unchanged':before==after,'native_sha256':filehash(F),'native_bytes':F.stat().st_size,'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post)}
(P/'evidence/NATIVE_PRESERVATION_AND_INVENTORY.json').write_text(json.dumps(inventory,indent=2))
targets={'v046':('shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'),'v007':('locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de'),'v045c':('shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend','5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4')}
sourcechecks={}
for key,(path,expected) in targets.items():
    h=filehash(ROOT/path);sourcechecks[key]={'path':path,'expected':expected,'actual':h,'unchanged':h==expected};assert h==expected
sourcechecks['v023_preserved_copy']={'actual':filehash(P/'reference/PRESERVED_CONTINUOUS_v023.blend'),'current_v023':filehash(P.parent/'continuous_coat_walk_v023/native/WTSC_Continuous_Coat_Walk_v023.blend')}
assert sourcechecks['v023_preserved_copy']['actual']==sourcechecks['v023_preserved_copy']['current_v023']
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(sourcechecks,indent=2))
handoff={'status':'TECHNICAL_PASS_ART_NOT_PASSED','scope':'Isolated boy continuous walking/loading/cloth study from v021/v022; v024 follows preserved v023. No production integration.','native':str(F),'native_sha256':filehash(F),'guide':'V024_IMPORT_TIMING_AND_EDIT_GUIDE.txt','travel':'V024_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv','preview':json.loads((P/'evidence/preview_verification.json').read_text()),'private_preview':{'library_file_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','version':0,'file_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]'},'technical':json.loads((P/'evidence/fresh_continuous_native_check.json').read_text()),'observed':'Small native proof, matched coat poses, same-clock comparison, first-cycle31decoded close frames,22boundary frames,9shot frames. Frame inspection only.','actual_normal_speed_playback_observed':False,'artistic_pass':False,'visual_open_items':['Coat remains a flat painted representation with stretched baked folds; new pose-specific painting is unresolved.','Convincing loading/cadence at normal speed remains unverified without observable continuous playback.','Paired recovery-to-walk transition and production world matching are outside this solo test.'],'blockers':[{'action':'Built-in imagegen coat-only repaint','target':'v023 loading native render with original v015 design reference','reason':'AbsolutePathBuf deserialized without a base path at line1column173','status':'Failed before generation, not approval-denied; no image returned','completed':'Native pose-specific coat/cloth alternatives and continuous walking/loading refinements; matched proof and encoded movie.'},{'action':'Observe actual normal-speed playback','target':'WTSC_v024_Normal_Speed_Walk_Close_and_Shot_3p1s.mp4','reason':'Available file/DCC tools can render, decode and inspect frames but expose no observable running player','status':'Unavailable/unobserved; no playback pass claimed','completed':'93frame30fps movie, allframes decoded and selected temporal boards inspected; private upload verified.'}],'preservation':sourcechecks}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps({'native':str(F),'bytes':F.stat().st_size,'sha256':filehash(F),'preserved':preserved['original_rig_child_mesh_coordinates_topology_uv'] and preserved['original_rest_bones'] and preserved['packed_original_images'],'metadata_geometry_unchanged':before==after,'sources_unchanged':True,'status':handoff['status']}))
