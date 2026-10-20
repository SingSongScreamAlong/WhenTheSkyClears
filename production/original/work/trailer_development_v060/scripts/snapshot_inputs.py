from pathlib import Path
import hashlib,shutil,json,datetime
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/trailer_development_v060'
sources={'WORLD_v058':R/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend','STEADY_PAIR_v047':R/'locomotion/steady_walk_baseline_v047/native/WTSC_Steady_Ordinary_Walk_v047.blend'}
expected={'WORLD_v058':'13c2aee075315131eac6f85d9d726b766051a84edffa961f4ec38ecf7029a890','STEADY_PAIR_v047':'29a4d9f794187602af43f7349f2b01c1019f39cba9f1d1278b966b78d1770103'}
rows=[]
for name,S in sources.items():
 D=O/'reference'/('PRESERVED_'+name+'.blend');assert not D.exists(),D
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 before=h(S);assert before==expected[name],(name,before)
 st=S.stat();shutil.copy2(S,D);assert h(D)==h(S)==before
 rows.append({'name':name,'source':str(S),'copy':str(D),'sha256':before,'source_modified_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat()})
(O/'evidence/INPUT_SNAPSHOTS.json').write_text(json.dumps({'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':rows},indent=2))
print(json.dumps(rows),flush=True)
