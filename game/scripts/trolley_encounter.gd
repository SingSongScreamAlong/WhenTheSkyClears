extends Node2D

# A handcart remains an ordinary native rigid body: the child's existing
# E+movement contact supplies its velocity. Canvas coverage travels with it.
var game
var data={}
var body:RigidBody2D
var dock_body:StaticBody2D
var cabinet_body:StaticBody2D
var hatch_body:AnimatableBody2D
var state="parked"
var docked=false
var hatch_amount=0.0
var travel=0.0
var push_ticks=0
var protected_ticks={"Girl":0,"Boy":0,"both":0}
var paused_velocity=Vector2.ZERO
var paused_motion=false
var previous_x=0.0
var wheel_angle=0.0
var origin=Vector2.ZERO
var chassis_size=Vector2(84,48)
var cabinet=Vector2.ZERO
var art:Texture2D
var regions={"chassis":Rect2(15,200,595,204),"canvas":Rect2(635,92,605,316),"wheel":Rect2(136,484,391,388),"ratchet":Rect2(727,495,501,377),"cabinet":Rect2(74,924,479,244),"lid":Rect2(626,1053,587,103)}
var fallback=preload("res://assets/props/painted_survival_atlas_v020.png")
var announced=false
var cache_item={}

func _ready():
	z_index=0
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	origin=Vector2(float(data.get("x",10355)),float(data.get("y",646))-chassis_size.y*.5)
	cabinet=Vector2(float(data.get("cache_x",11070)),float(data.get("cache_y",700)))
	for item in game.level.interact:
		if item.get("id","")==str(data.get("cache_id","school_trolley_medicine")): cache_item=item
	var path="res://assets/props/Trolley_Parts_v043.png"
	if ResourceLoader.exists(path): art=load(path)
	body=RigidBody2D.new(); body.name="ShelterHandcart"
	body.lock_rotation=true; body.mass=14; body.gravity_scale=1; body.linear_damp=4.0
	body.collision_layer=1; body.collision_mask=1; body.can_sleep=false
	body.contact_monitor=true; body.max_contacts_reported=12
	body.continuous_cd=RigidBody2D.CCD_MODE_CAST_SHAPE
	body.freeze_mode=RigidBody2D.FREEZE_MODE_STATIC
	var material=PhysicsMaterial.new(); material.friction=.65; material.bounce=0
	body.physics_material_override=material
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=chassis_size; shape.shape=box
	body.add_child(shape); add_child(body)
	dock_body=make_box(Rect2(float(data.get("dock_x",10920))+chassis_size.x*.5,float(data.get("dock_y",700))-36,9,36),"TrolleyDock")
	cabinet_body=make_box(Rect2(cabinet+Vector2(-36,-38),Vector2(72,38)),"SupplyCabinet")
	hatch_body=AnimatableBody2D.new(); hatch_body.name="SupplyHatch"
	hatch_body.collision_layer=1; hatch_body.collision_mask=2; hatch_body.sync_to_physics=false
	hatch_body.position=cabinet+Vector2(36,-38)
	var lid_shape=CollisionShape2D.new(); var lid_box=RectangleShape2D.new(); lid_box.size=Vector2(72,10)
	lid_shape.shape=lid_box; lid_shape.position=Vector2(-36,-5); hatch_body.add_child(lid_shape); add_child(hatch_body)
	reset_from_progress()

func make_box(rect,label):
	var result=StaticBody2D.new(); result.name=label; result.collision_layer=1; result.collision_mask=2
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=rect.size
	shape.shape=box; shape.position=rect.get_center(); result.add_child(shape); add_child(result)
	return result

func reset_from_progress():
	docked=bool(game.flags.get(str(data.get("key","school_trolley_docked")),false))
	state="docked" if docked else "parked"; hatch_amount=1.0 if docked else 0.0
	body.freeze=true; body.position=Vector2(float(data.get("dock_x",10920)),float(data.get("dock_y",700))-24) if docked else origin
	body.linear_velocity=Vector2.ZERO; body.angular_velocity=0; body.rotation=0
	# A live RigidBody can restore its previous server transform on the next
	# synchronization tick. Reset both representations together, only here.
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM,body.global_transform)
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_LINEAR_VELOCITY,Vector2.ZERO)
	PhysicsServer2D.body_set_state(body.get_rid(),PhysicsServer2D.BODY_STATE_ANGULAR_VELOCITY,0.0)
	body.freeze=docked; paused_motion=false; paused_velocity=Vector2.ZERO
	travel=maxf(0,body.position.x-origin.x); previous_x=body.position.x; wheel_angle=travel/18.0
	push_ticks=0; protected_ticks={"Girl":0,"Boy":0,"both":0}; announced=false
	hatch_body.rotation=1.25*hatch_amount
	queue_redraw()

func cart_floor(): return body.position.y+chassis_size.y*.5

func ground_below(x):
	# The chassis is deliberately level, while its short sprung wheel legs
	# follow the actual authored grade. Ignore the chassis/cabinet support API.
	for segment in game.level.ground:
		if x>=float(segment.x) and x<=float(segment.x)+float(segment.w): return float(game.profile_y(segment,x))
	return cart_floor()

func wheel_centers():
	var centers=[]
	for dx in [-25,25]:
		var x=body.position.x+dx
		centers.append(Vector2(x,ground_below(x)-18))
	return centers

func shield_bounds():
	return Rect2(body.position.x-175,cart_floor()-142,213,142)

func is_covered(child):
	if not is_instance_valid(child) or not child.crouching or not child.is_on_floor(): return false
	if child.col.shape.size.y>(78.0 if child.is_girl else 66.0): return false
	var bounds=shield_bounds(); var half_width=child.col.shape.size.x*.5
	if child.position.x-half_width<bounds.position.x or child.position.x+half_width>bounds.end.x: return false
	if absf(child.position.y-cart_floor())>45: return false
	# The painted roof slopes up toward the cart. A nearby silhouette above
	# the cloth or beyond its trailing edge receives no moving cover.
	var u=clampf((child.position.x-half_width-bounds.position.x)/bounds.size.x,0,1)
	var roof=cart_floor()-lerpf(62,142,u)
	return child.position.y-child.col.shape.size.y>=roof+2

func pushing_contact(child):
	if docked or state=="docking" or not is_instance_valid(child) or not child.is_on_floor(): return false
	if not child.controlled or not Input.is_action_pressed("interact") or absf(Input.get_axis("left","right"))<.1: return false
	for index in range(child.get_slide_collision_count()):
		if child.get_slide_collision(index).get_collider()==body: return true
	return false

func work_contacts(child):
	if game==null or game.mode!="playing" or not pushing_contact(child): return {}
	var direction=signf(Input.get_axis("left","right"))
	var grip=body.position+Vector2(-direction*44,-18)
	return {"kind":"cart_push","weight":1.0,"near":grip,"far":grip+Vector2(direction*3,-7),"look":body.position+Vector2(direction*25,-23)}

func obstacle_rects():
	if not is_instance_valid(body): return []
	var cabinet_height=48.0 if hatch_amount<.001 else 38.0
	var result=[Rect2(body.position-chassis_size*.5,chassis_size),Rect2(cabinet+Vector2(-36,-cabinet_height),Vector2(72,cabinet_height)),Rect2(float(data.get("dock_x",10920))+42,float(data.get("dock_y",700))-36,9,36)]
	if hatch_amount>.001:
		var bounds=Rect2(hatch_body.position,Vector2.ZERO)
		for corner in [Vector2(-72,-10),Vector2(0,-10),Vector2(0,0),Vector2(-72,0)]: bounds=bounds.expand(hatch_body.position+corner.rotated(hatch_body.rotation))
		result.append(bounds)
	return result

func support_at(x,fallback_y=700.0):
	var surfaces=[]
	for rect in [Rect2(body.position-chassis_size*.5,chassis_size),Rect2(cabinet+Vector2(-36,-38),Vector2(72,38)),Rect2(float(data.get("dock_x",10920))+42,float(data.get("dock_y",700))-36,9,36)]:
		if x>=rect.position.x and x<=rect.end.x: surfaces.append(rect.position.y)
	var corners=PackedVector2Array()
	for corner in [Vector2(-72,-10),Vector2(0,-10),Vector2(0,0),Vector2(-72,0)]: corners.append(hatch_body.position+corner.rotated(hatch_body.rotation))
	var lid_surface=INF
	for index in range(4):
		var a=corners[index]; var b=corners[(index+1)%4]
		if x<minf(a.x,b.x)-.001 or x>maxf(a.x,b.x)+.001: continue
		if absf(b.x-a.x)<.001:
			if absf(x-a.x)<.001: lid_surface=minf(lid_surface,minf(a.y,b.y))
		else: lid_surface=minf(lid_surface,lerpf(a.y,b.y,clampf((x-a.x)/(b.x-a.x),0,1)))
	if is_finite(lid_surface): surfaces.append(lid_surface)
	var closest=INF; var distance=INF
	for y in surfaces:
		if absf(y-fallback_y)<distance: closest=y; distance=absf(y-fallback_y)
	return closest

func event(kind):
	game.encounter_events.append({"kind":kind,"id":str(data.get("id","school_trolley")),"chapter":game.chapter,"time":game.playtime,"travel":travel,"push_ticks":push_ticks})

func _physics_process(dt):
	if game==null: return
	if game.mode!="playing":
		if not body.freeze:
			paused_motion=true; paused_velocity=body.linear_velocity; body.freeze=true
		return
	if paused_motion:
		paused_motion=false; body.freeze=false; body.linear_velocity=paused_velocity
	var distance=body.position.x-previous_x; previous_x=body.position.x
	wheel_angle+=distance/18.0; travel=maxf(0,body.position.x-origin.x)
	if pushing_contact(game.player): push_ticks+=1
	var both=true
	for child in [game.player,game.boy]:
		var protected=is_covered(child)
		if protected: protected_ticks[str(child.name)]=int(protected_ticks.get(str(child.name),0))+1
		both=both and protected
	if both: protected_ticks.both+=1
	if not docked and state!="docking":
		var handling=Input.is_action_pressed("interact") and absf(Input.get_axis("left","right"))>.1 and absf(game.player.position.x-body.position.x)<98 and absf(game.player.position.y-cart_floor())<48
		if not handling:
			# The spring parking shoe arrests the cart when its handle is released.
			# It is a brake on real velocity; position is never driven or snapped.
			body.linear_velocity.x=move_toward(body.linear_velocity.x,0.0,dt*630)
		state="moving" if handling and absf(body.linear_velocity.x)>8 else "parked"
		if body.get_colliding_bodies().has(dock_body) and travel>float(data.get("dock_x",10920))-origin.x-16 and push_ticks>30:
			state="docking"; body.freeze=true; body.linear_velocity=Vector2.ZERO
			game.play_sfx("wheel",-12); event("trolley_ratchet_caught")
	if state=="docking":
		hatch_amount=move_toward(hatch_amount,1.0,dt*1.3)
		if hatch_amount>=1:
			docked=true; state="docked"; game.flags[str(data.get("key","school_trolley_docked"))]=true
			game.announce_message("The ratchet catches. The keeper's medicine hatch is open. Bring him through.",5)
			event("trolley_hatch_open"); game.write_save()
	hatch_body.rotation=1.25*(hatch_amount*hatch_amount*(3-2*hatch_amount))
	if not announced and pushing_contact(game.player):
		announced=true; game.announce_message("Keep both children crouched beneath the canvas. Hold E and move to push the shelter.",6)
	queue_redraw()

func objective_text():
	if not is_instance_valid(game.player) or game.player.position.x<origin.x-360 or game.player.position.x>cabinet.x+340: return ""
	if docked:
		if game.flags.get(str(data.get("cache_id","school_trolley_medicine")),false): return "The medicine is packed. Take the road behind the school kitchens."
		return "The dock holds the cart. Step over it and search the opened medicine cabinet together."
	if state=="docking": return "The cart is caught. Wait for the supply hatch to open."
	if not game.boy.following: return "Call him close [Q]. Both children need the canvas when the patrol light returns."
	return "Keep both children low beneath the canvas. Hold E and move to push the cart to the far dock."

func draw_part(key,rect,tint=Color(.94,.93,.86)):
	if is_instance_valid(art): draw_texture_rect_region(art,rect,regions[key],tint)
	else: draw_texture_rect_region(fallback,rect,Rect2(505,488,415,269),tint)

func cache_contents():
	if game.flags.get(str(data.get("cache_id","school_trolley_medicine")),false): return []
	return game.world.interaction_art.cache_contents(game,cache_item)

func _draw():
	if not is_instance_valid(body): return
	var floor_y=cart_floor(); var at=body.position
	# Cloth and posts occupy the rear plane; both crouched silhouettes remain
	# visible in front of the painting rather than being hidden by a flat panel.
	draw_part("canvas",shield_bounds(),Color(.94,.93,.85))
	# Source handles occupy the left part of the chassis crop. The solid crate
	# part is registered to the real84px collision box, not the full handle span.
	draw_part("chassis",Rect2(at.x-96,floor_y-57,138,48))
	for center in wheel_centers():
		draw_line(Vector2(center.x,floor_y-25),center,Color(.32,.34,.27),3,true)
		draw_circle(center,3,Color(.55,.53,.39))
		draw_set_transform(center,wheel_angle,Vector2.ONE)
		draw_part("wheel",Rect2(-18,-18,36,36),Color(.87,.88,.78))
		draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	var dock=Vector2(float(data.get("dock_x",10920))+46,float(data.get("dock_y",700)))
	draw_part("ratchet",Rect2(dock+Vector2(-14,-67),Vector2(65,67)),Color(.94,.90,.79))
	var cable_start=dock+Vector2(22,-44)
	var cable_end=hatch_body.position+Vector2(-58,-7).rotated(hatch_body.rotation)
	var cable=PackedVector2Array()
	for step in range(17):
		var t=float(step)/16.0
		cable.append(cable_start.lerp(cable_end,t)+Vector2(0,4*t*(1-t)*lerpf(18,3,hatch_amount)))
	draw_polyline(cable,Color(.22,.26,.22,.86),2.3,true)
	draw_polyline(cable,Color(.65,.59,.43,.65),.8,true)
	draw_part("cabinet",Rect2(cabinet+Vector2(-36,-38),Vector2(72,38)))
	if hatch_amount>.6:
		var contents=cache_contents()
		if "medicine" in contents: game.world.interaction_art.paint(self,"medicine",cabinet+Vector2(-17,-9),21,Color(.97,.96,.87))
		if "scrap" in contents: game.world.interaction_art.paint(self,"scrap",cabinet+Vector2(14,-10),29,Color(.95,.94,.84))
	draw_set_transform(hatch_body.position,hatch_body.rotation,Vector2.ONE)
	draw_part("lid",Rect2(-72,-10,72,10),Color(.95,.92,.82))
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func draw_foreground(canvas):
	if not is_instance_valid(body): return
	# A narrow iron axle and parking shoe tie the two visible wheel contacts
	# together without covering the children's faces or shelter silhouettes.
	var centers=wheel_centers()
	canvas.draw_line(centers[0],centers[1],Color(.25,.29,.25),3,true)
	if state=="parked":
		canvas.draw_line(Vector2(body.position.x-18,cart_floor()-13),Vector2(body.position.x-11,cart_floor()-2),Color(.39,.39,.29),3,true)
