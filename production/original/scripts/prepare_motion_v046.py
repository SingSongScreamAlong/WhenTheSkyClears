"""Verify parent-sealed v007 and copy it into this integration's own imports."""
import hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];parent=json.loads((R/'notes/world_v016/art_checkpoint_v045c.json').read_text());native=R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend';expected='77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de';assert hashlib.sha256(native.read_bytes()).hexdigest()==expected
assert not (R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend').exists()
preserved={parent['source']['path']:parent['source']['sha256'],str(native):expected,**parent['preserved_inputs']}
for row in parent['actual_frames_and_comparisons']:preserved[row['native_4K_png']['path']]=row['native_4K_png']['sha256']
for name,sha in preserved.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name
folder=R/'shots/integration/v046/imports';folder.mkdir(parents=True,exist_ok=True);copy=folder/native.name;assert not copy.exists();shutil.copyfile(native,copy);assert hashlib.sha256(copy.read_bytes()).hexdigest()==expected
(R/'renders/world_v016/integration_v046').mkdir(parents=True,exist_ok=True)
report={'sealed_source':str(native),'source_sha256':expected,'snapshot':str(copy),'snapshot_sha256':expected,'collection':'WTSC_BATTLEFIELD_DRAWN_PAIR_v007','baseline':parent['source'],'preserved_inputs':preserved,'reuse':'Parent-sealed original native motion and existingv045cbackground/EEVEE/light/FX. Existingnativeappend/NLA/materialinterfaces reused; no externalplugin/asset replacement required. Productionreusev1guide alreadyreadandchecked; ownedbackgroundbpy fallback retained, no livegatewayvalidation claimed.','scope':'Boundedmatched120frame1080p baseline/candidate previews, savednative4Ksettings, actualcritical4Kstills. No newFX, foregroundexperiment, fulltrailer/title/FPS/duration changes.'}
(R/'notes/world_v016/motion_snapshot_v046.json').write_text(json.dumps(report,indent=2));print('V046_SEALED_SNAPSHOT_VERIFIED',expected,flush=True)
