import json, hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
validation=json.loads((P/'evidence/media_validation.json').read_text())
append=json.loads((P/'evidence/append_sandbox.json').read_text())
library=[]
for file in (P/'evidence').glob('library_*_receipt.json'):
    for row in json.loads(file.read_text())['results']:
        assert row['status']=='succeeded'
        library.append({k:row[k] for k in ['file_name','library_file_id','file_id','file_size_bytes','mime_type','status']})
report={
 'task_status':'Completed bounded five-second painted-impulse refinement v006, actual review media, fresh native Append test and private Library delivery.',
 'artistic_status':'Review candidate. User preferred v003 paint over gas; this refines that direction. No artistic acceptance or full production integration claimed.',
 'primary_review':'WTSC_Compare_LEFT-v003_RIGHT-Painted-Impulse-v006.mp4',
 'changes':['All thirteen cold-smoke births compressed to ages0–5, rapid fan-out/upward impulse then deceleration, unequal lobe lifetimes and hanging drift.','Consecutive24fps ignition grows from small glint to larger hot gesture; hot emission/light envelope ends by age10.','FX-only HDR bloom extracted before alpha-over and added outside sprite alpha, with native scene occlusion; background excluded from Glare.','Three separately timed depth/shape/size/contrast variations and six sparse, independently timed tapered tracers.','Rough authored debris rise/apex/fall, three landing puffs, landed chips remain.','Separate persistent ground-gouge/rim collection per blast; no end fade.'],
 'native_assets':{'path':str(P/'native/WTSC_Painted_Blast_Assets_v006.blend'),'bytes':(P/'native/WTSC_Painted_Blast_Assets_v006.blend').stat().st_size,'sha256':validation['native_library_sha256'],'collection':'FXv006 | APPEND ASSETS | painted blasts impacts tracers','node_tree':'FXv006 | HDR FX bloom over | append helper','objects':append['objects'],'packed_images':len(append['packed_images']),'no_cameras_or_lights':True},
 'native_proof':{'path':str(P/'native/WTSC_Painted_Blast_Proof_v006.blend'),'sha256':validation['proof_native_sha256'],'scene':'FX_PROOF_v006 | painted impulse depth tracers and ground','frames':[1800,1919],'fps':24,'pixels':[1920,1080],'renderer':'BLENDER_EEVEE','samples':32,'static_fixture_frame':1825,'fixture_source':'read-only v038 project geometry / v003 matched held shot'},
 'sandbox':str(P/'sandbox/WTSC_Fresh_Append_Sandbox_v006.blend'),
 'guide':str(P/'IMPORT_GUIDE.md'),
 'package':json.loads((P/'evidence/package_validation.json').read_text()),
 'actual_media':validation['outputs'],
 'tests':{'native_factory_append':True,'reversible_retime_and_scale':True,'invalid_drivers':append['invalid_drivers'],'outside_driver_targets':append['outside_driver_targets'],'all_dependencies_packed':True,'persistent_impact_at_frame2300':True,'post_smoke_render_frame2064':True,'all120_actual_new_proof_pngs_decoded':True,'all120_transparent_PNGs_decoded':True,'full_mp4_decodes':True,'transparent_outer_edge_alpha':0,'bloom':validation['bloom_ablation'],'child_mask':validation['child_silhouette_checks'],'protected_source_hashes_unchanged':validation['source_hashes_unchanged']},
 'resources':{'threads':2,'new_bake':False,'gas_used':False,'approx_proof_render_elapsed_seconds_excluding_production_pause':297.484+77.3634551,'transparent_export_seconds':35.965116,'snapshot':json.loads((P/'evidence/resource_sample.json').read_text()),'yield':'Own motion worker stopped after frame1894 when production began. Resumed final25 frames only after production exited. No production process stopped; no UI control. Subsequent frame loops detect and yield to other Blender workers.','running_effects_processes_at_handoff':0},
 'library':library,
 'remaining_limits':['Artistic review against preferred v003 still needed; no final acceptance claimed.','Proof uses a held camera/children/background at1825. Moving-camera live occlusion, production light receivers and character contact are production work.','The set has an opaque battlefield matte atY12. Far blast atY11.5 is in front of it; tracer atY14 is behind it. Deeper ruin threading needs scene layer separation.','2.5D layered painted forms with native motion/erosion, not a fluid simulation; repeated source forms may remain recognizable.','Only MID has a960×540 straight-alpha working sequence; native geometry provides all variants and final-resolution path.','Earlier v001 broad pack remains an unaccepted artistic prototype; gas v004 not preferred, hybrid v005 was built but not rendered/promoted.','Library uploads succeeded. Local Library version xattrs could not be written because the supplied helper calls os.setxattr, unavailable on this Windows Python. Full receipts and attempted metadata logs are preserved.'],
 'blockers':[]
}
(P/'evidence/HANDOFF_v006.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['task_status'],'native':report['native_assets'],'library':library,'remaining_production_work':report['remaining_limits'][:3]},indent=2))
