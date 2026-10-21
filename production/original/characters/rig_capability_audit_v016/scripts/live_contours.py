"""Native Geometry Nodes link the16 source ribbons to the painted skeleton.
UVs, topology and materials remain the original native drawing surfaces.
No handler, cached frame lookup, generated bitmap or proxy retarget.
The editable per-row widths/curve coefficients live on the source mesh.
"""
import bpy,math
from mathutils import Matrix,Vector
def coefficients(t,leg):
    if not leg:return (1-t,0,t),(-1,0,1)
    if t<.35:return (1-2*t,2*t,0),(-2,2,0)
    if t>.65:return (0,2-2*t,2*t-1),(0,-2,2)
    u=(t-.35)/.30
    return (.3*(1-u)**2,.7+.6*u-.6*u*u,.3*u*u),(-2*(1-u),2-4*u,2*u)
def add_attribute(me,name,values):
    if me.attributes.get(name):me.attributes.remove(me.attributes[name])
    a=me.attributes.new(name,'FLOAT','POINT');a.data.foreach_set('value',values)
def anchor(rig,bone,point,collection,name):
    # Copy the final bone matrix, then retain the exact original drawing point
    # as a rest-space offset. This preserves the painted boot collar entry.
    base=bpy.data.objects.new(name+' | joint',None);collection.objects.link(base)
    c=base.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget=bone
    end=bpy.data.objects.new(name,None);collection.objects.link(end);end.parent=base
    end.matrix_local=Matrix.Translation(rig.data.bones[bone].matrix_local.inverted()@Vector(point))
    base.empty_display_size=.012;end.empty_display_size=.012
    return end
def setup(mesh,rig,collection,source_coords,boot):
    role=mesh['v007_role'];side='near' if mesh.name.endswith('near') else 'far';leg=role=='drawn_leg'
    if leg:
        H=anchor(rig,'thigh_'+side,rig.data.bones['thigh_'+side].head_local,collection,mesh.name+' | H')
        K=anchor(rig,'shin_'+side,rig.data.bones['shin_'+side].head_local,collection,mesh.name+' | K')
        uv=boot.data.uv_layers.active
        ys={lp.vertex_index:(1-uv.data[lp.index].uv.y)*941 for lp in boot.data.loops};top=min(ys.values());ids=[i for i,y in ys.items() if y<top+1.6]
        pts=[boot.data.vertices[i].co for i in ids];U=min(pts,key=lambda v:v.x);V=max(pts,key=lambda v:v.x)
        # Place the final contour slightly inside the unchanged painted boot,
        # because its UV alpha boundary is below the traced top clipping edge.
        inset=Vector((0,0,-.018));U=U+inset;V=V+inset
        A=anchor(rig,'foot_'+side,(U+V)*.5,collection,mesh.name+' | boot collar')
        CU=anchor(rig,'foot_'+side,U,collection,mesh.name+' | collar U');CV=anchor(rig,'foot_'+side,V,collection,mesh.name+' | collar V')
    else:
        sleeve='drawn skin' not in mesh.name
        bn=('upper_arm_' if sleeve else 'forearm_')+side
        H=anchor(rig,bn,rig.data.bones[bn].head_local,collection,mesh.name+' | start')
        A=anchor(rig,bn,rig.data.bones[bn].tail_local,collection,mesh.name+' | end');K=H
    oldmods=list(mesh.modifiers)
    for m in oldmods:mesh.modifiers.remove(m)
    mesh.vertex_groups.clear()
    if mesh.data.shape_keys:mesh.shape_key_clear()
    count=len(source_coords)//2
    ts=[(i//2)/(count-1) for i in range(len(source_coords))]
    if role=='drawn_cuff':ts=[(15+i//2)/18 for i in range(len(source_coords))]
    width=[(source_coords[(i//2)*2+1]-source_coords[(i//2)*2]).length*.5 for i in range(len(source_coords))]
    if role=='drawn_arm' and 'drawn sleeve' in mesh.name:
        # A rounded shoulder attachment, retaining the sampled paint and full
        # source sleeve width below the first10 percent. No extra patch/card.
        width=[v*math.sqrt(max(0,1-(1-min(1,t/.10))**2)) for v,t in zip(width,ts)]
    depth=[p.y for p in source_coords]
    for n,j in [('H',0),('K',1),('A',2)]:
        add_attribute(mesh.data,'V016_'+n,[coefficients(t,leg)[0][j] for t in ts])
        add_attribute(mesh.data,'V016_D'+n,[coefficients(t,leg)[1][j] for t in ts])
    add_attribute(mesh.data,'V016_width',[v*(-1 if i%2==0 else 1) for i,v in enumerate(width)])
    add_attribute(mesh.data,'V016_depth',depth)
    g=bpy.data.node_groups.new('V016 live contour | '+mesh.name,'GeometryNodeTree')
    g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes=g.nodes;links=g.links
    inp=nodes.new('NodeGroupInput');out=nodes.new('NodeGroupOutput')
    def attr(name):
        n=nodes.new('GeometryNodeInputNamedAttribute');n.data_type='FLOAT';n.inputs['Name'].default_value=name;return n.outputs['Attribute']
    def vec(operation,a,b=None):
        n=nodes.new('ShaderNodeVectorMath');n.operation=operation
        links.new(a,n.inputs[0])
        if b is not None:links.new(b,n.inputs[3] if operation=='SCALE' else n.inputs[1])
        return n.outputs['Vector']
    loc=[]
    for ob in [H,K,A]:
        n=nodes.new('GeometryNodeObjectInfo');n.transform_space='RELATIVE';n.inputs['Object'].default_value=ob;loc.append(n.outputs['Location'])
    def combination(prefix):
        xs=[vec('SCALE',location,attr('V016_'+prefix+n)) for n,location in zip(['H','K','A'],loc)]
        return vec('ADD',vec('ADD',xs[0],xs[1]),xs[2])
    center=combination('');tangent=combination('D')
    sep=nodes.new('ShaderNodeSeparateXYZ');links.new(tangent,sep.inputs[0])
    neg=nodes.new('ShaderNodeMath');neg.operation='MULTIPLY';neg.inputs[1].default_value=-1;links.new(sep.outputs['Z'],neg.inputs[0])
    normal=nodes.new('ShaderNodeCombineXYZ');links.new(neg.outputs[0],normal.inputs['X']);links.new(sep.outputs['X'],normal.inputs['Z'])
    off=vec('SCALE',vec('NORMALIZE',normal.outputs[0]),attr('V016_width'))
    position=vec('ADD',center,off)
    # Remove anchor depth before applying the established art layer depth.
    # It is a planar drawing, so joint depth must not duplicate draw offsets.
    ps=nodes.new('ShaderNodeSeparateXYZ');links.new(position,ps.inputs[0]);flatpos=nodes.new('ShaderNodeCombineXYZ');links.new(ps.outputs['X'],flatpos.inputs['X']);links.new(ps.outputs['Z'],flatpos.inputs['Z']);position=flatpos.outputs[0]
    if leg:
        # Last3 rows settle into the exact original boot opening; the source
        # sole and all boot vertices remain untouched.
        add_attribute(mesh.data,'V016_entry',[max(0,min(1,(t-.91)/.09)) for t in ts])
        add_attribute(mesh.data,'V016_edge',[float(i%2) for i in range(len(ts))])
        locuv=[]
        for ob in [CU,CV]:
            nn=nodes.new('GeometryNodeObjectInfo');nn.transform_space='RELATIVE';nn.inputs['Object'].default_value=ob;locuv.append(nn.outputs['Location'])
        endpoint=vec('ADD',locuv[0],vec('SCALE',vec('SUBTRACT',locuv[1],locuv[0]),attr('V016_edge')))
        es=nodes.new('ShaderNodeSeparateXYZ');links.new(endpoint,es.inputs[0]);ef=nodes.new('ShaderNodeCombineXYZ');links.new(es.outputs['X'],ef.inputs['X']);links.new(es.outputs['Z'],ef.inputs['Z'])
        position=vec('ADD',position,vec('SCALE',vec('SUBTRACT',ef.outputs[0],position),attr('V016_entry')))
    depthnode=nodes.new('ShaderNodeCombineXYZ');links.new(attr('V016_depth'),depthnode.inputs['Y']);position=vec('ADD',position,depthnode.outputs[0])
    setpos=nodes.new('GeometryNodeSetPosition');links.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);links.new(position,setpos.inputs['Position']);links.new(setpos.outputs['Geometry'],out.inputs['Geometry'])
    mod=mesh.modifiers.new('V016 live curved painted contour','NODES');mod.node_group=g
    mesh['v016_linkage']='Native Geometry Nodes from final original skeleton joints and boot collar. Editable per-row widths and curve coefficients. No frame clock.'
    mesh['v016_design_limit']='Joint curves are technical corrective construction, requiring visual approval in each supported pose.'
    return {'mesh':mesh.name,'anchors':[H.name,K.name,A.name],'method':'native pose-driven curved contour','vertices':len(source_coords)}
