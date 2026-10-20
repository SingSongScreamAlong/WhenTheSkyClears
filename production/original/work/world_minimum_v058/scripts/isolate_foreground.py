exec((__import__('pathlib').Path(__file__).parent/'audit_world.py').read_text().split('rows=[]')[0])
s.frame_set(1537)
bank=s.objects['v020 | Foreground bank | continuous blended paint'];path=s.objects['v020 | Walking path | continuous blended paint']
for label,ob in [('bank_hidden',bank),('path_hidden',path)]:
 old=ob.hide_render;ob.hide_render=True;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True,scene=s.name);ob.hide_render=old
print('ISOLATION_READY')
