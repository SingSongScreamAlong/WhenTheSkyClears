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
		var pixels=parts.get_image()
		var cell=float(parts.get_width())/3.0
		for index in range(3):
			var box=Rect2i(int(index*cell),0,int(cell),parts.get_height())
			var used=pixels.get_region(box).get_used_rect()
			part_regions[["wheel","gate","fence"][index]]=Rect2(Vector2(box.position+used.position),Vector2(used.size))
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
	queue_redraw()

func _draw():
	if data.is_empty(): return
	draw_bridge()
	draw_chain()
	draw_gate()
	if is_instance_valid(wheel): draw_wheel()

func draw_bridge():
	var x=float(data.get("bridge_x",15720)); var y=float(data.get("bridge_y",700)); var width=float(data.get("bridge_w",210))
	for index in range(int(ceil(width/25.0))):
		var px=x+index*25
		paint_beam(Vector2(px,y+8),Vector2(minf(px+25,x+width),y+8),17,Color(.49,.55,.43))
	paint_beam(Vector2(x-13,y+19),Vector2(x+width+13,y+19),12,Color(.31,.41,.32))
	for post in [x-6,x+width+6]: paint_beam(Vector2(post,y+31),Vector2(post,y-51),9,Color(.39,.47,.35))
	# A low rear rope is separate from the traversable deck at exactly y700.
	draw_line(Vector2(x-6,y-42),Vector2(x+width+6,y-42),Color(.50,.53,.39,.66),1.4,true)

func draw_chain():
	var gate_x=float(data.get("gate_x",17350)); var gate_y=float(data.get("gate_y",700)); var gate_h=float(data.get("gate_h",205))
	var axle=wheel.position if is_instance_valid(wheel) and state!="open" else origin+Vector2(minf(travel,float(data.get("travel_required",240))),0)
	var pulley=Vector2(gate_x-9,gate_y-gate_h-49)
	draw_line(axle+Vector2(0,-10),pulley,Color(.18,.24,.20,.86),3.2,true)
	draw_line(axle+Vector2(0,-11),pulley-Vector2(0,1),Color(.52,.55,.41,.40),.9,true)
	draw_arc(pulley,8,0,TAU,20,Color(.32,.39,.30),3,true)
	draw_line(pulley+Vector2(7,0),Vector2(gate_x+7,gate_y-gate_h-gate_lift),Color(.43,.48,.35,.82),2,true)

func draw_gate():
	var x=float(data.get("gate_x",17350)); var y=float(data.get("gate_y",700)); var height=float(data.get("gate_h",205)); var width=float(data.get("gate_w",94))
	if background==null:
		for dx in [-width*.66,width*.66]: paint_beam(Vector2(x+dx,y+4),Vector2(x+dx,y-height-45),12,Color(.37,.47,.36))
		paint_beam(Vector2(x-width*.76,y-height-42),Vector2(x+width*.76,y-height-42),17,Color(.41,.50,.37))
	if parts!=null:
		draw_texture_rect_region(parts,Rect2(x-width*.5,y-height-gate_lift,width,height),part_regions.gate,Color(.90,.93,.84))
	else:
		game.world.paint_asset(self,"door",Vector2(x,y-gate_lift),width,height,Color(.53,.63,.48))

func draw_wheel():
	draw_set_transform(wheel.position,wheel.rotation,Vector2.ONE)
	if parts!=null:
		draw_texture_rect_region(parts,Rect2(-radius,-radius,radius*2,radius*2),part_regions.wheel,Color(.94,.96,.88))
	else:
		draw_arc(Vector2.ZERO,radius-5,0,TAU,56,Color(.22,.31,.23),13,true)
		draw_arc(Vector2.ZERO,radius-1,0,TAU,56,Color(.48,.53,.36),3,true)
		for spoke in range(10):
			var end=Vector2(cos(spoke*TAU/10),sin(spoke*TAU/10))*(radius-9)
			draw_line(Vector2.ZERO,end,Color(.38,.46,.30),8,true)
		draw_circle(Vector2.ZERO,12,Color(.21,.30,.21))
	# A slipping axle, wood dust and an irregular wobble are warning cues.
	if state=="warning":
		var amount=clampf(warning_clock/maxf(.1,float(data.get("warning_seconds",1.2))),0,1)
		for speck in range(9):
			var age=fposmod(warning_clock*1.8+speck*.17,1.0)
			var at=Vector2(-8+speck*2.2,12+age*60)
			draw_circle(at,.6+speck%2*.4,Color(.60,.54,.32,(1-age)*amount*.55))
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
