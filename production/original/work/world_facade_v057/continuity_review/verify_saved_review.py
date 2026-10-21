from pathlib import Path
import hashlib,json
import win_ea_compat as ea
O=Path(__file__).parent;P=O/'WTSC_v057_ENVIRONMENT_Continuity_24fps_1201-1249.mp4'
identity=ea.getxattr(P,'user.library-file-id').decode();version=ea.getxattr(P,'user.library-file-version').decode()
assert identity=='[PRIVATE_LIBRARY_REFERENCE_REMOVED]' and version=='0'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='401c7d40500787bebd871cbe045498be9b48a04d5377ec07703a2734a21fabb4'
q={'path':str(P),'library_file_id':identity,'version':0,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'fresh_process_native_metadata_verified':True}
if (O/'evidence').exists():dest=O/'evidence/SAVED_REVIEW_IDENTITY.json'
else:dest=O/'SAVED_REVIEW_IDENTITY.json'
dest.write_text(json.dumps(q,indent=2));print(json.dumps(q))
