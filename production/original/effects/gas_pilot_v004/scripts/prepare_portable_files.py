"""Stage cache hardlinks, avoiding a second allocated simulation cache."""
import os,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1]
stage=P/'delivery';(stage/'native').mkdir(parents=True,exist_ok=True)
roots=[(P/'cache/proof_48r_120f',stage/'cache/proof_48r_120f')]
roots += [(p,stage/'native'/p.name) for p in (P/'native').glob('blendcache_WTSC_Gas_Particles_Proof_48r_120f_v004') if p.is_dir()]
count=0;logical=0
for source,target in roots:
    for original in source.rglob('*'):
        if not original.is_file():continue
        dest=target/original.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():os.link(original,dest)
        count+=1;logical+=original.stat().st_size
(P/'evidence/portable_staging.json').write_text(json.dumps({'cache_files_hardlinked':count,'logical_bytes':logical,'method':'NTFS hardlinks, no duplicate allocated gas cache data. The ZIP will contain ordinary file bytes.','path':str(stage)},indent=2))
print('STAGING_READY',count,logical)
