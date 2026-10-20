from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
validation=json.loads((P/'evidence/final_validation.json').read_text());build=json.loads((P/'evidence/build_coherent.json').read_text());library=[]
for receipt in (P/'evidence').glob('library_*_receipt.json'):
    for row in json.loads(receipt.read_text())['results']:
        assert row['status']=='succeeded';library.append({key:row[key] for key in ['file_name','library_file_id','file_id','file_size_bytes','status']})
native=P/'native/WTSC_Coherent_Append_v008b.blend'
criteria={
 'sharp_muted_impulse':'Actualframes1824–1829 show a compact hot ground impulse followed immediately by rapid unequal mass expansion and separated chunks. No audio or camera shake is present.',
 'continuous_changing_silhouette':'Left/right/core retain the same vertex IDs through133absolute native keys. Perimeter shape, position and internal pigment coordinates evolve; there are no generated-pose replacements/crossfades. The painted stage has the identical geometry hash.',
 'weight':'The main left mass reaches its apex around age12–18 then descends while keeping density and spreads along the ground. Fresh Append evaluation measured its local top2.24374 atage12,2.11742 atage24,1.54080 atage44 and0.87265 atage113. It does not keep rising as a chimney.',
 'ground_and_persistence':'Connected low dust spreads and settles. Eight independently tumbling chunks follow separate ascent/apex/descent and remain at contact; four landing puffs accompany several landings. Actualframe2064 verifies the shallow gouge and landed debris after the smoke is gone.',
 'children':'Nine sampled actual full-resolution frames preserve all7334opaque child-mask pixels exactly, with maximum channel difference0; full-shot visual checks retain the faces/figures in front.'}
report={
 'status':'Completed one continuous native blast proof v008b, silhouette validation followed by existing paint on unchanged motion. Ready for user review; no artistic acceptance or production integration claimed.',
 'scope':'One blast only. No variants, tracer expansion, full trailer edits, new image generation, simulation cache, software installation, public publishing or shared UI control.',
 'native':{'append':str(native),'bytes':native.stat().st_size,'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'collection':'FXv008 | ONE COHERENT NATIVE BLAST','root':'FXv008 | fixed world impact and controls','objects':22,'packed_images':2,'geometry_sha256':build['geometry_sha256'],'painted_proof':str(P/'native/WTSC_Coherent_Painted_v008b.blend'),'silhouette_proof':str(P/'native/WTSC_Coherent_Silhouette_Clean_v008.blend'),'fresh_append_sandbox':str(P/'native/WTSC_Coherent_Append_Test_v008b.blend')},
 'media':[validation['painted_media'],validation['silhouette_media']],
 'criteria_review':criteria,
 'review_method':'Inspected actual full-shot native frames, dense chronological frames, decodedMP4 audit frames, and the post-smoke frame2064. Full MP4 decoding confirmed. An independent real-time player session was not verified; do not claim to have watched the inaccessible linked video.',
 'remaining_visible_limits':['Some outer contour scallops remain stylized.','Pigment can stretch on the low dust/front and during strong deformation; the brief flash is angular when paused.','The crater is shallow at this camera and some left-side landings are hidden by the existing foreground.','Held-camera proof only: final moving-camera live occlusion, receiver lighting and character/environment integration remain production work.'],
 'controls':{'fps':24,'frames':[1818,1937],'start_frame':1824,'world_anchor':build['root'],'orientation':'Xhorizontal,+Zup,camera looks+Y; metric scale_length1','properties':['start_frame','speed','size','intensity','painted'],'python_control_update':'Call root.update_tag(refresh={OBJECT}) and update the view layer/depsgraph after changing custom properties; verified by retime/scale test.'},
 'verified':{'all240_native_phase_PNGs_decoded':True,'both120frame_videos_fully_decoded':True,'videos_under20MB':True,'source_hashes_unchanged':validation['protected_sources_unchanged'],'same_silhouette_and_painted_vertex_geometry':True,'fresh_append_packed_dependencies_and_controls':True,'invalid_drivers':[],'outside_driver_targets':[],'after_smoke_ground_frame':2064,'zip_crc_passed':True},
 'resource_use':{'threads':2,'silhouette_motion_seconds':json.loads((P/'evidence/render_silhouette_motion.json').read_text())['seconds'],'painted_motion_seconds':json.loads((P/'evidence/render_painted_final_motion.json').read_text())['seconds'],'render_resolution':[1920,1080],'new_simulation_bake':False,'effects_Blender_processes_left_running':0},
 'library':library,'package':json.loads((P/'evidence/package_validation.json').read_text()),'guide':str(P/'IMPORT_AND_REVIEW.txt'),
 'delivery_notes':'Fresh current Library helpers were fetched. Prepared helper reported prepare_uploads unavailable before any reservation; ordered direct creates then succeeded for all5files. Local version-xattr writeback remains unsupported by the supplied helper on Windows; receipts and logs are preserved.',
 'blockers':[]}
(P/'evidence/HANDOFF_v008b.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'native':report['native'],'library':library,'limits':report['remaining_visible_limits']},indent=2))
