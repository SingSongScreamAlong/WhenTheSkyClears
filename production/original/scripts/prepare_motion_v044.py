"""Seal the supplied motion into an integration-owned snapshot; never edit inputs."""
import hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
paths={
 'shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend':'afe5f18602023c3c35732ff0132e1bb3c79c1aa1f4e14eb55d14af3216f5fd7f',
 'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend':'c3ed3c15055ae5cd242a68964d6980bb8bda3ff6f7f4882d69fa4198e937819f',
 'renders/world_v016/integration_v043/WTSC_Combined_Open_75_80_4K_v043.mp4':'4078fcf20fc69e40d7512eac6a6391ec79a664f1b264512cd39a8851264abae9',
 'renders/world_v016/WTSC_Full_Knockout_Trailer_4K_v040.mp4':'a8b4edc357498ba3e2ffb585624a862d88ee852f4bb97caca617a14a19ad8569',
 'locomotion/battlefield_corrections_v006/native/WTSC_Battlefield_Drawn_Corrections_v006.blend':'d74339ba11bd0d8d5dcd09f30ea8e1ff42d5b329f706410b0565d145100f8189'}
for name,sha in paths.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
out=R/'shots/world/WTSC_Open_Battlefield_Drawn_Trial_v044.blend';assert not out.exists()
folder=R/'shots/integration/v044/imports';folder.mkdir(parents=True,exist_ok=True)
source=R/list(paths)[-1];snapshot=folder/source.name;assert not snapshot.exists();shutil.copyfile(source,snapshot)
sha=paths[list(paths)[-1]];assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==sha
for name in ['renders/world_v016/integration_v044','notes/world_v016']: (R/name).mkdir(parents=True,exist_ok=True)
receipt={'sealed_source':str(source),'source_sha256':sha,'snapshot':str(snapshot),'snapshot_sha256':sha,'collection':'WTSC_BATTLEFIELD_DRAWN_PAIR_v006','preserved_inputs':paths,'source_written':False,'scope':'Separate120frame matched EEVEE trial only. Existing native world, camera, route, v003FX, lighting and contacts fixed.','reuse':{'contract':'dcc-mcp-production-reuse/v1','guide':'notes/dcc_agent_workflows.md; checked and substantive gate read','existing_reuse':'Supplied original v006 native motion and v043 native world/FX; no new asset/plugin needed. Prior native append, NLA and material interfaces reused.','transport':'dcc-mcp-cli absent on PATH; established owned background bpy fallback. No live gateway validation claimed.','discovery':'Existing project handoff and scripts inspected; prior provider/marketplace investigation in notes/production_reuse_evidence.json remains provenance, not a new provider call. Stock plugins cannot substitute this exact matched original performance.','rights_scope':'Same local original project assets and user-supplied music; no external publication or transfer.'}}
(R/'notes/world_v016/motion_snapshot_v044.json').write_text(json.dumps(receipt,indent=2));print('V044_SNAPSHOT_VERIFIED',sha,flush=True)
