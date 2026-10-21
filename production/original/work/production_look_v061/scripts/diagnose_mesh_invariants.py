"""Single read-only diagnostic of serialized source and current actor mesh invariants.
Opens only the v061 target; never renders or saves any native.
"""
import sys
sys.dont_write_bytecode=True
import bpy,json,hashlib,importlib.util,traceback
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
TARGET=P/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'
REFERENCE=P/'reference/PRESERVED_v060.blend'
SIDECAR=REFERENCE.with_suffix('.invariants.json')
REPORT=P/'evidence/MESH_INVARIANT_DIAGNOSIS.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.loads(json.dumps(v,sort_keys=True,allow_nan=False))
def typedifferences(a,b):
    total=0;samples=[]
    def walk(a,b,path):
        nonlocal total
        if type(a)!=type(b):
            total+=1
            if len(samples)<8:samples.append({'path':path,'source_type':type(a).__name__,'actual_type':type(b).__name__})
        if isinstance(a,dict) and isinstance(b,dict):
            for k in sorted(set(a)&set(b)):walk(a[k],b[k],path+'.'+str(k))
        elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'['+str(i)+']')
    walk(a,b,'')
    return {'count':total,'samples':samples}
before={str(p):sha(p) for p in (TARGET,REFERENCE,SIDECAR)}
report={'target':str(TARGET),'reference':str(REFERENCE),'sidecar':str(SIDECAR),'hashes_before':before,
    'native_opened':str(TARGET),'native_save_or_render':False}
try:
    source=json.loads(SIDECAR.read_text())
    assert before[str(REFERENCE)]==source['reference_sha256']
    spec=importlib.util.spec_from_file_location('flat_validator_diagnostic',P/'scripts/validate_flat_stage_v061.py')
    V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
    bpy.ops.wm.open_mainfile(filepath=str(TARGET),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=scene
    V._frame(scene,source.get('snapshot_frame',937))
    rows={};fields=Counter();realfields=Counter();attribute_names=Counter()
    for name,expected in source['meshes'].items():
        ob=scene.objects.get(name)
        if ob is None:
            rows[name]={'missing':True};continue
        actual=V._mesh(ob);changes={}
        for key in sorted(set(expected)|set(actual)):
            a=expected.get(key);b=actual.get(key)
            if a!=b:
                same=canonical(a)==canonical(b)
                changes[key]={'python_equal':False,'canonical_json_equal':same,
                    'type_differences':typedifferences(a,b)}
                fields[key]+=1
                if not same:realfields[key]+=1
                if key not in ('attributes','shapes'):changes[key].update({'source':a,'actual':b})
        ea=expected.get('attributes',{});aa=actual.get('attributes',{})
        attrs={}
        for an in sorted(set(ea)|set(aa)):
            if ea.get(an)!=aa.get(an):
                attrs[an]={'source':ea.get(an),'actual':aa.get(an),
                    'changed_keys':[k for k in sorted(set(ea.get(an,{}) or {})|set(aa.get(an,{}) or {}))
                        if (ea.get(an,{}) or {}).get(k)!=(aa.get(an,{}) or {}).get(k)]}
                attribute_names[an]+=1
        rows[name]={'missing':False,'python_equal':expected==actual,
            'canonical_json_equal':canonical(expected)==canonical(actual),
            'field_differences':changes,'attribute_differences':attrs}
    report.update({'scene':scene.name,'snapshot_frame':source.get('snapshot_frame',937),
        'mesh_count':len(rows),'python_equal_count':sum(r.get('python_equal',False) for r in rows.values()),
        'canonical_json_equal_count':sum(r.get('canonical_json_equal',False) for r in rows.values()),
        'field_difference_mesh_counts':dict(fields),'canonical_value_difference_mesh_counts':dict(realfields),
        'attribute_difference_mesh_counts':dict(attribute_names),'meshes':rows})
except Exception:
    report['exception']=traceback.format_exc()
finally:
    report['hashes_after']={str(p):sha(p) for p in (TARGET,REFERENCE,SIDECAR)}
    report['all_input_files_unchanged']=report['hashes_after']==before
    REPORT.write_text(json.dumps(report,indent=2))
    print('V061_MESH_INVARIANT_DIAGNOSIS',json.dumps({k:report.get(k) for k in
        ['mesh_count','python_equal_count','canonical_json_equal_count','field_difference_mesh_counts',
         'canonical_value_difference_mesh_counts','attribute_difference_mesh_counts','all_input_files_unchanged','exception']}),flush=True)
