import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;R=Path(r'WTSC_LOCAL_WORKSPACE')
CAND=O/'WTSC_Continuous_Facade_Painterly_Candidate.png';SOURCE=O.parent/'facade_continuity_v054/School_LARGER_CONTINUOUS_REGION_NATIVE_624x416_v054.png'
PAINT=O/'WTSC_Continuous_Facade_Source_Lighting_v056.exr';RECIPE=O/'WTSC_Continuous_Facade_Lighting_Recipe_v056.blend'
assert not PAINT.exists() and not RECIPE.exists()
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='v056_CONTINUOUS_PAINT_SOURCE_LIGHTING_RECIPE';nt=bpy.data.node_groups.new('v056 | candidate detail with source broad colour and lighting','CompositorNodeTree');s.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');out=nt.nodes.new('NodeGroupOutput')
def image(path,name):
 n=nt.nodes.new('CompositorNodeImage');n.name=name;n.image=bpy.data.images.load(str(path),check_existing=True);n.image.pack();return n.outputs['Image']
def blur(sock,size,name):
 n=nt.nodes.new('CompositorNodeBlur');n.name=name;n.inputs['Size'].default_value=(size,size);n.inputs['Type'].default_value='Gaussian';nt.links.new(sock,n.inputs['Image']);return n.outputs[0]
def resize(sock):
 n=nt.nodes.new('CompositorNodeScale');n.inputs['Type'].default_value='Absolute';n.inputs['X'].default_value=1536;n.inputs['Y'].default_value=1024;n.inputs['Interpolation'].default_value='Bilinear';nt.links.new(sock,n.inputs['Image']);return n.outputs[0]
def vm(op,a,b):
 n=nt.nodes.new('ShaderNodeVectorMath');n.operation=op
 for i,v in enumerate([a,b]):
  if isinstance(v,tuple):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs['Vector']
candidate=image(CAND,'PAINTERLY CANDIDATE | source1536x1024 | libraryv0');old=image(SOURCE,'EXACT ORIGINAL624x416 | low-frequency colour reference')
# Matching physical bandwidth, not an original-image sharpening operation.
old_low=resize(blur(old,8.,'Original broad light/material colour |8source px'))
new_low=blur(candidate,8.*1536/624,'Candidate broad light/material colour |same source bandwidth')
ratio=vm('DIVIDE',vm('ADD',old_low,(.004,.004,.004)),vm('ADD',new_low,(.004,.004,.004)))
ratio=vm('MINIMUM',vm('MAXIMUM',ratio,(.35,.35,.35)),(2.8,2.8,2.8))
corrected=vm('MULTIPLY',candidate,ratio);nt.links.new(corrected,out.inputs['Image'])
cam=bpy.data.objects.new('v056 recipe camera',bpy.data.cameras.new('v056 recipe camera'));s.collection.objects.link(cam);cam.location=(0,0,10);s.camera=cam
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=1;s.render.resolution_x=1536;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';s.render.dither_intensity=0;s.render.filepath=str(PAINT)
s['method']='Full candidate paint, normalized perRGB channel to original coarse colour/lighting. Original silhouette alpha retained in final native world shader. Original source never sharpened. No new procedural grain.'
s['source_candidate_library_id']='[PRIVATE_LIBRARY_REFERENCE_REMOVED]';s['source_candidate_file_id']='[PRIVATE_LIBRARY_REFERENCE_REMOVED]';s['source_candidate_native_size']=[1536,1024]
bpy.ops.wm.save_as_mainfile(filepath=str(RECIPE),compress=True);bpy.ops.render.render(write_still=True,scene=s.name)
base=(O.parent/'facade_candidate_v053/test_registered_candidate.py').read_text()
base=base.replace('task\\facade_candidate_v053','task\\facade_continuous_v056')
base=base.replace("IMAGE=O/'WTSC_Facade_Reference_Painted_Candidate.png'","IMAGE=O/'WTSC_Continuous_Facade_Source_Lighting_v056.exr'")
base=base.replace('WTSC_Registered_Facade_Candidate_TEST_v053.blend','WTSC_Continuous_Facade_Source_Lighting_TEST_v056.blend')
base=base.replace('v053 | candidate registered to original plaster patch | TEST ONLY','v056 | continuous painterly facade source lighting | TEST ONLY')
base=base.replace("mn('SUBTRACT',x,1004),84","mn('SUBTRACT',x,824),624").replace("mn('SUBTRACT',y,475),163","mn('SUBTRACT',y,324),416")
base=base.replace("mn('SUBTRACT',x,1004),mn('SUBTRACT',1088,x),mn('SUBTRACT',y,475),mn('SUBTRACT',638,y)","mn('SUBTRACT',x,824),mn('SUBTRACT',1448,x),mn('SUBTRACT',y,324),mn('SUBTRACT',740,y)")
base=base.replace("n.inputs['From Max'].default_value=6","n.inputs['From Max'].default_value=24")
base=base.replace("im.pack();im['library_file_id']","im.pack();im.colorspace_settings.name='Non-Color';im['source_candidate_library_file_id']")
base=base.replace("im['library_version']","im['source_candidate_library_version']").replace("im['original_file_id']","im['source_candidate_file_id']").replace("im['source_bytes_sha256']","im['derived_image_sha256']")
base=base.replace('[PRIVATE_LIBRARY_REFERENCE_REMOVED]','[PRIVATE_LIBRARY_REFERENCE_REMOVED]').replace('[PRIVATE_LIBRARY_REFERENCE_REMOVED]','[PRIVATE_LIBRARY_REFERENCE_REMOVED]')
# Preserve the exact existing broken-window painting behind the native window depth.
protection="""
window_inside=1.
for dist in [mn('SUBTRACT',x,864),mn('SUBTRACT',1011,x),mn('SUBTRACT',y,404),mn('SUBTRACT',664,y)]:
 n=nt.nodes.new('ShaderNodeMapRange');n.interpolation_type='SMOOTHERSTEP';n.clamp=True;n.inputs['From Min'].default_value=0;n.inputs['From Max'].default_value=8;n.inputs['To Min'].default_value=0;n.inputs['To Max'].default_value=1;nt.links.new(dist,n.inputs[0]);window_inside=mn('MULTIPLY',window_inside,n.outputs[0])
mask=mn('MULTIPLY',mask,mn('SUBTRACT',1,window_inside))
"""
base=base.replace('candidate_size=list(im.size)',protection+'\ncandidate_size=list(im.size)')
base=base.replace('CANDIDATE INTERIOR /6SOURCE PIXEL FEATHER','CONTINUOUS PAINT /24SOURCE PX JOIN /ORIGINAL WINDOW PROTECTED')
base=base.replace('WTSC_REGISTERED_FACADE_CANDIDATE_v053_TEST','WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v056_TEST')
base=base.replace('WTSC_Candidate_v053_','WTSC_ContinuousFacade_v056_').replace('REGISTERED_CANDIDATE_TECHNICAL_v053.json','CONTINUOUS_FACADE_TECHNICAL_v056.json')
base=base.replace("'patch_source_box':[1004,475,1088,638]","'patch_source_box':[824,324,1448,740]").replace("'feather_source_pixels':6","'feather_source_pixels':24")
base=base.replace('Unapproved facade material test only,using Library candidatev0. Registered source box1004..1088x475..638;6px feather. Existing v049i palette,characters,window/door geometry,camera and timing preserved.','Continuous painterly candidate detail normalized to original broad colour and lighting;original silhouette and broken window retained;24source-pixel external join;no production adoption.')
exec(compile(base,'v056 verified world harness','exec'))
p=O/'CONTINUOUS_FACADE_TECHNICAL_v056.json';q=json.loads(p.read_text());q.pop('candidate_library_id',None);q.pop('candidate_version',None)
q.update({'source_candidate_library_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','source_candidate_file_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','source_candidate_version':0,'source_candidate_native_dimensions':[1536,1024],'source_candidate_sha256':hashlib.sha256(CAND.read_bytes()).hexdigest(),'derived_image_has_no_original_library_identity':True,'recipe':str(RECIPE),'method':'Candidate RGB times spatial perRGB original/candidate lowpass ratio;8source-pixel bandwidth;24source-pixel outer join;original silhouette alpha and broken-window area preserved.','original_silhouette_alpha_replaced':False,'original_sharpened':False,'new_procedural_grain':False,'status':'VISUAL ACCEPTANCE PENDING; isolated continuous painterly facade test'})
p.write_text(json.dumps(q,indent=2));print('CONTINUOUS_FACADE_THREE_FRAME_TEST_READY',flush=True)
