"""Bake CC0 prop-node transforms into one glTF mesh, keeping every primitive/material.

The publisher downloads remain untouched. This geometry bridge uses installed NumPy;
it does not alter texture pixels, retopologize, or claim a native Unreal import.
"""
from pathlib import Path
import copy, hashlib, json, shutil, urllib.parse
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DTYPES={5120:np.dtype('i1'),5121:np.dtype('u1'),5122:np.dtype('<i2'),5123:np.dtype('<u2'),5125:np.dtype('<u4'),5126:np.dtype('<f4')}
COUNTS={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
receipts=[]

def bake(src):
    g=json.loads(src.read_text());assert not g.get('animations'), 'Animated props require an explicit pose selection'
    data=[(src.parent/urllib.parse.unquote(b['uri'])).read_bytes() for b in g['buffers']]
    def read(idx):
        a=g['accessors'][idx];assert 'sparse' not in a
        v=g['bufferViews'][a['bufferView']];dt=DTYPES[a['componentType']];n=COUNTS[a['type']]
        stride=v.get('byteStride',dt.itemsize*n);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
        return np.ndarray((a['count'],n),dtype=dt,buffer=data[v['buffer']],offset=offset,strides=(stride,dt.itemsize)).copy()
    def local(node):
        if 'matrix' in node:return np.array(node['matrix'],dtype=np.float64).reshape((4,4),order='F')
        x,y,z,w=node.get('rotation',[0,0,0,1]);M=np.eye(4)
        M[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(node.get('scale',[1,1,1]))
        M[:3,3]=node.get('translation',[0,0,0]);return M
    globals_by_node={}
    def find_globals(index,parent):
        M=parent@local(g['nodes'][index]);globals_by_node[index]=M
        for child in g['nodes'][index].get('children',[]):find_globals(child,M)
    for index in g['scenes'][g.get('scene',0)]['nodes']:find_globals(index,np.eye(4))
    out=copy.deepcopy(g)
    for k in ('meshes','nodes','scenes','buffers','bufferViews','accessors','animations','skins','cameras'):out.pop(k,None)
    out['bufferViews']=[];out['accessors']=[];blob=bytearray();primitives=[];bounds=[];parts=0
    def append(array,typ,component):
        while len(blob)%4:blob.append(0)
        array=np.asarray(array,dtype=DTYPES[component]);raw=array.tobytes();offset=len(blob);blob.extend(raw)
        vi=len(out['bufferViews']);out['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw)})
        a={'bufferView':vi,'componentType':component,'count':len(array),'type':typ}
        if typ=='VEC3' and component==5126:a.update(min=array.min(axis=0).astype(float).tolist(),max=array.max(axis=0).astype(float).tolist())
        i=len(out['accessors']);out['accessors'].append(a);return i
    def visit(index,parent):
        nonlocal parts
        node=g['nodes'][index];M=parent@local(node)
        if 'mesh' in node:
            parts+=1
            for source_primitive in g['meshes'][node['mesh']]['primitives']:
                assert source_primitive.get('mode',4)==4 and not source_primitive.get('targets')
                p={k:copy.deepcopy(v) for k,v in source_primitive.items() if k not in ('attributes','indices')};p['attributes']={}
                transforms=None
                if 'skin' in node:
                    skin=g['skins'][node['skin']]
                    inverse=read(skin['inverseBindMatrices']).reshape((-1,4,4)).transpose(0,2,1) if 'inverseBindMatrices' in skin else np.repeat(np.eye(4)[None,:,:],len(skin['joints']),axis=0)
                    matrices=np.array([globals_by_node[j]@inverse[k] for k,j in enumerate(skin['joints'])])
                    joints=read(source_primitive['attributes']['JOINTS_0']).astype(int)
                    weight_index=source_primitive['attributes']['WEIGHTS_0'];weights=read(weight_index).astype(float)
                    if g['accessors'][weight_index].get('normalized'):weights/=np.iinfo(DTYPES[g['accessors'][weight_index]['componentType']]).max
                    assert np.allclose(weights.sum(axis=1),1,atol=1e-4)
                    transforms=np.einsum('vk,vkij->vij',weights,matrices[joints])
                for key,idx in source_primitive['attributes'].items():
                    if key.startswith(('JOINTS_','WEIGHTS_')):continue
                    a=g['accessors'][idx];array=read(idx);component=a['componentType']
                    if key=='POSITION':
                        homogeneous=np.c_[array,np.ones(len(array))]
                        array=(np.einsum('vij,vj->vi',transforms,homogeneous) if transforms is not None else homogeneous@M.T)[:,:3];component=5126;bounds.append(array)
                    elif key=='NORMAL':
                        array=np.einsum('vij,vj->vi',np.linalg.inv(transforms[:,:3,:3]).transpose(0,2,1),array) if transforms is not None else array@np.linalg.inv(M[:3,:3])
                        array/=np.maximum(np.linalg.norm(array,axis=1,keepdims=True),1e-12);component=5126
                    elif key=='TANGENT':
                        tangent=np.einsum('vij,vj->vi',transforms[:,:3,:3],array[:,:3]) if transforms is not None else array[:,:3]@M[:3,:3].T
                        tangent/=np.maximum(np.linalg.norm(tangent,axis=1,keepdims=True),1e-12)
                        signs=np.sign(np.linalg.det(transforms[:,:3,:3])) if transforms is not None else np.sign(np.linalg.det(M[:3,:3]))
                        array=np.c_[tangent,array[:,3]*signs];component=5126
                    p['attributes'][key]=append(array,a['type'],component)
                    if a.get('normalized') and component!=5126:out['accessors'][-1]['normalized']=True
                indices=read(source_primitive['indices']).reshape(-1) if 'indices' in source_primitive else np.arange(len(read(source_primitive['attributes']['POSITION'])))
                det=np.linalg.det(transforms[:,:3,:3]) if transforms is not None else np.array([np.linalg.det(M[:3,:3])])
                assert np.all(det>0) or np.all(det<0), 'Mixed skin reflection needs per-triangle treatment'
                if np.all(det<0):indices=indices.reshape(-1,3)[:,[0,2,1]].reshape(-1)
                p['indices']=append(indices.reshape(-1,1),'SCALAR',5125);primitives.append(p)
        for child in node.get('children',[]):visit(child,M)
    for index in g['scenes'][g.get('scene',0)]['nodes']:visit(index,np.eye(4))
    name=src.parent.name;dest=ROOT/'SourceAssets'/'DerivedStaticModels'/name;dest.mkdir(parents=True,exist_ok=True)
    binary=name+'_static.bin';out.update(asset={'version':'2.0','generator':'WTSC static-transform bake; publisher originals preserved'},buffers=[{'uri':binary,'byteLength':len(blob)}],meshes=[{'name':name,'primitives':primitives}],nodes=[{'name':name,'mesh':0}],scenes=[{'nodes':[0]}],scene=0)
    for image in out.get('images',[]):
        if 'uri' in image:
            relative=Path(urllib.parse.unquote(image['uri']));assert not relative.is_absolute() and '..' not in relative.parts
            target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src.parent/relative,target)
    (dest/binary).write_bytes(blob);target=dest/(name+'_static.gltf');target.write_text(json.dumps(out,indent=2),encoding='utf8')
    b=np.concatenate(bounds)
    record={'id':name,'source_gltf':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'derived_gltf':str(target.relative_to(ROOT)),'derived_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_meshes':len(g['meshes']),'source_mesh_nodes_baked':parts,'preserved_primitives':len(primitives),'derived_meshes':1,'skins_baked_in_default_pose':len(g.get('skins',[])),'bounds_m_min':b.min(axis=0).tolist(),'bounds_m_max':b.max(axis=0).tolist(),'float32_position_max_error_m':float(np.max(np.abs(b-b.astype(np.float32)))),'texture_pixels_unchanged':True,'native_unreal_imported':False}
    receipts.append(record)
    print(name,'baked parts',parts,'preserved primitives',len(primitives))

for src in sorted((ROOT/'SourceAssets/PolyHaven').glob('*/*.gltf')):bake(src)
(ROOT/'Evidence/StaticGeometryBake.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
