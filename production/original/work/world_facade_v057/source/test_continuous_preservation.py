import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\facade_continuous_v057')
CAND=O.parent/'facade_continuous_v056/WTSC_Continuous_Facade_Painterly_Candidate.png'
RECIPE=O.parent/'facade_continuous_v056/WTSC_Continuous_Facade_Lighting_Recipe_v056.blend'
base=(O.parent/'facade_candidate_v053/test_registered_candidate.py').read_text()
base=base.replace('task\\facade_candidate_v053','task\\facade_continuous_v057')
base=base.replace("IMAGE=O/'WTSC_Facade_Reference_Painted_Candidate.png'","IMAGE=O/'WTSC_Continuous_Facade_Source_Lighting_v057.exr'")
base=base.replace('WTSC_Registered_Facade_Candidate_TEST_v053.blend','WTSC_Continuous_Facade_Source_Lighting_TEST_v057.blend')
base=base.replace('v053 | candidate registered to original plaster patch | TEST ONLY','v057 | continuous painterly facade source lighting | TEST ONLY')
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
base=base.replace('WTSC_REGISTERED_FACADE_CANDIDATE_v053_TEST','WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST')
base=base.replace('WTSC_Candidate_v053_','WTSC_ContinuousFacade_v057_').replace('REGISTERED_CANDIDATE_TECHNICAL_v053.json','CONTINUOUS_FACADE_TECHNICAL_v057.json')
base=base.replace("'patch_source_box':[1004,475,1088,638]","'patch_source_box':[824,324,1448,740]").replace("'feather_source_pixels':6","'feather_source_pixels':24")
base=base.replace('Unapproved facade material test only,using Library candidatev0. Registered source box1004..1088x475..638;6px feather. Existing v049i palette,characters,window/door geometry,camera and timing preserved.','Continuous painterly candidate detail normalized to original broad colour and lighting;original silhouette and broken window retained;24source-pixel external join;no production adoption.')
base=base.replace("IMAGE=O/'WTSC_Continuous_Facade_Source_Lighting_v057.exr'","IMAGE=Path(r'WTSC_LOCAL_USER\\Documents\\Codex\\2026-10-16\\task\\facade_continuous_v056\\WTSC_Continuous_Facade_Source_Lighting_v056.exr')")
base=base.replace('candidate_size=list(im.size)',"\n# Original impact-pit cores, complete rims and soft outskirts remain exact source.\npit_regions=[(1005.2317,402.5976,7.),(1021.125,450.75,6.),(1047.5,446.,6.),(1084.9386,465.2193,8.),(1044.0833,497.9167,6.)]\nfor cx,cy,radius in pit_regions:\n dx=mn('SUBTRACT',x,cx);dy=mn('SUBTRACT',y,cy);distance=mn('SQRT',mn('ADD',mn('MULTIPLY',dx,dx),mn('MULTIPLY',dy,dy)),0)\n n=nt.nodes.new('ShaderNodeMapRange');n.name='PRESERVE ORIGINAL IMPACT PIT';n.interpolation_type='SMOOTHERSTEP';n.clamp=True;n.inputs['From Min'].default_value=radius;n.inputs['From Max'].default_value=radius+4;n.inputs['To Min'].default_value=0;n.inputs['To Max'].default_value=1;nt.links.new(distance,n.inputs[0]);mask=mn('MULTIPLY',mask,n.outputs[0])\n# Keep existing lower vegetation/rubble placement and material treatment.\nfor xa,ya,xb,yb in [(824,618,1120,740),(1320,580,1448,740)]:\n region=1.\n for dist in [mn('SUBTRACT',x,xa),mn('SUBTRACT',xb,x),mn('SUBTRACT',y,ya),mn('SUBTRACT',yb,y)]:\n  n=nt.nodes.new('ShaderNodeMapRange');n.interpolation_type='SMOOTHERSTEP';n.clamp=True;n.inputs['From Min'].default_value=0;n.inputs['From Max'].default_value=16;n.inputs['To Min'].default_value=0;n.inputs['To Max'].default_value=1;nt.links.new(dist,n.inputs[0]);region=mn('MULTIPLY',region,n.outputs[0])\n mask=mn('MULTIPLY',mask,mn('SUBTRACT',1,region))\n"+'\ncandidate_size=list(im.size)')
exec(compile(base,'v057 verified world harness','exec'))
p=O/'CONTINUOUS_FACADE_TECHNICAL_v057.json';q=json.loads(p.read_text());q.pop('candidate_library_id',None);q.pop('candidate_version',None)
q.update({'pit_regions_source_space':[(1005.2317,402.5976,7.),(1021.125,450.75,6.),(1047.5,446.,6.),(1084.9386,465.2193,8.),(1044.0833,497.9167,6.)],'pit_full_source_retention_radius_pixels':[7,6,6,8,6],'pit_feather_source_pixels':4,'lower_vegetation_preservation_rectangles':[(824,618,1120,740),(1320,580,1448,740)],'source_candidate_library_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','source_candidate_file_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','source_candidate_version':0,'source_candidate_native_dimensions':[1536,1024],'source_candidate_sha256':hashlib.sha256(CAND.read_bytes()).hexdigest(),'derived_image_has_no_original_library_identity':True,'recipe':str(RECIPE),'method':'Candidate RGB times spatial perRGB original/candidate lowpass ratio;8source-pixel bandwidth;24source-pixel outer join;original silhouette alpha, broken-window area, original impact pits and lower foliage/rubble retained.','original_silhouette_alpha_replaced':False,'original_sharpened':False,'new_procedural_grain':False,'status':'VISUAL ACCEPTANCE PENDING; isolated continuous painterly facade test'})
p.write_text(json.dumps(q,indent=2));print('CONTINUOUS_FACADE_THREE_FRAME_TEST_READY',flush=True)
