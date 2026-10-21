extends Node2D

# A level horizontal rope ferry. The rail fixes its height; native rigid-body
# velocity, floor contacts and the far jetty's collision own horizontal travel.
var game
var data={}
var body:RigidBody2D
var dock_body:StaticBody2D
var origin=Vector2.ZERO
var moored=false
var state="waiting"
var travel=0.0
var crank_angle=0.0
var crank_ticks=0
var riding_ticks={"Girl":0,"Boy":0,"both":0}
var protected_ticks={"Girl":0,"Boy":0,"both":0}
var paused=false
var cache_item={}
var last_x=0.0
var atlas=preload("res://assets/props/ferry_parts_v044.png")
var supply_atlas=preload("res://assets/props/Interaction_Props_v041.png")
var regions={"hull":Rect2(10,249,740,171),"cloth":Rect2(766,201,479,243),"jetty":Rect2(23,524,692,351),"reel":Rect2(756,514,486,359),"crank":Rect2(171,982,440,178),"bollard":Rect2(711,902,535,321)}

func _ready():
	z_index=0; texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	origin=Vector2(float(data.get("start_x",12430)),float(data.get("deck_y",670))+9)
	for item in game.level.interact:
		if str(item.get("id",""))==str(data.get("cache_id","terrace_bowl")): cache_item=item
	body=RigidBody2D.new(); body.name="GardenRopeFerry"
	body.set_meta("mechanism_drive_only",true)
	body.mass=40; body.gravity_scale=0; body.lock_rotation=true; body.linear_damp=0
	body.collision_layer=1; body.collision_mask=1; body.can_sleep=false
	body.contact_monitor=true; body.max_contacts_reported=16
	body.continuous_cd=RigidBody2D.CCD_MODE_CAST_SHAPE
	body.freeze_mode=RigidBody2D.FREEZE_MODE_STATIC
	var material=PhysicsMaterial.new(); material.friction=1; material.bounce=0
	body.physics_material_override=material
	var shape=CollisionShape2D.new(); var rectangle=RectangleShape2D.new(); rectangle.size=Vector2(200,18); shape.shape=rectangle
	body.add_child(shape); add_child(body)
	# The top surfaces themselves are authored platforms. This bumper overlaps
	# the deck side, stays flush with its floor and leaves 112px below it.
	dock_body=StaticBody2D.new(); dock_body.name="GardenFerryDock"
	dock_body.collision_layer=1; dock_body.collision_mask=1
	var stop_shape=CollisionShape2D.new(); var stop_box=RectangleShape2D.new(); stop_box.size=Vector2(10,18)
	stop_shape.shape=stop_box; stop_shape.position=Vector2(float(data.get("far_x",12980))+5,float(data.get("deck_y",670))+9)
	dock_body.add_child(stop_shape); add_child(dock_body)
	reset_from_progress()

func deck_y(): return body.position.y-9
func deck_rect(): return Rect2(body.position-Vector2(100,9),Vector2(200,18))

func reset_from_progress():
	moored=bool(game.flags.get(str(data.get("key","garden_ferry_moored")),false))
	state="moored" if moored else "waiting"
	body.freeze=true
	body.position=Vector2(float(data.get("far_x",12980))-100,origin.y) if moored else origin
	body.rotation=0; body.linear_velocity=Vector2.ZERO; body.angular_velocity=0
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM,body.global_transform)
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_LINEAR_VELOCITY,Vector2.ZERO)
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_ANGULAR_VELOCITY,0.0)
	body.freeze=moored; paused=false; last_x=body.position.x
	travel=maxf(0,body.position.x-origin.x); crank_angle=travel*.052
	crank_ticks=0; riding_ticks={"Girl":0,"Boy":0,"both":0}; protected_ticks={"Girl":0,"Boy":0,"both":0}
	queue_redraw()

func foot_contact(child):
	if not is_instance_valid(child) or not child.is_on_floor() or absf(child.position.y-deck_y())>4: return false
	for index in range(child.get_slide_collision_count()):
		var contact=child.get_slide_collision(index)
		if contact.get_collider()==body and contact.get_normal().y<-.65: return true
	return false

func is_covered(child):
	if not foot_contact(child) or not child.crouching: return false
	if child.col.shape.size.y>(78.0 if child.is_girl else 66.0): return false
	return absf(child.position.x-body.position.x)+child.col.shape.size.x*.5<92

func both_boarded(): return foot_contact(game.player) and foot_contact(game.boy)
func both_low(): return is_covered(game.player) and is_covered(game.boy)
func crank_pivot(): return Vector2(body.position.x+58,deck_y()-49)
func crank_grip(): return crank_pivot()+Vector2(18,-5).rotated(crank_angle)

func operating():
	return not moored and both_low() and Input.is_action_pressed("interact") and absf(Input.get_axis("left","right"))<.1 and absf(game.player.position.x-(body.position.x+44))<28

func work_contacts(child):
	if game==null or game.mode!="playing" or moored or not foot_contact(child): return {}
	if child==game.player and operating():
		var grip=crank_grip()
		return {"kind":"winch","weight":1.0,"near":grip,"far":grip+Vector2(-3,-4),"look":crank_pivot()}
	if child==game.boy and child.crouching and absf(body.linear_velocity.x)>1:
		var rail=Vector2(clampf(child.position.x+child.facing*11,body.position.x-81,body.position.x+81),deck_y()-43)
		return {"kind":"balance_hold","weight":.78,"near":rail,"far":rail+Vector2(-7,-3),"look":game.player.position+Vector2(0,-48)}
	return {}

func event(kind):
	game.encounter_events.append({"kind":kind,"id":str(data.get("id","garden_rope_ferry")),"chapter":game.chapter,"time":game.playtime,"travel":travel,"crank_ticks":crank_ticks})

func _physics_process(_dt):
	if game==null or not is_instance_valid(body): return
	if game.mode!="playing":
		if not body.freeze: body.freeze=true; paused=true
		return
	if paused:
		paused=false; body.freeze=moored; body.linear_velocity=Vector2.ZERO
	var both=true; var sheltered=true
	for child in [game.player,game.boy]:
		var label=str(child.name); var aboard=foot_contact(child); var covered=is_covered(child)
		if aboard: riding_ticks[label]=int(riding_ticks.get(label,0))+1
		if covered: protected_ticks[label]=int(protected_ticks.get(label,0))+1
		both=both and aboard; sheltered=sheltered and covered
	if both: riding_ticks.both+=1
	if sheltered: protected_ticks.both+=1
	travel=maxf(0,body.position.x-origin.x); crank_angle=travel*.052; last_x=body.position.x
	if not moored:
		var working=operating()
		# The hold-to-work brake changes real velocity, never a body/child pose.
		body.linear_velocity=Vector2(float(data.get("speed",54)) if working else 0.0,0)
		if working: crank_ticks+=1
		state="crossing" if working else ("holding" if travel>1 else "waiting")
		if body.get_colliding_bodies().has(dock_body) and both and travel>float(data.get("far_x",12980))-100-origin.x-4 and crank_ticks>60:
			body.linear_velocity=Vector2.ZERO; body.freeze=true; moored=true; state="moored"
			game.flags[str(data.get("key","garden_ferry_moored"))]=true
			game.play_sfx("wheel",-12); game.announce_message("The rope goes slack. The far mooring holds. Step ashore together.",5)
			event("garden_ferry_moored"); game.write_save()
	queue_redraw()

func support_at(x,fallback_y=700.0):
	if absf(x-body.position.x)<=100: return deck_y()
	return INF

func obstacle_rects():
	return [deck_rect(),Rect2(float(data.get("far_x",12980)),deck_y(),10,18)]

func objective_text():
	if game.player.position.x<float(data.get("near_x",12230))-170 or game.player.position.x>float(cache_item.get("x",13170))+200: return ""
	if moored:
		return "The bandage is packed. Follow the garden path together." if game.flags.get(str(data.get("cache_id","terrace_bowl")),false) else "The mooring holds. Step ashore and search the dry bowl together."
	if not both_boarded(): return "Bring both children onto the ferry. The lower watercourse is passable, but cold."
	if not both_low(): return "Crouch together beneath the ferry cloth [S]. Keep his feet on the deck."
	return "Hold E beside the reel. Release it to brake. Both children must stay aboard and low."

func cache_contents():
	if game.flags.get(str(data.get("cache_id","terrace_bowl")),false): return []
	return game.world.interaction_art.cache_contents(game,cache_item)

func part(key,rect,tint=Color(.98,.98,.92)):
	draw_texture_rect_region(atlas,rect,regions[key],tint)

func _draw():
	if not is_instance_valid(body): return
	var y=deck_y(); var x=body.position.x
	for jetty in [Rect2(float(data.get("near_x",12230)),y-6,100,136),Rect2(float(data.get("far_x",12980)),y-6,80,136)]:
		part("jetty",jetty,Color(.92,.95,.86))
	# These ropes span the real current reel/dock coordinates; neither is a
	# generic action icon painted over an unrelated static backdrop.
	var rope_y=y-36
	draw_polyline(PackedVector2Array([Vector2(float(data.get("near_x",12230))+80,rope_y),Vector2(x-84,rope_y+5),crank_pivot(),Vector2(float(data.get("far_x",12980))+20,rope_y)]),Color(.43,.40,.27),1.5,true)
	part("cloth",Rect2(x-96,y-107,192,98),Color(.97,.98,.93))
	part("hull",Rect2(x-110,y-7,220,50))
	# Painted wheel bearing and separate original crank share the same pivot
	# sampled by character_work_contacts on every native animation tick.
	part("reel",Rect2(crank_pivot()+Vector2(-17,-17),Vector2(57,43)))
	draw_set_transform(crank_pivot(),crank_angle,Vector2.ONE)
	part("crank",Rect2(-1.4,-7.2,22,8.9),Color(.96,.95,.88))
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	part("bollard",Rect2(float(data.get("far_x",12980))+6,y-37,47,50))
	if moored:
		draw_line(Vector2(x+92,y+2),Vector2(float(data.get("far_x",12980))+26,y-16),Color(.52,.47,.31),2,true)
	if not cache_contents().is_empty():
		var at=Vector2(float(cache_item.get("x",13170)),float(cache_item.get("y",708)))
		draw_texture_rect_region(supply_atlas,Rect2(at+Vector2(-17,-28),Vector2(34,28)),Rect2(594,43,394,411),Color(.97,.97,.90))

func draw_foreground(canvas):
	if not is_instance_valid(body): return
	var y=deck_y(); var x=body.position.x
	canvas.draw_line(Vector2(x-90,y-43),Vector2(x+85,y-43),Color(.45,.40,.28,.86),1.4,true)
	for dx in [-90,85]: canvas.draw_line(Vector2(x+dx,y-47),Vector2(x+dx,y+3),Color(.40,.39,.28),2,true)
