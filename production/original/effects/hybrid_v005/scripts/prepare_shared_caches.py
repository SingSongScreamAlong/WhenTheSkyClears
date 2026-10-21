import os,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
original=P.parent/'gas_pilot_v004'
pairs=[(original/'cache/proof_48r_120f',P/'cache/proof_48r_120f'),
       (original/'native/blendcache_WTSC_Gas_Particles_Proof_48r_120f_v004',P/'native/blendcache_WTSC_Hybrid_Proof_v005')]
files=0;logical_bytes=0
for source,target in pairs:
    for file in source.rglob('*'):
        if not file.is_file():continue
        dest=target/file.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():os.link(file,dest)
        files+=1;logical_bytes+=file.stat().st_size
(P/'evidence/cache_reuse.json').write_text(json.dumps({'files':files,'logical_bytes':logical_bytes,'new_bake':False,'resolution_change':False,'new_allocated_cache_data_bytes':0,'method':'NTFS hardlinks to existing v004 caches; read-only use. No source data altered.'},indent=2))
print('SHARED_CACHES_READY',files,logical_bytes)
