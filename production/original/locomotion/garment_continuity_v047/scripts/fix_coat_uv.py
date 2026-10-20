"""Continuous upper-coat paint registration; no image or geometry edits."""
import bpy,math,numpy as np
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def apply(scene):
 ob=scene.objects['V046 BOY | tailored coat'];me=ob.data;assert len(me.vertices)==65*17
 layer=me.uv_layers['V046 | original pigment registration']
 image=next(n.image for m in me.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE')
 W,H=image.size;pixels=np.empty(W*H*4,dtype=np.float32);image.pixels.foreach_get(pixels);alpha=pixels.reshape(H,W,4)[::-1,:,3]
 before={lp.vertex_index:tuple(layer.data[lp.index].uv) for lp in me.loops}
 mapping={}
 for row in range(32):
  t=row/64.;py=20+555*t+95*(1-smooth(t/.5));a=alpha[int(round(py))];good=np.flatnonzero(a[520:840]>.75)+520;assert len(good)
  k=int(good[np.argmin(abs(good-740))]);lo=k;hi=k
  while lo>520 and a[lo-1]>.75:lo-=1
  while hi<839 and a[hi+1]>.75:hi+=1
  lo+=.6;hi-=.6
  # Keep the source's open armhole beneath the separate painted sleeve:
  # sample solid shoulder fabric instead of printing a second dark hole.
  avoid=1-smooth((py-245)/55)
  assert hi>lo+10
  for col in range(17):
   u=lo+(hi-lo)*col/16
   if u<=670:safe=670+.2*(u-lo)
   elif u<740:safe=u+.2*(670-lo)*(740-u)/70
   else:safe=u
   u=u+(safe-u)*avoid
   mapping[row*17+col]=(u/W,1-py/H)
 for lp in me.loops:
  if lp.vertex_index in mapping:layer.data[lp.index].uv=mapping[lp.vertex_index]
 after={lp.vertex_index:tuple(layer.data[lp.index].uv) for lp in me.loops}
 assert all(after[k]==v for k,v in before.items() if k//17>=32)
 def jumps(d):
  return [abs((d[(r+1)*17+8][1]-d[r*17+8][1])*H) for r in range(31)]
 return {'object':ob.name,'scope':'Upper32rows UV registration only. Original mesh, images, lower33rows and lower costume painting unchanged. No new raster painting.',
  'original_max_adjacent_upper_row_source_y_jump_px':max(jumps(before)),
  'new_max_adjacent_upper_row_source_y_jump_px':max(jumps(after)),
  'source_y_mapping':'20+555t+95*(1-smoothstep(t/0.5)), until t=0.5; original mapping below',
  'source_armhole_exclusion':'Gradual solid cloth sampling above source row300; no copied gap or duplicated collar.',
  'lower_rows_uv_exact':True,'original_image_pixels_edited':False}
