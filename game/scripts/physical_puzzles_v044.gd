extends Node2D

# Two authored machines share geometry helpers, not their completion logic.
# Orchard: native crate contact pays out a hinged ramp. Freight: a real rider
# is raised by a stationary winch and catches the upper load ratchet.
var game
var data={}
var kind=""
var state="idle"
var solved=false
var crate:RigidBody2D
var plate_body:StaticBody2D
var chock_body:StaticBody2D
var ramp_body:AnimatableBody2D
var lift_body:AnimatableBody2D
var amount=0.0
var actual_travel=0.0
var push_ticks=0
var winch_ticks=0
var rider_ticks=0
var load_contact=false
var crank_angle=0.0
var paused_velocity=Vector2.ZERO
var paused_body=false
var atlas=preload("res://assets/props/painted_survival_atlas_v020.png")
var parts:Texture2D
var part_regions={}
var cache_item={}
var lift_width=160.0
var ramp_ticks={"Girl":0,"Boy":0}
var lowering_blocked=false

func _ready():
	kind=str(data.kind); z_index=0
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	if ResourceLoader.exists("res://assets/props/mechanical_parts_v044.png"):
		parts=load("res://assets/props/mechanical_parts_v044.png")
		part_regions={"crate":Rect2(76,80,439,267),"platform":Rect2(40,612,686,144),"pulley":Rect2(1043,402,125,133),"winch":Rect2(139,808,414,398),"ratchet":Rect2(765,894,463,275),"handle":Rect2(1036,1026,189,64)}
	for item in game.level.interact:
		if item.get("id","")==data.get("cache_id",""): cache_item=item
	if kind=="weighted_orchard":
		crate=RigidBody2D.new(); crate.name="OrchardCounterweight"
		crate.mass=9; crate.lock_rotation=true; crate.gravity_scale=1; crate.linear_damp=6
		crate.collision_layer=1; crate.collision_mask=1|4; crate.contact_monitor=true; crate.max_contacts_reported=16
		crate.can_sleep=false; crate.freeze_mode=RigidBody2D.FREEZE_MODE_STATIC
		var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=Vector2(64,56); shape.shape=box
		crate.add_child(shape); add_child(crate)
		var track_start=float(data.crate_x)-40
		plate_body=box_body(Rect2(track_start,float(data.floor_y),float(data.plate_x)+40-track_start,9),"WeightCradle")
		# The iron carriage starts on its own flush track. Its final chock is
		# crate-only hardware; native support AND end-stop contact must load it.
		plate_body.collision_mask=1|2
		chock_body=box_body(Rect2(float(data.plate_x)+32,float(data.floor_y)-12,10,12),"IronWeightChock")
		chock_body.collision_layer=4; chock_body.collision_mask=1
		ramp_body=deck(Vector2(data.ramp_x,data.floor_y),Vector2(200,14),"HingedOrchardRamp")
	else:
		lift_width=float(data.get("lift_w",160))
		lift_body=deck(Vector2(data.lift_x,data.low_y),Vector2(lift_width,18),"FreightCargoLift")
		lift_body.sync_to_physics=true
	reset_from_progress()

func box_body(rect,label):
	var body=StaticBody2D.new(); body.name=label; body.collision_layer=1; body.collision_mask=2
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=rect.size
	shape.shape=box; shape.position=rect.get_center(); body.add_child(shape); add_child(body)
	return body

func deck(at,size,label):
	var body=AnimatableBody2D.new(); body.name=label; body.position=at
	body.collision_layer=1; body.collision_mask=2; body.sync_to_physics=false
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=size
	shape.shape=box; shape.position=size*.5; body.add_child(shape); add_child(body)
	return body

func reset_from_progress():
	solved=bool(game.flags.get(str(data.key),false)); amount=1.0 if solved else 0.0
	state="latched" if solved else "idle"; push_ticks=0; winch_ticks=0; rider_ticks=0; load_contact=false
	ramp_ticks={"Girl":0,"Boy":0}
	paused_body=false; paused_velocity=Vector2.ZERO; actual_travel=0; crank_angle=0
	lowering_blocked=false
	if kind=="weighted_orchard":
		crate.freeze=true
		crate.position=Vector2(float(data.plate_x) if solved else float(data.crate_x),float(data.floor_y)-28)
		crate.rotation=0; crate.linear_velocity=Vector2.ZERO; crate.angular_velocity=0
		PhysicsServer2D.body_set_state(crate.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM,crate.global_transform)
		PhysicsServer2D.body_set_state(crate.get_rid(),PhysicsServer2D.BODY_STATE_LINEAR_VELOCITY,Vector2.ZERO)
		crate.freeze=solved; ramp_body.rotation=lerpf(.4,-atan2(120.0,160.0),amount)
	else:
		lift_body.sync_to_physics=false
		lift_body.position=Vector2(data.lift_x,float(data.upper_y) if solved else float(data.low_y))
		PhysicsServer2D.body_set_state(lift_body.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM,lift_body.global_transform)
		lift_body.reset_physics_interpolation(); lift_body.sync_to_physics=true
		actual_travel=float(data.low_y)-lift_body.position.y
	queue_redraw()

func foot_contact(child,body):
	if not is_instance_valid(child) or not child.is_on_floor(): return false
	for index in range(child.get_slide_collision_count()):
		var contact=child.get_slide_collision(index)
		if contact.get_collider()==body and contact.get_normal().y<-.65: return true
	return false

func crate_on_plate():
	if absf(crate.position.x-float(data.plate_x))>24 or absf(crate.position.y+28-float(data.floor_y))>3 or absf(crate.linear_velocity.y)>12: return false
	var contacts=crate.get_colliding_bodies()
	return contacts.has(plate_body) and contacts.has(chock_body)

func crate_pushing(child):
	if solved or not Input.is_action_pressed("interact") or absf(Input.get_axis("left","right"))<.1: return false
	for index in range(child.get_slide_collision_count()):
		if child.get_slide_collision(index).get_collider()==crate: return true
	return false

func at_winch():
	return game.player.is_on_floor() and absf(game.player.position.x-float(data.winch_x))<36 and absf(game.player.position.y-float(data.floor_y))<10 and absf(Input.get_axis("left","right"))<.1

func child_bounds(child):
	# Use the live collider, including its actual crouch transition height.
	var half=child.col.shape.size*.5; var bounds=Rect2(child.col.global_transform* -half,Vector2.ZERO)
	for corner in [Vector2(half.x,-half.y),half,Vector2(-half.x,half.y)]: bounds=bounds.expand(child.col.global_transform*corner)
	return bounds

func obstructed_lowering(next_y):
	var swept=Rect2(lift_body.position,Vector2(lift_width,next_y-lift_body.position.y+18)).grow(.3)
	for child in [game.player,game.boy]:
		if foot_contact(child,lift_body): continue
		var bounds=child_bounds(child)
		# A child on or above the top is carried normally. Only a real body
		# beneath the deck can arrest its downward swept solid volume.
		if bounds.end.y<=lift_body.position.y+1: continue
		if swept.intersects(bounds): return true
	return false

func work_contacts(child):
	if game.mode!="playing" or solved: return {}
	if kind=="weighted_orchard":
		if child!=game.player or not crate_pushing(child): return {}
		var hand=crate.position+Vector2(-33,-10)
		return {"kind":"cart_push","weight":1.0,"near":hand,"far":hand+Vector2(2,-9),"look":crate.position}
	if child!=game.player or not at_winch() or not Input.is_action_pressed("interact"): return {}
	var pivot=Vector2(float(data.winch_x)+18,float(data.floor_y)-50)
	var hand=pivot+Vector2(20,0).rotated(crank_angle)
	return {"kind":"winch","weight":1.0,"near":hand,"far":hand+Vector2(-5,-6),"look":pivot}

func event(name):
	game.encounter_events.append({"kind":name,"id":data.id,"chapter":game.chapter,"time":game.playtime,"travel":actual_travel})

func latch():
	solved=true; state="latched"; game.flags[data.key]=true
	if kind=="weighted_orchard":
		crate.freeze=true; crate.linear_velocity=Vector2.ZERO
		game.announce_message("The chock bites. The orchard ramp will hold.",5)
	else: game.announce_message("His weight catches the upper tooth. Climb the freight steps and call him across [Q].",6)
	game.play_sfx("wheel",-11); event("physical_puzzle_latched"); game.write_save()

func _physics_process(dt):
	if game==null: return
	if game.mode!="playing":
		if kind=="weighted_orchard" and not crate.freeze:
			paused_body=true; paused_velocity=crate.linear_velocity; crate.freeze=true
		return
	if kind=="weighted_orchard":
		for child in [game.player,game.boy]:
			if foot_contact(child,ramp_body): ramp_ticks[str(child.name)]=int(ramp_ticks.get(str(child.name),0))+1
		if paused_body:
			paused_body=false; crate.freeze=false; crate.linear_velocity=paused_velocity
		if crate_pushing(game.player): push_ticks+=1
		if not solved:
			if not Input.is_action_pressed("interact") or absf(Input.get_axis("left","right"))<.1: crate.linear_velocity.x=move_toward(crate.linear_velocity.x,0,dt*630)
			load_contact=crate_on_plate()
			amount=move_toward(amount,1.0 if load_contact else 0.0,dt*.8)
			ramp_body.rotation=lerpf(.4,-atan2(120.0,160.0),amount*amount*(3-2*amount))
			state="raising" if load_contact and amount<1 else "idle"
			if amount>=1 and load_contact: latch()
		actual_travel=crate.position.x-float(data.crate_x)
	else:
		var rider=foot_contact(game.boy,lift_body)
		if rider: rider_ticks+=1
		lowering_blocked=false
		if not solved:
			var working=at_winch() and Input.is_action_pressed("interact")
			var lowering=working and game.player.crouching
			if working and (rider or lowering):
				var target=float(data.low_y) if lowering else float(data.upper_y)
				var next_y=move_toward(lift_body.position.y,target,dt*42)
				lowering_blocked=lowering and next_y>lift_body.position.y and obstructed_lowering(next_y)
				if lowering_blocked: state="blocked"
				else:
					lift_body.position.y=next_y
					winch_ticks+=1; state="lowering" if lowering else "raising"
			else: state="holding" if actual_travel>1 else "idle"
			actual_travel=float(data.low_y)-lift_body.position.y
			amount=actual_travel/maxf(1,float(data.low_y)-float(data.upper_y)); crank_angle=actual_travel*.065
			if rider and absf(lift_body.position.y-float(data.upper_y))<.5 and absf(game.boy.position.y-float(data.upper_y))<5: latch()
	queue_redraw()

func transformed_corners(body,size):
	var result=PackedVector2Array()
	for point in [Vector2.ZERO,Vector2(size.x,0),size,Vector2(0,size.y)]: result.append(body.position+point.rotated(body.rotation))
	return result

func polygon_top(points,x):
	var height=INF
	for index in range(points.size()):
		var a=points[index]; var b=points[(index+1)%points.size()]
		if x<minf(a.x,b.x)-.001 or x>maxf(a.x,b.x)+.001: continue
		if absf(b.x-a.x)<.001:
			if absf(x-a.x)<.001: height=minf(height,minf(a.y,b.y))
		else: height=minf(height,lerpf(a.y,b.y,clampf((x-a.x)/(b.x-a.x),0,1)))
	return height

func obstacle_rects():
	if kind=="weighted_orchard":
		var bounds=Rect2(ramp_body.position,Vector2.ZERO)
		for point in transformed_corners(ramp_body,Vector2(200,14)): bounds=bounds.expand(point)
		return [Rect2(crate.position-Vector2(32,28),Vector2(64,56)),bounds,Rect2(float(data.plate_x)+32,float(data.floor_y)-12,10,12)]
	return [Rect2(lift_body.position,Vector2(lift_width,18))]

func support_at(x,fallback_y=700.0):
	var options=[]
	if kind=="weighted_orchard":
		if absf(x-crate.position.x)<=32: options.append(crate.position.y-28)
		if x>=float(data.crate_x)-40 and x<=float(data.plate_x)+40: options.append(float(data.floor_y))
		var top=polygon_top(transformed_corners(ramp_body,Vector2(200,14)),x)
		if is_finite(top): options.append(top)
	else:
		if x>=lift_body.position.x and x<=lift_body.position.x+lift_width: options.append(lift_body.position.y)
	var closest=INF; var distance=INF
	for y in options:
		if absf(y-fallback_y)<distance: closest=y; distance=absf(y-fallback_y)
	return closest

func objective_text():
	var start=float(data.crate_x) if kind=="weighted_orchard" else float(data.winch_x)
	if game.player.position.x<start-220 or game.player.position.x>float(cache_item.get("x",start))+240: return ""
	if game.flags.get(str(data.get("cache_id","")),false): return "The supplies are packed. Keep following the road together."
	if kind=="weighted_orchard":
		return "The chock holds. Follow the timber ramp to the keeper's supplies." if solved else "Hold E and move to push the heavy crate onto the iron cradle."
	if solved:
		return "Climb the freight steps, then call him across [Q]." if not game.boy.following else "The lift is caught. Reunite on the upper loading walk and search together."
	if lowering_blocked: return "He's beneath the cargo deck. Call him clear [Q] before lowering it."
	if not game.boy.following and foot_contact(game.boy,lift_body): return "He's waiting on the cargo lift. Work the winch [hold E] from the lower road."
	return "Bring him onto the cargo platform, ask him to wait [Q], then return to the winch. Crouch + E lowers it."

func beam(a,b,width,tint=Color(.91,.90,.79)):
	draw_set_transform(a,(b-a).angle(),Vector2.ONE)
	draw_texture_rect_region(atlas,Rect2(0,-width*.5,a.distance_to(b),width),Rect2(555,296,300,52),tint)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func _draw():
	if kind=="weighted_orchard":
		if is_instance_valid(parts): draw_texture_rect_region(parts,Rect2(crate.position-Vector2(32,28),Vector2(64,56)),part_regions.crate,Color(.95,.94,.85))
		else: draw_texture_rect_region(atlas,Rect2(crate.position-Vector2(32,28),Vector2(64,56)),Rect2(938,185,316,202),Color(.94,.92,.83))
		beam(Vector2(float(data.crate_x)-40,data.floor_y+3),Vector2(float(data.plate_x)+41,data.floor_y+3),7)
		beam(Vector2(float(data.plate_x)+34,data.floor_y-3),Vector2(float(data.plate_x)+40,data.floor_y-10),9,Color(.56,.54,.39))
		var cable=PackedVector2Array([Vector2(data.plate_x,data.floor_y+5),Vector2(data.ramp_x-16,data.floor_y+12),ramp_body.position+Vector2(160,5).rotated(ramp_body.rotation)])
		draw_polyline(cable,Color(.43,.43,.31),1.5,true)
		draw_set_transform(ramp_body.position,ramp_body.rotation,Vector2.ONE)
		if is_instance_valid(parts):
			var uvs=PackedVector2Array()
			for point in [Vector2(649,158),Vector2(1194,282),Vector2(1195,324),Vector2(649,200)]: uvs.append(point/parts.get_size())
			draw_polygon(PackedVector2Array([Vector2.ZERO,Vector2(200,0),Vector2(200,14),Vector2(0,14)]),PackedColorArray([Color(.96,.94,.84)]),uvs,parts)
		else:
			for index in range(10): draw_texture_rect_region(atlas,Rect2(index*20,0,20,14),Rect2(1014,284,60,36),Color(.94,.91,.77))
		draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
		draw_circle(ramp_body.position+Vector2(0,7),6,Color(.37,.38,.27))
	else:
		var floor_y=float(data.floor_y); var upper=float(data.upper_y); var left=float(data.lift_x)
		for x in [left-9,left+lift_width+9]:
			beam(Vector2(x,floor_y+5),Vector2(x,upper-95),11)
			beam(Vector2(x-17,floor_y),Vector2(x,upper+20),6,Color(.76,.80,.68))
		beam(Vector2(left-22,upper-94),Vector2(left+lift_width+23,upper-94),12)
		for x in [left+13,left+lift_width-13]:
			draw_line(Vector2(x,upper-84),Vector2(x,lift_body.position.y+2),Color(.43,.45,.33),1.8,true)
			if is_instance_valid(parts): draw_texture_rect_region(parts,Rect2(x-11,upper-95,22,23),part_regions.pulley,Color(.91,.91,.80))
		if is_instance_valid(parts): draw_texture_rect_region(parts,Rect2(lift_body.position+Vector2(0,-11),Vector2(lift_width,34)),part_regions.platform,Color(.96,.94,.84))
		else:
			for index in range(int(ceil(lift_width/20))): beam(lift_body.position+Vector2(index*20,9),lift_body.position+Vector2(minf(lift_width,index*20+20),9),18)
		var pivot=Vector2(float(data.winch_x)+18,floor_y-50)
		if is_instance_valid(parts):
			draw_texture_rect_region(parts,Rect2(pivot+Vector2(-16,-31.8),Vector2(82.8,79.6)),part_regions.winch,Color(.95,.93,.84))
			draw_set_transform(pivot,crank_angle,Vector2.ONE)
			draw_texture_rect_region(parts,Rect2(0,-5,23,10),part_regions.handle,Color(.96,.94,.85))
			draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
			draw_texture_rect_region(parts,Rect2(left+lift_width+2,upper-27,51,31),part_regions.ratchet,Color(.98,.93,.77) if solved else Color(.83,.86,.77))
		else:
			draw_texture_rect_region(atlas,Rect2(pivot+Vector2(-28,-3),Vector2(56,53)),Rect2(901,768,353,413),Color(.93,.92,.82))
			draw_line(pivot,pivot+Vector2(20,0).rotated(crank_angle),Color(.57,.54,.38),5,true)
		draw_circle(pivot+Vector2(20,0).rotated(crank_angle),3,Color(.34,.36,.28))
		draw_polyline(PackedVector2Array([pivot,Vector2(left-9,upper-84),Vector2(left+13,upper-84)]),Color(.42,.43,.31),1.5,true)
	if not cache_item.is_empty() and game.flags.get(str(data.key),false):
		var contents=game.world.interaction_art.cache_contents(game,cache_item)
		if not game.flags.get(str(cache_item.id),false):
			for index in range(contents.size()):
				var resource=contents[index]
				game.world.interaction_art.paint(self,resource,Vector2(float(cache_item.x)+(index-(contents.size()-1)*.5)*30,float(cache_item.y)+2),30 if resource=="medicine" else 40,Color(.95,.94,.85))

func draw_foreground(_canvas): pass
