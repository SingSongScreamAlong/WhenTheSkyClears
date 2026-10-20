extends Node2D

# This encounter is a real body/counterweight mechanism. The child standing on
# the wheel loads the axle; no interaction key or progress flag starts it.
var game
var data={}
var state="locked"
var wheel:RigidBody2D
var gate_body:StaticBody2D
var bridge_body:StaticBody2D
var fence_body:StaticBody2D
var gate_lift=0.0
var travel=0.0
var hit_children=[]
var load_clock=0.0
var warning_clock=0.0
var rolling_clock=0.0
var impact_spent=false
var radius=96.0
var origin=Vector2.ZERO
var background:Texture2D
var parts:Texture2D
var part_regions={}
var original_fence:Texture2D
var paused_motion=false
var paused_velocity=Vector2.ZERO
var paused_angular=0.0
# Cosmetic fragments have their own bounded, pause-aware simulation. They never
# apply force or add colliders to the real wheel and the children's route.
var debris=[]
var debris_serial=0
var visual_state="locked"
var warning_dust_clock=0.0
var contact_distance=0.0
var previous_wheel_position=Vector2.ZERO
var previous_gate_lift=0.0
var released_chain_end=Vector2.ZERO
var chain_drop_clock=0.0

func _ready():
	z_index=1
	radius=float(data.get("radius",96))
	origin=Vector2(data.get("wheel_x",16700),data.get("wheel_y",604))
	load_art()
	bridge_body=make_box(Rect2(float(data.get("bridge_x",15720)),float(data.get("bridge_y",700)),float(data.get("bridge_w",210)),float(data.get("bridge_h",20))),"MillBridge")
	gate_body=make_box(Rect2(float(data.get("gate_x",17350))-float(data.get("gate_w",94))/2,float(data.get("gate_y",700))-float(data.get("gate_h",205)),float(data.get("gate_w",94)),float(data.get("gate_h",205))),"MillSluiceGate")
	# The approach fence doubles as the first broad step. Its painted top and
	# collider coincide with the authored 16320/640 approach scaffold.
	var fence_x=float(data.get("fence_x",16320))
	var fence_y=float(data.get("fence_y",700))
	var fence_w=float(data.get("fence_w",150))
	var fence_h=float(data.get("fence_h",60))
	fence_body=make_box(Rect2(fence_x,fence_y-fence_h,fence_w,fence_h),"MillClimbableFence")
	create_wheel()
	reset_from_progress()

func load_art():
	var background_path="res://assets/environments/Mill_Background_v040.png"
	if ResourceLoader.exists(background_path): background=load(background_path)
	var parts_path="res://assets/props/Mill_Parts_v040.png"
	if ResourceLoader.exists(parts_path):
		parts=load(parts_path)
		# These are painted objects, not equal atlas cells. Faint alpha specks
		# and neighbouring posts polluted get_used_rect(), padding the visible
		# wheel away from its circle and leaving transparent timber swatches.
		var source_scale=Vector2(parts.get_width()/2172.0,parts.get_height()/724.0)
		for key in ["wheel","gate","fence"]:
			var source={"wheel":Rect2(64,13,691,694),"gate":Rect2(860,47,454,612),"fence":Rect2(1398,284,737,249)}[key]
			part_regions[key]=Rect2(source.position*source_scale,source.size*source_scale)
	var old_path="res://assets/props/painted_survival_atlas_v020.png"
	if ResourceLoader.exists(old_path): original_fence=load(old_path)

func make_box(rect,label):
	var body=StaticBody2D.new()
	body.name=label; body.collision_layer=1; body.collision_mask=2
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new()
	box.size=rect.size; shape.shape=box; shape.position=rect.position+rect.size/2
	body.add_child(shape); add_child(body)
	return body

func create_wheel():
	wheel=RigidBody2D.new(); wheel.name="BreakawayWheel"
	wheel.mass=78; wheel.gravity_scale=1; wheel.linear_damp=.12; wheel.angular_damp=.12
	wheel.collision_layer=1; wheel.collision_mask=1; wheel.can_sleep=false
	wheel.continuous_cd=RigidBody2D.CCD_MODE_CAST_SHAPE
	var material=PhysicsMaterial.new(); material.friction=.84; material.bounce=.015
	wheel.physics_material_override=material
	var shape=CollisionShape2D.new(); var circle=CircleShape2D.new(); circle.radius=radius
	shape.shape=circle; wheel.add_child(shape); add_child(wheel)
	wheel.freeze=true; wheel.freeze_mode=RigidBody2D.FREEZE_MODE_STATIC
	if is_instance_valid(game.get("right_boundary")): wheel.add_collision_exception_with(game.right_boundary)

func reset_from_progress():
	if not is_instance_valid(wheel): create_wheel()
	var complete=bool(game.flags.get(str(data.get("key","mill_gate_open")),false))
	state="open" if complete else "locked"
	paused_motion=false; paused_velocity=Vector2.ZERO; paused_angular=0
	load_clock=0; warning_clock=0; rolling_clock=0; impact_spent=false; hit_children=[]
	travel=float(data.get("travel_required",240)) if complete else 0.0
	gate_lift=float(data.get("gate_h",205))+12 if complete else 0.0
	wheel.freeze=true; wheel.linear_velocity=Vector2.ZERO; wheel.angular_velocity=0; wheel.rotation=0
	wheel.position=Vector2(float(game.level.width)+radius+400,origin.y) if complete else origin
	wheel.collision_layer=0 if complete else 1
	gate_body.collision_layer=0 if complete else 1
	gate_body.position=Vector2(0,-gate_lift)
	debris.clear(); debris_serial=0; visual_state=state
	warning_dust_clock=0; contact_distance=0
	previous_wheel_position=wheel.position; previous_gate_lift=gate_lift
	released_chain_end=origin+Vector2(float(data.get("travel_required",240))*float(data.get("roll_direction",1)),radius-2)
	chain_drop_clock=1.0 if complete else 0.0
	queue_redraw()

func child_on_crown(child):
	if not is_instance_valid(child) or not is_instance_valid(wheel) or not child.is_on_floor(): return false
	if child.position.y>wheel.position.y-radius*.25: return false
	for index in range(child.get_slide_collision_count()):
		var contact=child.get_slide_collision(index)
		if contact.get_collider()==wheel and contact.get_normal().y<-.55: return true
	return false

func child_touches_rim(child):
	for index in range(child.get_slide_collision_count()):
		if child.get_slide_collision(index).get_collider()==wheel: return true
	# Circle against the actual changing standing/crouching rectangle also
	# catches a rigid-body push between consecutive child move_and_slide calls.
	var box=child.col.shape as RectangleShape2D
	var center=child.global_position+child.col.position
	var closest=wheel.global_position.clamp(center-box.size*.5,center+box.size*.5)
	return closest.distance_to(wheel.global_position)<=radius+2.5

func event(kind,child=""):
	var record={"kind":kind,"id":str(data.get("id","woods_mill")),"chapter":game.chapter,"time":game.playtime}
	if not child.is_empty(): record["child"]=child
	game.encounter_events.append(record)

func release_wheel():
	state="rolling"; rolling_clock=0
	wheel.freeze=false; wheel.sleeping=false
	var direction=float(data.get("roll_direction",1))
	wheel.apply_central_impulse(Vector2(wheel.mass*115*direction,0))
	wheel.apply_torque_impulse(wheel.mass*radius*57.5*direction)
	game.play_sfx("wheel",-8)
	game.play_sfx("warning",-14)
	event("mill_breakaway")

func _physics_process(dt):
	if game==null or game.mode!="playing":
		if is_instance_valid(wheel) and not wheel.freeze:
			paused_motion=true; paused_velocity=wheel.linear_velocity; paused_angular=wheel.angular_velocity
			wheel.freeze=true
		queue_redraw(); return
	if paused_motion and is_instance_valid(wheel):
		wheel.freeze=false; wheel.sleeping=false
		wheel.linear_velocity=paused_velocity; wheel.angular_velocity=paused_angular
		paused_motion=false
	if state in ["locked","loading"]:
		var loaded=child_on_crown(game.player) or child_on_crown(game.boy)
		if loaded:
			state="loading"; load_clock+=dt
			if load_clock>=float(data.get("load_seconds",.4)):
				state="warning"; warning_clock=0
				game.play_sfx("wheel",-13); game.play_sfx("warning",-17)
				event("mill_weight")
		else:
			state="locked"; load_clock=0
	elif state=="warning":
		warning_clock+=dt
		if warning_clock>=float(data.get("warning_seconds",1.2)): release_wheel()
	elif state in ["rolling","open"] and is_instance_valid(wheel) and not wheel.freeze:
		rolling_clock+=dt
		var direction=float(data.get("roll_direction",1))
		var desired=170.0*direction
		# The counterweight provides force and torque; contact/friction own the
		# actual velocity and rotation. Positions are never scripted along a path.
		wheel.apply_central_force(Vector2(wheel.mass*(desired-wheel.linear_velocity.x)*2.4,0))
		var inertia=wheel.mass*radius*radius*.5
		wheel.apply_torque(inertia*(desired/radius-wheel.angular_velocity)*2.4)
		travel=maxf(travel,(wheel.position.x-origin.x)*direction)
		var required=maxf(1,float(data.get("travel_required",240)))
		var target=clampf(travel/required,0,1)*(float(data.get("gate_h",205))+12)
		gate_lift=move_toward(gate_lift,target,dt*220)
		gate_body.position=Vector2(0,-gate_lift)
		if state=="rolling" and travel>=required and gate_lift>=float(data.get("gate_h",205))+10:
			state="open"; game.flags[str(data.get("key","mill_gate_open"))]=true
			gate_body.collision_layer=0; game.play_sfx("wheel",-14); event("mill_open")
		if rolling_clock>.7 and not impact_spent and absf(wheel.linear_velocity.x)>25:
			for child in [game.player,game.boy]:
				var ahead=(child.position.x-wheel.position.x)*direction
				if ahead>0 and ahead<radius+55 and child.position.y>wheel.position.y+22 and absf(child.position.y-(wheel.position.y+radius))<72 and child_touches_rim(child):
					hit_children.append(child.name); event("mill_wheel_hit",child.name)
			if not hit_children.is_empty():
				impact_spent=true
				game.hurt(34,"The loose wheel is too heavy. Keep him behind it and clear of the rim.")
		if wheel.position.x>float(game.level.width)+radius+500:
			wheel.queue_free(); wheel=null
	update_visuals(dt)
	queue_redraw()

func emit_debris(at,count,burst=false):
	for index in range(count):
		if debris.size()>=84: debris.pop_front()
		debris_serial+=1
		var seed_value=float(debris_serial)
		var spread=sin(seed_value*2.39996)
		var chip=burst and index%3!=0
		var velocity=Vector2(spread*(62 if burst else 24),-18-absf(cos(seed_value*1.71))*(68 if burst else 23))
		debris.append({"at":at+Vector2(spread*7,0),"velocity":velocity,"age":0.0,"life":1.05+absf(spread)*.7,"size":1.1+absf(spread)*1.6,"chip":chip,"angle":seed_value*1.37,"spin":spread*4.5,"floor":float(data.get("gate_y",700))})

func update_visuals(dt):
	if state=="open":
		if visual_state!="open" and is_instance_valid(wheel):
			released_chain_end=wheel.position+Vector2(0,-7); chain_drop_clock=0
		chain_drop_clock+=dt
	if state=="warning":
		warning_dust_clock+=dt
		if warning_dust_clock>=.11:
			warning_dust_clock=0
			emit_debris(origin+Vector2(8,13),2)
	if state in ["rolling","open"] and visual_state=="warning":
		emit_debris(origin+Vector2(5,7),18,true)
		emit_debris(origin+Vector2(0,radius-4),7)
	if is_instance_valid(wheel):
		var floor_y=wheel.position.y+radius
		if game.has_method("surface_y_at"): floor_y=game.surface_y_at(wheel.position.x,floor_y)
		# Contact dust follows distance actually rolled, never a timer that could
		# continue to billow while the wheel is blocked, airborne or paused.
		if state in ["rolling","open"] and absf(wheel.position.y+radius-floor_y)<8:
			contact_distance+=absf(wheel.position.x-previous_wheel_position.x)
			if contact_distance>=15:
				contact_distance=fposmod(contact_distance,15)
				emit_debris(Vector2(wheel.position.x-12,floor_y-2),3)
		previous_wheel_position=wheel.position
	if gate_lift-previous_gate_lift>=14:
		previous_gate_lift=gate_lift
		for side in [-1,1]: emit_debris(Vector2(float(data.get("gate_x",17350))+side*float(data.get("gate_w",94))*.5,float(data.get("gate_y",700))-gate_lift-8),1)
	for index in range(debris.size()-1,-1,-1):
		var p=debris[index]
		p.age+=dt
		if p.age>=p.life: debris.remove_at(index); continue
		p.velocity.y+=dt*(210 if p.chip else 74)
		p.at+=p.velocity*dt; p.angle+=p.spin*dt
		if p.at.y>p.floor-1:
			p.at.y=p.floor-1; p.velocity.x*=.84; p.velocity.y=0; p.spin=0
	visual_state=state

func _draw():
	if data.is_empty(): return
	draw_bridge()
	draw_axle_supports()
	draw_chain()
	draw_gate()
	if is_instance_valid(wheel): draw_wheel()
	draw_axle_bearing()
	draw_debris()

func draw_bridge():
	var x=float(data.get("bridge_x",15720)); var y=float(data.get("bridge_y",700)); var width=float(data.get("bridge_w",210))
	for index in range(int(ceil(width/25.0))):
		var px=x+index*25
		paint_beam(Vector2(px,y+8),Vector2(minf(px+25,x+width),y+8),17,Color(.49,.55,.43))
	paint_beam(Vector2(x-13,y+19),Vector2(x+width+13,y+19),12,Color(.31,.41,.32))
	for post in [x-6,x+width+6]: paint_beam(Vector2(post,y+31),Vector2(post,y-51),9,Color(.39,.47,.35))
	# A low rear rope is separate from the traversable deck at exactly y700.
	draw_line(Vector2(x-6,y-42),Vector2(x+width+6,y-42),Color(.50,.53,.39,.66),1.4,true)

func draw_axle_supports():
	var floor_y=origin.y+radius-2
	# This trestle is behind the wheel's depth plane. The timber and broken
	# bearing remain in the wall after the rim has physically rolled away.
	for side in [-1,1]:
		var post=origin+Vector2(side*51,0)
		paint_mill_timber(Vector2(post.x,floor_y),post+Vector2(0,-45),15,Color(.78,.83,.72))
		paint_mill_timber(Vector2(origin.x+side*78,floor_y),origin+Vector2(side*35,13),10,Color(.72,.79,.69))
		paint_mill_timber(Vector2(post.x-11,floor_y-2),Vector2(post.x+11,floor_y-2),9,Color(.69,.75,.64))
	paint_mill_timber(origin+Vector2(-72,11),origin+Vector2(72,11),18,Color(.86,.88,.77))
	paint_mill_timber(origin+Vector2(-64,39),origin+Vector2(64,39),9,Color(.74,.80,.69))
	for side in [-1,1]:
		var bolt=origin+Vector2(side*51,11)
		draw_circle(bolt,3.8,Color(.15,.18,.16)); draw_circle(bolt+Vector2(-.8,-.8),1.9,Color(.47,.46,.34))

func warning_amount():
	return clampf(warning_clock/maxf(.1,float(data.get("warning_seconds",1.2))),0,1) if state=="warning" else 0.0

func draw_axle_bearing():
	var broken=state in ["rolling","open"]
	var amount=warning_amount()
	var cap=origin+Vector2(0,2)
	draw_arc(cap,17,.12,PI-.12,20,Color(.12,.15,.14),6,true)
	draw_arc(cap,17,.12,PI-.12,20,Color(.43,.43,.33),2,true)
	# The right cheek shears away; it is no longer drawn across the travelling
	# hub. The exposed notch and its split end grain stay at the old axle.
	if broken:
		paint_mill_timber(origin+Vector2(12,10),origin+Vector2(27,23),6,Color(.94,.81,.57))
		draw_line(origin+Vector2(10,6),origin+Vector2(5,17),Color(.09,.12,.10),2,true)
	else:
		var slip=Vector2(amount*4,sin(warning_clock*54)*amount*.9)
		draw_arc(cap+slip,17,PI+.12,TAU-.12,20,Color(.16,.19,.17),5,true)
		draw_arc(cap+slip,17,PI+.12,TAU-.12,20,Color(.55,.53,.39),1.2,true)
		if amount>.15:
			var split=PackedVector2Array([origin+Vector2(14,-3),origin+Vector2(19,4),origin+Vector2(15,9),origin+Vector2(23,16)])
			draw_polyline(split,Color(.09,.12,.10,amount),1.4,true)

func chain_point(a,b,t,sag):
	return a.lerp(b,t)+Vector2(0,4*t*(1-t)*sag)

func draw_chain_run(a,b,sag,payout):
	var length=a.distance_to(b)
	if length<2: return
	var segments=maxi(2,int(ceil(length/18)))
	var centerline=PackedVector2Array()
	for index in range(segments+1): centerline.append(chain_point(a,b,float(index)/segments,sag))
	draw_polyline(centerline,Color(.12,.16,.15,.92),2.7,true)
	# Alternating forged links move only with measured wheel travel/gate lift.
	# Their narrow highlights are worn iron, with no emissive danger outline.
	var phase=fposmod(payout,9.0)
	for index in range(mini(180,int(ceil(length/9)))):
		var distance=index*9.0+phase
		if distance>length-2: break
		var t=distance/length
		var center=chain_point(a,b,t,sag)
		var tangent=(chain_point(a,b,minf(1,t+.01),sag)-chain_point(a,b,maxf(0,t-.01),sag)).normalized()
		var normal=Vector2(-tangent.y,tangent.x)
		var link=PackedVector2Array()
		for step in range(9):
			var angle=step*TAU/8
			link.append(center+tangent*cos(angle)*3.5+normal*sin(angle)*(1.65 if index%2==0 else .65))
		draw_polyline(link,Color(.42,.43,.34,.87),1.1,true)

func draw_pulley(at,phase):
	draw_circle(at+Vector2(1,1),12,Color(.09,.13,.12))
	draw_circle(at,10,Color(.33,.37,.31))
	draw_arc(at,8,0,TAU,24,Color(.57,.56,.41),1.1,true)
	for index in range(4):
		var spoke=Vector2.from_angle(phase+index*TAU/4)*7
		draw_line(at,at+spoke,Color(.16,.21,.19),2,true)
	draw_circle(at,2.9,Color(.18,.21,.18)); draw_circle(at+Vector2(-.7,-.7),1.1,Color(.60,.56,.39))

func draw_chain():
	var gate_x=float(data.get("gate_x",17350)); var gate_y=float(data.get("gate_y",700)); var gate_h=float(data.get("gate_h",205))
	var required=float(data.get("travel_required",240))
	var direction=float(data.get("roll_direction",1))
	var axle=wheel.position+Vector2(0,-7) if is_instance_valid(wheel) else origin+Vector2(required*direction,0)
	if state=="open":
		# Once the gate catches at full lift, the haul-chain leaves the hub and
		# drops onto the ground. It never hangs from an invisible stopped wheel.
		axle=released_chain_end
		axle.y=minf(origin.y+radius-2,axle.y+chain_drop_clock*chain_drop_clock*150)
	# The rear fairlead makes rightward wheel travel draw chain OUT, lifting
	# the hanging gate. Its headstock clears the gate at its real full height.
	var fairlead=origin+Vector2(-138*direction,-radius-44)
	var pulley=Vector2(gate_x-9,gate_y-gate_h-(gate_h+12)-34)
	paint_mill_timber(fairlead+Vector2(-20,-4),fairlead+Vector2(20,-4),10,Color(.74,.80,.68))
	paint_mill_timber(fairlead+Vector2(-16,32),fairlead+Vector2(-16,-9),9,Color(.72,.79,.67))
	var taut=state in ["warning","rolling"]
	draw_chain_run(axle,fairlead+Vector2(7,0),1.1 if taut else 4.5,minf(travel,required))
	draw_chain_run(fairlead+Vector2(0,-9),pulley+Vector2(0,-9),1.6 if taut else 9.0,minf(travel,required))
	var hook=Vector2(gate_x+7,gate_y-gate_h-gate_lift+11)
	draw_chain_run(pulley+Vector2(9,0),hook,0,-gate_lift)
	draw_pulley(fairlead,minf(travel,required)/10); draw_pulley(pulley,gate_lift/10)
	draw_arc(hook+Vector2(0,2),4,-PI*.2,PI*1.6,12,Color(.18,.23,.20),2.3,true)

func draw_gate():
	var x=float(data.get("gate_x",17350)); var y=float(data.get("gate_y",700)); var height=float(data.get("gate_h",205)); var width=float(data.get("gate_w",94))
	var head_y=y-height-(height+12)-34
	for dx in [-width*.67,width*.67]:
		paint_mill_timber(Vector2(x+dx,y+4),Vector2(x+dx,head_y-8),12,Color(.80,.85,.74))
		paint_mill_timber(Vector2(x+dx,y+3),Vector2(x+dx+signf(dx)*23,y-75),9,Color(.74,.80,.69))
	paint_mill_timber(Vector2(x-width*.82,head_y-6),Vector2(x+width*.82,head_y-6),17,Color(.90,.91,.79))
	for dx in [-width*.67,width*.67]:
		draw_circle(Vector2(x+dx,head_y-6),3.6,Color(.17,.21,.17))
		draw_circle(Vector2(x+dx-.7,head_y-6.7),1.5,Color(.56,.53,.37))
	if parts!=null:
		draw_texture_rect_region(parts,Rect2(x-width*.5,y-height-gate_lift,width,height),part_regions.gate,Color(.90,.93,.84))
	else:
		game.world.paint_asset(self,"door",Vector2(x,y-gate_lift),width,height,Color(.53,.63,.48))

func draw_wheel():
	var amount=warning_amount()
	var shudder=Vector2(sin(warning_clock*61)*.8,cos(warning_clock*47)*.5)*amount
	# Less than one world pixel: the visual creak keeps the crown aligned with
	# its unchanged circular collider while the children retreat.
	draw_set_transform(wheel.position+shudder,wheel.rotation+sin(warning_clock*39)*amount*.006,Vector2.ONE)
	if parts!=null:
		draw_texture_rect_region(parts,Rect2(-radius,-radius,radius*2,radius*2),part_regions.wheel,Color(.94,.96,.88))
	else:
		draw_arc(Vector2.ZERO,radius-5,0,TAU,56,Color(.22,.31,.23),13,true)
		draw_arc(Vector2.ZERO,radius-1,0,TAU,56,Color(.48,.53,.36),3,true)
		for spoke in range(10):
			var end=Vector2(cos(spoke*TAU/10),sin(spoke*TAU/10))*(radius-9)
			draw_line(Vector2.ZERO,end,Color(.38,.46,.30),8,true)
		draw_circle(Vector2.ZERO,12,Color(.21,.30,.21))
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func draw_debris():
	for p in debris:
		var fade=pow(1-p.age/p.life,1.25)
		if p.chip:
			var along=Vector2.from_angle(p.angle)*p.size*2.4
			draw_line(p.at-along,p.at+along,Color(.20,.23,.16,fade),p.size+1,true)
			draw_line(p.at-along,p.at+along,Color(.59,.49,.29,fade),p.size*.75,true)
		else:
			draw_circle(p.at,p.size*(1+p.age*1.6),Color(.56,.51,.36,fade*.25))

func paint_mill_timber(a,b,thickness,tint):
	var delta=b-a
	draw_set_transform(a,delta.angle(),Vector2.ONE)
	draw_line(Vector2.ZERO,Vector2(delta.length(),0),Color(.17,.21,.16),thickness,true)
	if parts!=null and part_regions.has("fence"):
		var source_scale=Vector2(parts.get_width()/2172.0,parts.get_height()/724.0)
		var grain=Rect2(Vector2(1483,345)*source_scale,Vector2(184,34)*source_scale)
		draw_texture_rect_region(parts,Rect2(0,-thickness*.5,delta.length(),thickness),grain,tint)
	elif original_fence!=null:
		draw_texture_rect_region(original_fence,Rect2(0,-thickness*.5,delta.length(),thickness),Rect2(555,296,300,52),tint)
	else: draw_line(Vector2.ZERO,Vector2(delta.length(),0),tint,thickness,true)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func draw_foreground(canvas):
	if data.is_empty(): return
	var x=float(data.get("fence_x",16320)); var y=float(data.get("fence_y",700)); var width=float(data.get("fence_w",150)); var height=float(data.get("fence_h",60))
	if parts!=null:
		canvas.draw_texture_rect_region(parts,Rect2(x,y-height,width,height),part_regions.fence,Color(.85,.91,.79))
		var bridge_x=float(data.get("bridge_x",15720)); var bridge_y=float(data.get("bridge_y",700)); var bridge_w=float(data.get("bridge_w",210))
		# This is the near railing of the same physical bridge. It occludes
		# ankles in the depth plane while the native deck carries both children.
		canvas.draw_texture_rect_region(parts,Rect2(bridge_x-12,bridge_y-60,bridge_w+24,60),part_regions.fence,Color(.83,.89,.77))
	elif original_fence!=null:
		canvas.draw_texture_rect_region(original_fence,Rect2(x,y-height,width,height),Rect2(488,185,450,202),Color(.47,.57,.43))

func draw_background(canvas):
	if data.is_empty(): return
	var floor_y=float(data.get("bridge_y",700))
	if background!=null:
		# Paint is registered to the real axle, deck and gate separately. A
		# single wide card would imply bridges/doors at different coordinates.
		var scale=.85
		var house_source=Rect2(470,30,950,655)
		var house_at=origin-Vector2(1250-470,525-30)*scale
		paint_architecture_edge(canvas,Rect2(house_at,house_source.size*scale),house_source,Color(.83,.90,.84))
		var bridge_source=Rect2(0,430,565,255)
		var bridge_scale=.9
		var bridge_mid=float(data.get("bridge_x",15720))+float(data.get("bridge_w",210))*.5
		var bridge_at=Vector2(bridge_mid-315*bridge_scale,floor_y-(495-430)*bridge_scale)
		paint_architecture_edge(canvas,Rect2(bridge_at,bridge_source.size*bridge_scale),bridge_source,Color(.85,.91,.82),.04,.21)
		var gate_at=Vector2(float(data.get("gate_x",17350))-100,float(data.get("gate_y",700))-212)
		canvas.draw_texture_rect_region(background,Rect2(gate_at,Vector2(200,212)),Rect2(1420,325,340,360),Color(.85,.91,.82))
	else:
		# During source loading only: grounded masonry, never a replacement for
		# the final layered painting and independently moving components.
		game.world.paint_asset(canvas,"wall",Vector2(origin.x+220,700),740,269,Color(.47,.54,.45))

func paint_beam(a,b,thickness,tint):
	var delta=b-a
	draw_set_transform(a,delta.angle(),Vector2.ONE)
	if original_fence!=null: draw_texture_rect_region(original_fence,Rect2(0,-thickness*.5,delta.length(),thickness),Rect2(555,296,300,52),tint)
	else: draw_line(Vector2.ZERO,Vector2(delta.length(),0),tint,thickness,true)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func paint_architecture_edge(canvas,destination,source,tint,left_fade=.13,right_fade=.06):
	# The house is a depth layer: blend the cropped ivy margin into the woods,
	# while retaining the opaque masonry and the separately colliding wheel.
	for column in range(40):
		var u=(column+.5)/40.0
		var alpha=smoothstep(0.0,left_fade,u)*smoothstep(0.0,right_fade,1.0-u)
		var from=Rect2(source.position+Vector2(source.size.x*column/40.0,0),Vector2(source.size.x/40.0,source.size.y))
		var to=Rect2(destination.position+Vector2(destination.size.x*column/40.0,0),Vector2(destination.size.x/40.0+.1,destination.size.y))
		canvas.draw_texture_rect_region(background,to,from,Color(tint,tint.a*alpha))
