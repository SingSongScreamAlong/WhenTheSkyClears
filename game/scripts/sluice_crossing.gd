extends Node2D

# A pressure cradle pays out the rope of an actual hinged footbridge. The far
# treadle can engage its ratchet only while a different child holds the cradle.
# Releasing before that simply folds the optional route back above safe ground.
var game
var data={}
var state="folded"
var bridge_body:AnimatableBody2D
var bridge_shape:CollisionShape2D
var lower_amount=0.0
var plate_child=""
var far_child=""
var hinge=Vector2.ZERO
var span=250.0
var bridge_height=14.0
var fold_angle=-1.22
var latched=false
var held_clock=0.0
var has_crossed=[]
var bridge_contact_ticks={}
var atlas=preload("res://assets/props/painted_survival_atlas_v020.png")
var rig_art:Texture2D
var rig_regions={}
var notified=false

func _ready():
	# The timber rig is behind the children; only the low front rail belongs
	# over their feet. A foreground hoist cheek hid the waiting child's hands.
	z_index=0
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	hinge=Vector2(float(data.get("bridge_x",15140)),float(data.get("bridge_y",570)))
	span=float(data.get("bridge_w",250)); bridge_height=float(data.get("bridge_h",14))
	bridge_body=AnimatableBody2D.new(); bridge_body.name="CounterweightBridge"
	bridge_body.collision_layer=1; bridge_body.collision_mask=2
	bridge_body.sync_to_physics=false
	bridge_body.position=hinge
	bridge_shape=CollisionShape2D.new()
	var shape=RectangleShape2D.new(); shape.size=Vector2(span,bridge_height)
	bridge_shape.shape=shape; bridge_shape.position=Vector2(span*.5,bridge_height*.5)
	bridge_body.add_child(bridge_shape); add_child(bridge_body)
	var art_path="res://assets/props/Counterweight_Parts_v042.png"
	if ResourceLoader.exists(art_path):
		rig_art=load(art_path)
		rig_regions={"cradle":Rect2(49,310,582,270),"hoist":Rect2(677,39,546,559),"weight":Rect2(133,692,443,489),"pawl":Rect2(719,697,453,486)}
	reset_from_progress()

func reset_from_progress():
	latched=bool(game.flags.get(str(data.get("key","woods_counterweight_latched")),false))
	lower_amount=1.0 if latched else 0.0
	state="latched" if latched else "folded"
	plate_child=""; far_child=""; held_clock=0; has_crossed=[]; bridge_contact_ticks={}; notified=false
	if is_instance_valid(bridge_body): bridge_body.rotation=0.0 if latched else fold_angle
	queue_redraw()

func on_treadle(child,x,y,width):
	if not is_instance_valid(child) or not child.is_on_floor(): return false
	if absf(child.position.x-x)>width*.5 or absf(child.position.y-y)>5.0: return false
	# The plate reacts to a real upward-facing floor contact, never an airborne
	# child whose drawing happens to pass over its projected rectangle.
	for index in range(child.get_slide_collision_count()):
		if child.get_slide_collision(index).get_normal().y<-.8: return true
	return false

func holder():
	for child in [game.player,game.boy]:
		if on_treadle(child,float(data.get("plate_x",15055)),hinge.y,float(data.get("plate_w",76))): return child
	return null

func work_contacts(child):
	if game==null or game.mode!="playing" or latched: return {}
	if child!=holder(): return {}
	return {"kind":"balance_hold","near":child.position+Vector2(11,-47),"far":child.position+Vector2(18,-52),"look":hinge+Vector2(span,0)}

func event(kind):
	if game.get("encounter_events")!=null:
		game.encounter_events.append({"kind":kind,"id":str(data.get("id","woods_counterweight")),"chapter":game.chapter,"time":game.playtime,"holder":plate_child,"crossing_child":far_child})

func _physics_process(dt):
	if game==null or game.mode!="playing": return
	var child=holder()
	plate_child=str(child.name) if is_instance_valid(child) else ""
	if not latched:
		var before=lower_amount
		lower_amount=move_toward(lower_amount,1.0 if child!=null else 0.0,dt/float(data.get("lower_seconds",1.4) if child!=null else data.get("return_seconds",2.2)))
		held_clock=held_clock+dt if child!=null else 0.0
		if lower_amount>=.999:
			state="held"
			for traveller in [game.player,game.boy]:
				if traveller==child: continue
				if on_treadle(traveller,float(data.get("latch_x",15445)),hinge.y,float(data.get("latch_w",58))):
					latched=true; lower_amount=1; state="latched"; far_child=str(traveller.name)
					game.flags[str(data.get("key","woods_counterweight_latched"))]=true
					game.play_sfx("wheel",-12)
					game.announce_message("The iron tooth catches. The bridge will hold for both of you.",5)
					event("counterweight_latched")
					game.write_save()
					break
		elif lower_amount<=.001: state="folded"
		else: state="lowering" if lower_amount>before else "returning"
		if before<.999 and lower_amount>=.999:
			game.play_sfx("wheel",-19); event("counterweight_held_open")
		if child!=null and not notified:
			notified=true; game.announce_message("A child's weight lowers the span. The far iron tooth can hold it open.",6)
	var ease=lower_amount*lower_amount*(3-2*lower_amount)
	bridge_body.rotation=lerpf(fold_angle,0.0,ease)
	for traveller in [game.player,game.boy]:
		if is_on_bridge(traveller):
			var child_name=str(traveller.name)
			bridge_contact_ticks[child_name]=int(bridge_contact_ticks.get(child_name,0))+1
			if not child_name in has_crossed: has_crossed.append(child_name)
	queue_redraw()

func contact_ticks(child):
	return int(bridge_contact_ticks.get(str(child.name),0))

func is_on_bridge(child):
	if not is_instance_valid(child) or not child.is_on_floor(): return false
	for index in range(child.get_slide_collision_count()):
		if child.get_slide_collision(index).get_collider()==bridge_body and child.get_slide_collision(index).get_normal().y<-.65: return true
	return false

func support_at(x,fallback_y=700.0):
	if lower_amount<.995 or x<hinge.x or x>hinge.x+span: return INF
	return hinge.y if absf(hinge.y-fallback_y)<120 else INF

func ground_at(x):
	return lower_amount>=.995 and x>=hinge.x and x<=hinge.x+span

func objective_text():
	if not is_instance_valid(game.player) or game.player.position.x<hinge.x-420 or game.player.position.x>hinge.x+span+420: return ""
	if latched:
		if game.boy.position.x>hinge.x+span+8 and absf(game.boy.position.y-hinge.y)<25:
			return "You are both across. Search the keeper's medicine, then take the road to the mill."
		if game.boy.following: return "The ratchet holds. Wait on the far landing while he comes across."
		return "The ratchet holds. Call him across [Q], then search the keeper's medicine."
	if plate_child==str(game.boy.name):
		if game.boy.following: return "His weight holds the cradle. Ask him to wait [Q] before you cross."
		if lower_amount<.995: return "He's holding the cradle. Wait for the span to settle."
		return "He's holding the cradle. Cross the lowered span and step onto the far iron tooth."
	if plate_child==str(game.player.name): return "Bring him onto the cradle, then ask him to wait [Q] while you cross."
	if state=="returning": return "The cradle was released. The span is rising; the road below is safe."
	return "The near cradle needs a child's weight. The raised span reaches the keeper's medicine."

func paint_beam(canvas,a,b,thickness,tint=Color(.89,.88,.76)):
	var direction=b-a
	canvas.draw_set_transform(a,direction.angle(),Vector2.ONE)
	canvas.draw_texture_rect_region(atlas,Rect2(0,-thickness*.5,direction.length(),thickness),Rect2(555,296,300,52),tint)
	canvas.draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func paint_prop(canvas,source,rect,tint=Color(.91,.91,.82)):
	canvas.draw_texture_rect_region(atlas,rect,source,tint)

func paint_rig(key,rect,tint=Color(.94,.93,.85)):
	if is_instance_valid(rig_art): draw_texture_rect_region(rig_art,rect,rig_regions[key],tint)

func _draw():
	if data.is_empty(): return
	var floor_y=700.0
	var gantry=hinge+Vector2(-32,-130)
	# Posts and braces use restrained opaque wood grain at a plausible scale.
	for x in [hinge.x-47,hinge.x+span+21]:
		paint_beam(self,Vector2(x,floor_y+8),Vector2(x,hinge.y-46),9)
		paint_beam(self,Vector2(x-21,floor_y),Vector2(x,hinge.y+12),6,Color(.77,.80,.69))
	if is_instance_valid(rig_art):
		paint_rig("hoist",Rect2(hinge+Vector2(-125,-180),Vector2(546,559)*.34))
	else:
		paint_beam(self,hinge+Vector2(-51,0),gantry+Vector2(-15,-13),10)
		paint_beam(self,gantry+Vector2(-32,-10),gantry+Vector2(34,-10),9)
	var weight=hinge+Vector2(-20,35-lower_amount*85)
	draw_line(gantry,weight,Color(.27,.30,.23),2,true)
	var tip=hinge+Vector2(span-13,0).rotated(bridge_body.rotation)
	draw_line(gantry,tip+Vector2(0,-4),Color(.31,.33,.24),1.7,true)
	if is_instance_valid(rig_art):
		paint_rig("weight",Rect2(weight+Vector2(-26,-5.6),Vector2(443,489)*.12))
	else:
		draw_circle(gantry,8,Color(.21,.25,.22))
		draw_arc(gantry,6,0,TAU,18,Color(.61,.61,.46),1.6,true)
		paint_prop(self,Rect2(1014,284,94,70),Rect2(weight.x-17,weight.y-5,34,40),Color(.86,.85,.71))
		for dx in [-11,11]: draw_line(weight+Vector2(dx,-6),weight+Vector2(dx,35),Color(.27,.29,.24),2,true)
	# The entire painted deck rotates with the real support body. Repeated short
	# board crops retain grain size instead of stretching one tree over the span.
	draw_set_transform(hinge,bridge_body.rotation,Vector2.ONE)
	for board in range(int(ceil(span/28.0))):
		var width=minf(28,span-board*28)
		draw_texture_rect_region(atlas,Rect2(board*28,0,width,bridge_height),Rect2(1014+(board%2)*20,284,60,36),Color(.94,.91,.78))
		draw_line(Vector2(board*28+1,3),Vector2(board*28+1,bridge_height-1),Color(.23,.27,.22,.55),.8,true)
	draw_texture_rect_region(atlas,Rect2(0,bridge_height-3,span,5),Rect2(555,296,300,52),Color(.70,.75,.63))
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	var plate_x=float(data.get("plate_x",15055)); var sink=3.0 if not plate_child.is_empty() and not latched else 0.0
	if is_instance_valid(rig_art): paint_rig("cradle",Rect2(plate_x-48,hinge.y+2+sink,93,43))
	paint_prop(self,Rect2(1014,284,94,70),Rect2(plate_x-38,hinge.y-5+sink,76,8))
	for dx in [-31,31]: draw_circle(Vector2(plate_x+dx,hinge.y-2+sink),1.5,Color(.30,.32,.25))
	# A small real-looking rail gives the waiting child a visible hand contact.
	paint_beam(self,Vector2(plate_x-29,hinge.y),Vector2(plate_x-29,hinge.y-58),5)
	paint_beam(self,Vector2(plate_x-29,hinge.y-53),Vector2(plate_x+32,hinge.y-53),5)
	var latch=Vector2(float(data.get("latch_x",15445)),hinge.y)
	if is_instance_valid(rig_art): paint_rig("pawl",Rect2(latch+Vector2(27,-49),Vector2(453,486)*.10),Color(.98,.94,.81) if latched else Color(.87,.88,.81))
	paint_prop(self,Rect2(1014,284,94,70),Rect2(latch.x-29,latch.y-5,58,8),Color(.84,.85,.74))
	draw_line(latch+Vector2(-10,-3),latch+Vector2(13,-12 if not latched else -5),Color(.29,.33,.28),5,true)
	draw_circle(latch+Vector2(-10,-3),3,Color(.64,.64,.48))

func draw_foreground(canvas):
	if data.is_empty(): return
	# Low foreground stanchions frame the crossing without hiding either child.
	for x in [hinge.x-17,hinge.x+span+8]:
		paint_beam(canvas,Vector2(x,hinge.y+15),Vector2(x,hinge.y-30),5,Color(.78,.81,.69))
	if lower_amount>.995:
		canvas.draw_polyline(PackedVector2Array([hinge+Vector2(-17,-27),hinge+Vector2(span*.5,-19),hinge+Vector2(span+8,-27)]),Color(.43,.46,.35,.7),1.1,true)
