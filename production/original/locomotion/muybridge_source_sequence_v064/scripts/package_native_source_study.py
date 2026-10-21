"""Package editable native files and exact companion sources for handoff."""

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root=Path(__file__).resolve().parents[1]
members=[root / "SOURCE_SEQUENCE_GUIDE_v064.txt"]
members += sorted((root / "native").glob("Muybridge_Phase??_Manual_Trace_v064.blend"))
members += sorted((root / "phase_specs").glob("phase??.json"))
members += sorted((root / "reference").glob("phase??_source_crop.png"))
members += [root / "evidence" / name for name in (
    "SOURCE_CROPS_VERIFIED_v064.json",
    "ALL_12_COLD_REOPEN_v064.json",
    "EDITORIAL_PLAYBACK_DECODE_v064.json",
)]
if len(members)!=40 or any(not p.exists() for p in members):
    raise RuntimeError("Native package does not have guide, 12 blends, 12 point lists, 12 crops and 3 checks")
output=root / "native" / "WTSC_Muybridge_12_Editable_Source_Phases_v064.zip"
with ZipFile(output,"w",compression=ZIP_DEFLATED,compresslevel=6) as archive:
    for path in members:
        archive.write(path,arcname=path.relative_to(root).as_posix())
report={
    "path":str(output),
    "member_count":len(members),
    "members":[p.relative_to(root).as_posix() for p in members],
    "bytes":output.stat().st_size,
    "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
    "contains_production_files":False,
}
(root / "evidence" / "NATIVE_PACKAGE_v064.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="members"}))
