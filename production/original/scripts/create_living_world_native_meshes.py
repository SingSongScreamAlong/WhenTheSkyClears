import subprocess,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cli=r'WTSC_LOCAL_USER\AppData\Local\dcc-mcp\bin\dcc-mcp-cli.exe'
recipe=json.loads((root/'work/living_world_meshes/v008/assembly.json').read_text())
receipts=root/'notes/living_world/typed_mesh_creation_v008.jsonl'
assert not receipts.exists(),'Inspect existing receipts and native state before any replay'
for i,entry in enumerate(recipe['entries']):
    p=subprocess.run([cli,'call','blender.dda6f921.blender_data_geometry__create_mesh_from_data',
        '--json-file',entry['payload'],'--gateway','local','--transport','mcp','--output','json'],capture_output=True,text=True)
    try:r=json.loads(p.stdout)
    except Exception:raise RuntimeError((entry['name'],p.returncode,p.stdout[-1000:],p.stderr[-1000:]))
    native=r.get('result',{}).get('structuredContent',{})
    with receipts.open('a',encoding='utf-8') as f:f.write(json.dumps({'index':i,'name':entry['name'],'request_id':r.get('request_id'),'returncode':p.returncode,'response':native})+'\n')
    assert p.returncode==0 and r.get('success') and native.get('success'),(entry['name'],r)
    if i%6==0 or i==len(recipe['entries'])-1:print(json.dumps({'native_meshes_created':i+1,'total':len(recipe['entries']),'name':entry['name']}),flush=True)
print('All original mesh groups created by the typed native Blender data geometry tool',flush=True)
