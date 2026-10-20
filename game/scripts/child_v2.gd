extends CharacterBody2D

# Game-space feet remain planted during stance. The stride advances from the
# distance actually travelled, rather than a free-running animation clock.
var game
var is_girl=true
var controlled=true
var following=true
var facing=1.0
var crouching=false
var forced_crouch=false
var ai_axis=0.0
var ai_jump=false
var leap_axis=0.0
var phase=0.0
var anim_time=0.0
var action_time=0.0
var hit_time=0.0
var land_time=0.0
var hand_active=false
var contact_hand=Vector2.ZERO
var coyote=0.0
var jump_buffer=0.0
var was_floor=false
var foot_lock=[Vector2.ZERO,Vector2.ZERO]
var foot_start=[Vector2.ZERO,Vector2.ZERO]
var foot_phase=[0.0,0.5]
var feet=[Vector2(-10,0),Vector2(10,0)]
var legs=[Vector2.ZERO,Vector2.ZERO]
var last_direction=1.0
var planted_error=0.0
var col:CollisionShape2D
var head_atlas=preload("res://assets/characters/boy_atlas.png")
var girl_profile=preload("res://assets/characters/girl_profile.png")
var step_timer=0.0
var body_lean=0.0
var moving_blend=0.0
var climbing=false
var climb_target=Vector2.ZERO
var climb_clock=0.0
var climb_direction=1.0
var mantle_count=0
var moving_last=false
var pushing=false
var push_blend=0.0
var danger_blend=0.0
var fatigue_blend=0.0
var glance_blend=0.0
var glance_direction=1.0
var takeoff_time=0.0
var cloth_drag=0.0
var cloth_velocity=0.0
var braid_drag=0.0
var previous_horizontal=0.0
var crouch_blend=0.0
var run_blend=0.0
var brake_blend=0.0
var input_axis=0.0
var land_impact=0.0
var idle_settle_clock=0.0
var idle_settle_side=0
var idle_settle_start=Vector2.ZERO
var idle_settle_target=Vector2.ZERO
var standing_probe:RectangleShape2D
var work_blend=0.0
var work_kind=""
var hand_blend=0.0
var smoothed_contact=Vector2.ZERO
var mantle_blend=0.0
var acceleration_lean=0.0
var jump_released=false
var animation_state="idle"
var recoil_blend=0.0
var paint_light=Color.WHITE
var paint_bounce=0.0

func _ready():
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	anim_time=0 if is_girl else .83
	collision_layer=2; collision_mask=1; floor_snap_length=14
	col=CollisionShape2D.new(); col.shape=RectangleShape2D.new(); col.shape.size=Vector2(23,99 if is_girl else 84); col.position.y=-col.shape.size.y/2
	standing_probe=RectangleShape2D.new(); standing_probe.size=col.shape.size
	add_child(col); reset_feet()

func reset_feet():
	for i in range(2):
		foot_lock[i]=position+Vector2(-10 if i==0 else 10,0)
		foot_lock[i].y=surface_height(foot_lock[i].x,position.y)
		foot_start[i]=foot_lock[i]
		feet[i]=(foot_lock[i]-position)/(1.0 if is_girl else .84)
	phase=.26; foot_phase=[.26,.76]
	idle_settle_clock=0

func begin_stride():
	# Keep the support foot in world space when starting or reversing. Resetting
	# both feet to a default spread here made a visible pop at every small turn.
	for i in range(2):
		foot_lock[i]=position+feet[i]*(1.0 if is_girl else .84)
		foot_start[i]=foot_lock[i]
	# Choose the foot already ahead in the new travel direction as support.
	# Keeping an arbitrary side planted through a reversal can strand that foot
	# behind the pelvis for another half stride and overextend the whole leg.
	var support=0 if (feet[0].x-feet[1].x)*facing>=0 else 1
	phase=0.0 if support==0 else .5
	foot_phase=[fposmod(phase,1),fposmod(phase+.5,1)]; idle_settle_clock=0

func can_stand():
	var height=99.0 if is_girl else 84.0
	var query=PhysicsShapeQueryParameters2D.new()
	query.shape=standing_probe; query.transform=Transform2D(0,global_position+Vector2(0,-height/2-.8))
	query.collision_mask=1; query.exclude=[get_rid()]; query.margin=.02
	return get_world_2d().direct_space_state.intersect_shape(query,1).is_empty()

func surface_height(world_x,fallback_y):
	# Flat studies and older chapters do not need to implement this query. The
	# native controller still owns the body; only the sole follows the ground.
	if game!=null and game.has_method("surface_y_at"):
		var result=float(game.surface_y_at(world_x,fallback_y))
		if absf(result-fallback_y)<42.0: return result
	return fallback_y

func update_animation(dt):
	# Simulation owns pose time, including work and impact recovery. A paused
	# game holds the entire pose, and rendering at 30/60/144 Hz cannot change it.
	anim_time+=dt; action_time=maxf(0,action_time-dt); hit_time=maxf(0,hit_time-dt); land_time=maxf(0,land_time-dt); takeoff_time=maxf(0,takeoff_time-dt)
	var acceleration=clampf((velocity.x-previous_horizontal)/maxf(dt,.001)/1250.0,-1,1)
	acceleration_lean=lerpf(acceleration_lean,acceleration,1-exp(-dt*12))
	body_lean=lerpf(body_lean,clampf(velocity.x/100,-3.4,3.4)+acceleration_lean*1.4,1-exp(-dt*9))
	moving_blend=lerpf(moving_blend,clampf(abs(velocity.x)/100,0,1),1-exp(-dt*10))
	run_blend=lerpf(run_blend,clampf((abs(velocity.x)-166)/99,0,1),1-exp(-dt*12))
	var braking=1.0 if input_axis!=0 and velocity.x*input_axis< -30 else 0.0
	brake_blend=lerpf(brake_blend,braking,1-exp(-dt*16))
	push_blend=lerpf(push_blend,1.0 if pushing else 0.0,1-exp(-dt*9))
	work_blend=lerpf(work_blend,1.0 if action_time>0 else 0.0,1-exp(-dt*11))
	recoil_blend=lerpf(recoil_blend,1.0 if hit_time>0 else 0.0,1-exp(-dt*18))
	mantle_blend=lerpf(mantle_blend,1.0 if climbing else 0.0,1-exp(-dt*14))
	if action_time>0 and not game.pending_action.is_empty(): work_kind=str(game.pending_action.kind)
	var was_contact=hand_blend
	hand_blend=lerpf(hand_blend,1.0 if hand_active and not climbing and action_time<=0 else 0.0,1-exp(-dt*12))
	if hand_active:
		if was_contact<.01: smoothed_contact=contact_hand
		else: smoothed_contact=smoothed_contact.lerp(contact_hand,1-exp(-dt*20))
	animation_state="idle"
	if climbing: animation_state="mantle"
	elif hit_time>0: animation_state="recoil"
	elif action_time>0: animation_state="work"
	elif not is_on_floor(): animation_state="rise" if velocity.y< -30 else ("fall" if velocity.y>30 else "apex")
	elif land_time>.10: animation_state="land"
	elif crouching: animation_state="crouch_walk" if absf(velocity.x)>5 else "crouch"
	elif absf(velocity.x)>220: animation_state="run"
	elif absf(velocity.x)>5: animation_state="walk"
	var threat=0.0
	var tired=0.0
	var glance=0.0
	if game!=null:
		threat=maxf(float(game.shell_warning),clampf(float(game.exposure)/1.4,0,1))
		var lane_notice=game.get("lane_warning")
		if lane_notice!=null and not str(lane_notice).is_empty(): threat=maxf(threat,.72)
		tired=maxf(clampf((38-float(game.warmth))/38.0,0,1),clampf((32-float(game.health))/32.0,0,1))
		tired=maxf(tired,float(game.wetness)*.45)
		if controlled: tired=maxf(tired,clampf((24-float(game.stamina))/24.0,0,1)*.6)
		var companion=game.boy if is_girl else game.player
		if is_instance_valid(companion) and game.mode=="playing" and not climbing and action_time<=0:
			var gap=companion.position.x-position.x
			var glance_window=fposmod(anim_time+(0.0 if is_girl else 2.4),7.4)
			# A short look catches the other child after separation, and during a
			# warning. It has a held beat and ease in/out, rather than a head snap.
			if absf(gap)>34 and absf(velocity.x)<215 and (glance_window>5.7 or threat>.35):
				glance=1.0
				glance_direction=signf(gap)
	danger_blend=lerpf(danger_blend,threat,1-exp(-dt*4.5))
	fatigue_blend=lerpf(fatigue_blend,tired,1-exp(-dt*2.0))
	glance_blend=lerpf(glance_blend,glance,1-exp(-dt*5.0))
	# Damped follow-through responds to acceleration as well as the gait.
	var inertia=clampf((velocity.x-previous_horizontal)*.035,-4,4)
	previous_horizontal=velocity.x
	cloth_velocity+=(-body_lean*1.4-cloth_drag)*dt*54-inertia
	cloth_velocity*=exp(-dt*10)
	cloth_drag=clampf(cloth_drag+cloth_velocity*dt,-6,6)
	braid_drag=lerpf(braid_drag,-body_lean*1.7+sin(anim_time*4.6)*.45,1-exp(-dt*5))
	queue_redraw()

func _physics_process(dt):
	if game==null or game.mode!="playing": return
	pushing=false
	var axis=Input.get_axis("left","right") if controlled else ai_axis
	var jump=Input.is_action_just_pressed("jump") if controlled else ai_jump
	if not controlled:
		ai_jump=false
		if not is_on_floor() and leap_axis!=0: axis=leap_axis
		elif is_on_floor() and not jump: leap_axis=0
	crouching=Input.is_action_pressed("crouch") if controlled else forced_crouch
	if not crouching and col.shape.size.y<(99.0 if is_girl else 84.0)-.01 and not can_stand(): crouching=true
	var full_height=99.0 if is_girl else 84.0
	var low_height=74.0 if is_girl else 62.0
	# The shape stays anchored at the soles throughout the transition. Down is
	# fast; rising is slightly slower and waits for actual overhead clearance.
	col.shape.size.y=move_toward(col.shape.size.y,low_height if crouching else full_height,dt*(300 if crouching else 210))
	col.position.y=-col.shape.size.y/2
	crouch_blend=clampf((full_height-col.shape.size.y)/(full_height-low_height),0,1)
	if climbing:
		climb_clock-=dt
		if hit_time>0 or climb_clock<=0 or axis*climb_direction<-.1:
			climbing=false
		else:
			if position.y>climb_target.y: velocity=Vector2(climb_direction*7,-215)
			else: velocity=Vector2(climb_direction*125,-8)
			feet[0]=feet[0].lerp(Vector2(-11*facing,-7),1-exp(-dt*12))
			feet[1]=feet[1].lerp(Vector2(16*facing,-32),1-exp(-dt*12))
			move_and_slide()
			if (position.x-climb_target.x)*climb_direction>=0:
				climbing=false; land_time=.2; reset_feet()
			update_animation(dt)
			return
	var speed=166.0
	var sprinting=controlled and Input.is_action_pressed("sprint") and game.stamina>2 and not crouching and action_time<=0
	if sprinting:
		speed=265
	if not controlled:
		speed=210 if abs(game.player.position.x-position.x)>105 else 172
		if jump or (not is_on_floor() and leap_axis!=0): speed=268
	if crouching: speed=73
	if game.in_water(position.x,position.y): speed*=.61
	speed*=game.wind_speed_scale(self)
	if action_time>0: axis=0; jump=false; leap_axis=0; jump_buffer=0
	input_axis=axis
	var before=position
	var acceleration=1350 if is_on_floor() else 540
	if axis==0 and is_on_floor(): acceleration=1660
	elif axis*velocity.x<0 and is_on_floor(): acceleration=2050
	velocity.x=move_toward(velocity.x,axis*speed,acceleration*dt)
	if abs(axis)>.1 and (axis*velocity.x>=0 or abs(velocity.x)<25): facing=signf(axis)
	if is_on_floor(): coyote=.14
	else: coyote-=dt
	if jump: jump_buffer=.15; jump_released=false
	else: jump_buffer-=dt
	if controlled and not Input.is_action_pressed("jump"): jump_released=true
	var launched=false
	if jump_buffer>0 and coyote>0 and not crouching and action_time<=0:
		velocity.y=-525; jump_buffer=0; coyote=0
		takeoff_time=.18; launched=true
		if not controlled: leap_axis=axis
		if controlled: game.stamina=maxf(0,game.stamina-7)
	velocity.y+=1420*dt
	if controlled and (Input.is_action_just_released("jump") or (launched and jump_released)) and not Input.is_action_pressed("jump") and velocity.y< -170: velocity.y*=.55
	var impact_speed=velocity.y
	move_and_slide()
	if not is_on_floor() and is_on_wall() and velocity.y> -75 and abs(axis)>.1 and not crouching:
		var ledges=game.level.platforms+game.level.ground
		for ledge in ledges:
			var edge=float(ledge.x) if axis>0 else float(ledge.x)+float(ledge.w)
			var reach=position.y-float(ledge.y)
			var destination=Vector2(edge+signf(axis)*22,float(ledge.y)-2)
			if abs(position.x-edge)<18 and reach>10 and reach<86 and mantle_clear(destination):
				climbing=true; climb_clock=1.15; climb_direction=signf(axis); climb_target=Vector2(edge+climb_direction*22,float(ledge.y)-2); mantle_count+=1; break
	if controlled and Input.is_action_pressed("interact") and abs(axis)>.1:
		for i in range(get_slide_collision_count()):
			var body=get_slide_collision(i).get_collider()
			if body is RigidBody2D:
				body.linear_velocity.x=axis*78; pushing=true
	var distance=absf(position.x-before.x)
	if sprinting and absf(velocity.x)>175 and distance>.1: game.stamina=maxf(0,game.stamina-dt*21)
	if is_on_floor():
		if not was_floor:
			land_impact=clampf((impact_speed-100)/500,0,1); land_time=.24; land_feet()
			if impact_speed>170: game.spawn_dust(position,2+int(land_impact*4))
		if abs(velocity.x)>5:
			if not moving_last or facing!=last_direction: begin_stride()
			var stride=lerpf(52,94,clampf(absf(velocity.x)/166,0,1))
			stride=lerpf(stride,110,clampf((abs(velocity.x)-190)/75,0,1))
			if crouching: stride=61.0
			stride*=1.0 if is_girl else .84
			phase+=distance/stride
			for i in range(2):
				var p=fposmod(phase+i*.5,1)
				var stance=.42 if abs(velocity.x)>220 else .50
				var reach=(stride*.22 if not crouching else 18)*(1.0 if is_girl or not crouching else .84)
				if p<stance:
					if foot_phase[i]>=stance:
						foot_lock[i]=Vector2(position.x+facing*reach,surface_height(position.x+facing*reach,position.y)); step(i)
					feet[i]=(foot_lock[i]-position)/(1.0 if is_girl else .84)
				else:
					if foot_phase[i]<stance: foot_start[i]=position+feet[i]*(1.0 if is_girl else .84)
					var u=(p-stance)/(1-stance); var smooth=u*u*(3-2*u)
					var end=Vector2(position.x+facing*reach,surface_height(position.x+facing*reach,position.y))
					feet[i]=(foot_start[i].lerp(end,smooth)-position)/(1.0 if is_girl else .84)
					feet[i].y-=sin(u*PI)*(18 if abs(velocity.x)>220 else 12)
				foot_phase[i]=p
		else:
			var scale_body=1.0 if is_girl else .84
			if moving_last:
				for i in range(2): foot_lock[i]=position+feet[i]*scale_body
				# Set down the swinging foot with a small lifted recovery step.
				# The other sole remains anchored; neither foot glides to an idle pose.
				idle_settle_side=0 if feet[0].y<feet[1].y else 1
				idle_settle_clock=.18; idle_settle_start=foot_lock[idle_settle_side]
				var rest_x=(-9 if idle_settle_side==0 else 9)*scale_body
				idle_settle_target=Vector2(position.x+rest_x,surface_height(position.x+rest_x,position.y))
			if idle_settle_clock>0:
				idle_settle_clock=maxf(0,idle_settle_clock-dt)
				var u=1-idle_settle_clock/.18; var ease=u*u*(3-2*u)
				foot_lock[idle_settle_side]=idle_settle_start.lerp(idle_settle_target,ease)-Vector2(0,sin(u*PI)*4)
			for i in range(2): feet[i]=(foot_lock[i]-position)/scale_body
	else:
		var rising=clampf(-velocity.y/400.0,0,1)
		var falling=clampf(velocity.y/480.0,0,1)
		feet[0]=feet[0].lerp(Vector2((-18+rising*7+falling*6)*facing,-9-rising*15+falling*9),1-exp(-dt*14))
		feet[1]=feet[1].lerp(Vector2((15-falling*8)*facing,-12-rising*21+falling*12),1-exp(-dt*14))
		if climbing:
			feet[0]=feet[0].lerp(Vector2(-11*facing,-5),1-exp(-dt*14)); feet[1]=feet[1].lerp(Vector2(16*facing,-31),1-exp(-dt*14))
	was_floor=is_on_floor(); last_direction=facing; moving_last=abs(velocity.x)>5
	update_animation(dt)

func mantle_clear(destination):
	var height=99.0 if is_girl else 84.0
	var query=PhysicsShapeQueryParameters2D.new()
	query.shape=standing_probe; query.transform=Transform2D(0,destination+Vector2(0,-height/2))
	query.collision_mask=1; query.exclude=[get_rid()]; query.margin=.02
	return get_world_2d().direct_space_state.intersect_shape(query,1).is_empty()

func land_feet():
	# Preserve the landing spread instead of snapping both ankles to an idle
	# template. The subsequent stride/recovery puts down the free foot.
	var scale_body=1.0 if is_girl else .84
	for i in range(2):
		var x=position.x+clampf(feet[i].x,-24,24)*scale_body
		foot_lock[i]=Vector2(x,surface_height(x,position.y))
		foot_start[i]=foot_lock[i]; feet[i]=(foot_lock[i]-position)/scale_body
	phase=.26; foot_phase=[.26,.76]; idle_settle_clock=0

func step(_side):
	game.play_step(position,(-24 if crouching else -20) if controlled else (-32 if crouching else -28))
	if controlled and abs(velocity.x)>210: game.spawn_dust(position,2)

func solve_knee(hip,foot,length_a=25.0,length_b=24.0,bend=1.0):
	var delta=foot-hip; var dist=clampf(delta.length(),.1,length_a+length_b-.05); var axis=delta.normalized()
	var along=(length_a*length_a-length_b*length_b+dist*dist)/(2*dist)
	return hip+axis*along+Vector2(-axis.y,axis.x)*sqrt(maxf(0,length_a*length_a-along*along))*bend

func local_illumination():
	# Preserve the illustration's painted values. The old uniform .2 profile
	# multiply crushed skin, hair and all the brushwork into the same silhouette.
	var chapter_index=clampi(int(game.chapter),0,4) if game!=null else 0
	var ambient=[Color(.98,.96,.88),Color(.88,.94,.97),Color(.88,.93,.98),Color(.87,.94,1.0),Color(.94,.96,.99)][chapter_index]
	paint_bounce=0.0
	if game!=null and not game.level.is_empty():
		for shelter in game.level.get("covers",[]):
			if shelter.kind!="tent": continue
			var delta=position-Vector2(float(shelter.x),float(shelter.get("y",700)))
			var influence=clampf(1-absf(delta.x)/(float(shelter.w)*.5+90),0,1)*clampf(1-absf(delta.y)/145,0,1)
			paint_bounce=maxf(paint_bounce,influence*.5)
		for source in game.level.get("interact",[]):
			if source.kind!="fire": continue
			var delta=position-Vector2(float(source.x),float(source.y))
			var influence=clampf(1-absf(delta.x)/250,0,1)*clampf(1-absf(delta.y)/150,0,1)
			paint_bounce=maxf(paint_bounce,influence)
	return ambient.lerp(Color(1.05,.96,.83),paint_bounce*.8)

func lit_color(color,depth=1.0):
	return Color(color.r*paint_light.r*depth,color.g*paint_light.g*depth,color.b*paint_light.b*depth,color.a)

func painted_colors(points,tint):
	var colors=PackedColorArray()
	for p in points:
		# Restrained warm key / cool fill across the form, over the authored
		# brush lighting. There is no glossy rim or bright outline around it.
		var key=clampf((12-p.x)/30.0,0,1)
		var light=Color(.86,.93,1.0).lerp(Color(1.06,1.02,.94),key)
		colors.append(Color(tint.r*light.r,tint.g*light.g,tint.b*light.b,tint.a))
	return colors

func paint_joint(center,radius,region,tint,texture):
	var outline=PackedVector2Array(); var uv=PackedVector2Array()
	for i in range(12):
		var direction=Vector2(cos(i*TAU/12),sin(i*TAU/12))
		outline.append(center+direction*radius)
		uv.append((region.position+(direction*.5+Vector2(.5,.5))*region.size)/Vector2(texture.get_size()))
	draw_polygon(outline,painted_colors(outline,tint),uv,texture)

func tube(a,b,c,width_a,width_b,width_c,color,material="",depth=1.0):
	var n1=Vector2(-(b-a).y,(b-a).x).normalized(); var n2=Vector2(-(c-b).y,(c-b).x).normalized()
	# Separate convex bone strips cannot fold across themselves at a tightly
	# bent elbow. A single six-point contour could disappear during hand contact.
	var sections=[]
	if a.distance_squared_to(b)>.0001: sections.append({"points":PackedVector2Array([a+n1*width_a,b+n1*width_b,b-n1*width_b,a-n1*width_a]),"upper":true})
	if b.distance_squared_to(c)>.0001: sections.append({"points":PackedVector2Array([b+n2*width_b,c+n2*width_c,c-n2*width_c,b-n2*width_b]),"upper":false})
	for section in sections: draw_colored_polygon(section.points,color)
	draw_circle(a,width_a*.94,color); draw_circle(b,width_b*.94,color); draw_circle(c,width_c*.94,color)
	if not material.is_empty():
		# Only opaque interior paint is sampled. The sleeve/trouser source's
		# transparent cutout edges never become light holes in the moving limbs.
		var texture=girl_profile if material=="stocking" else head_atlas
		var region=Rect2(1042,125,68,315) if material=="sleeve" else (Rect2(640,1100,220,220) if material=="stocking" else Rect2(580,690,72,420))
		var split=(b-a).length()/maxf(.01,(b-a).length()+(c-b).length())
		var tint=lit_color(Color(.99,1.08,1.12,.98) if material=="sleeve" else (Color(.69,.78,.88,.98) if material=="stocking" else Color(.91,.98,1.04,.98)),depth)
		for section in sections:
			var low=0.0 if section.upper else split; var high=split if section.upper else 1.0
			var uv=PackedVector2Array()
			for point in [Vector2(0,low),Vector2(0,high),Vector2(1,high),Vector2(1,low)]: uv.append((region.position+point*region.size)/Vector2(texture.get_size()))
			draw_polygon(section.points,painted_colors(section.points,tint),uv,texture)
		# Cloth continues around the elbow/knee instead of leaving an unpainted
		# dark circular hinge between two illustrated bone sections.
		var joint_region=Rect2(region.position+region.size*Vector2(.22,.38),region.size*Vector2(.56,.22))
		paint_joint(b,width_b*.97,joint_region,tint,texture)
		# A quiet fold catches at the elbow/knee, following the bend rather
		# than painting an unchanging rectangular limb over the anatomy.
		draw_line(b-n2*width_b*.58,b+n2*width_b*.36,Color(.10,.15,.17,.18),.65,true)

func painted_cloth(points,origin,end_y,region,tint):
	var uv=PackedVector2Array()
	for p in points:
		var v=clampf((p.y-origin.y)/maxf(1,end_y-origin.y),0,1)
		var center_x=lerpf(origin.x,body_lean*.65,v)
		var u=clampf((p.x-center_x+18)/36.0,0,1)
		uv.append((region.position+Vector2(u,v)*region.size)/Vector2(head_atlas.get_size()))
	draw_polygon(PackedVector2Array(points),painted_colors(points,tint),uv,head_atlas)

func sole_roll(side):
	var scale_body=1.0 if is_girl else .84
	var world_x=position.x+feet[side].x*scale_body
	var y=position.y+feet[side].y*scale_body
	var slope=atan2(surface_height(world_x+5,y)-surface_height(world_x-5,y),10)
	if not is_on_floor(): return -facing*.16*clampf(-velocity.y/400,0,1)
	var stance=.42 if abs(velocity.x)>220 else .50
	var p=foot_phase[side]
	var roll=0.0
	if moving_blend>.15:
		if p<stance: roll=-facing*pow(clampf((p/stance-.7)/.3,0,1),2)*.20
		else: roll=-facing*sin((p-stance)/(1-stance)*PI)*.20
	return clampf(slope,-.28,.28)+roll

func boot(ankle,color,roll=0.0,depth=1.0):
	var f=facing
	var outline=PackedVector2Array(); var uv=PackedVector2Array()
	var leather=Rect2(845,866,397,309)
	for p in [Vector2(-4.5*f,-8),Vector2(3.5*f,-8),Vector2(4*f,-4),Vector2(9*f,-3),Vector2(12*f,-1),Vector2(12*f,1.5),Vector2(6*f,2.5),Vector2(-5*f,2.5),Vector2(-5*f,-3)]:
		outline.append(ankle+p.rotated(roll))
		uv.append((leather.position+Vector2(clampf((p.x*f+5)/17.0,0,1),clampf((p.y+8)/10.5,0,1))*leather.size)/Vector2(head_atlas.get_size()))
	draw_colored_polygon(outline,lit_color(Color(.22,.17,.13),depth))
	draw_polygon(outline,painted_colors(outline,lit_color(Color(1.04,1.02,.96,.98),depth)),uv,head_atlas)
	draw_polyline(PackedVector2Array([ankle+Vector2(-5*f,1).rotated(roll),ankle+Vector2(6*f,1.5).rotated(roll),ankle+Vector2(11*f,.5).rotated(roll)]),Color(.37,.38,.31,.45),1,true)
	draw_line(ankle+Vector2(-4*f,-7).rotated(roll),ankle+Vector2(3*f,-7).rotated(roll),Color(.48,.47,.39,.35),1.2,true)
	draw_line(ankle+Vector2(3*f,-4).rotated(roll),ankle+Vector2(6*f,-2).rotated(roll),Color(.43,.46,.41,.27),.8,true)

func draw_hand(at,elbow,color,open_hand=false,depth=1.0):
	var direction=(at-elbow).normalized()
	var across=Vector2(-direction.y,direction.x)
	var points=PackedVector2Array([at-direction*2.2-across*2.0,at+direction*3.0-across*1.9,at+direction*4.3-across*.5,at+direction*3.7+across*1.5,at+direction*.5+across*2.2,at-direction*1.8+across*1.7])
	draw_colored_polygon(points,color)
	var skin=Rect2(185,720,35,180); var uv=PackedVector2Array()
	for p in points:
		var relative=p-at
		uv.append((skin.position+Vector2(clampf((relative.dot(across)+2.2)/4.4,0,1),clampf((relative.dot(direction)+2.2)/6.5,0,1))*skin.size)/Vector2(head_atlas.get_size()))
	draw_polygon(points,painted_colors(points,lit_color(Color(.98,.96,.92,.98),depth)),uv,head_atlas)
	draw_line(at-direction,at+direction*1.1+across*3.1,color,1.8,true)
	if open_hand:
		draw_line(at+across*1.0,at+direction*5+across*1.0,color,1.3,true)
		draw_line(at-across*1.0,at+direction*4.4-across*1.0,color,1.2,true)

func body_pose():
	var run=run_blend
	var gait=fposmod(phase,1)*TAU
	var bob=(1-cos(gait*2))*(.7+run*.7)*moving_blend
	var squat=30.0*crouch_blend
	var landing=sin(sqrt(clampf(1-land_time/.24,0,1))*PI)*(1+land_impact*5) if land_time>0 else 0.0
	var airborne=not is_on_floor() and game!=null and game.mode=="playing"
	var rise=clampf(-velocity.y/400,0,1) if airborne else 0.0
	var fall=clampf(velocity.y/500,0,1) if airborne else 0.0
	var weary=fatigue_blend*(1.0-moving_blend*.35)
	var shiver=sin(anim_time*28)*.32*fatigue_blend*(1-moving_blend)
	var hip=Vector2(body_lean*.65-facing*push_blend*4,-45+run*2+squat*.58+bob+landing+push_blend*2)
	var shoulder=Vector2(body_lean*1.5+facing*(weary*2+push_blend*11+rise*2-brake_blend*3),-75+squat+bob+landing+weary*2+push_blend*8+fall*2)
	if takeoff_time>0:
		var extension=sin(takeoff_time/.18*PI)
		shoulder.y-=extension*1.7; hip.y-=extension*.8
	shoulder+=Vector2(facing*12,15)*mantle_blend
	shoulder.x-=facing*4*recoil_blend
	shoulder+=Vector2(facing*7,9)*work_blend
	if work_kind=="fire": hip.y+=9*work_blend; shoulder.y+=10*work_blend
	# A planted ankle is authoritative. Lower the pelvis a little when a long
	# support step would otherwise stretch the shin beyond its authored length.
	var original_hip_y=hip.y
	for i in range(2):
		var dx=feet[i].x-(hip.x+(-2 if i==0 else 2))
		hip.y=maxf(hip.y,feet[i].y-sqrt(maxf(4,51.5*51.5-dx*dx)))
	shoulder.y+=(hip.y-original_hip_y)*.65
	# A compressed work or mantle pose still has a valid length of torso.
	# This also keeps the authored cloth contour simple under fast pose changes.
	shoulder.y=minf(shoulder.y,hip.y-11)
	var breathe=sin(anim_time*(2.8+weary*.7))*(.5+weary*.3)*(1-moving_blend)
	shoulder+=Vector2(shiver+sin(anim_time*.65)*.45*(1-moving_blend),breathe)
	var head=shoulder+Vector2(facing*(1.2+weary*2),-15+weary*1.7+crouch_blend*4)
	var head_facing=facing
	if glance_blend>.55 and glance_direction!=facing: head_facing=glance_direction
	head.x+=head_facing*glance_blend*1.6
	var head_tilt=facing*(-run*.055+weary*.13+fall*.05)-head_facing*glance_blend*.035
	head+=Vector2(facing*2,-1)*mantle_blend+Vector2(-facing*2,1)*recoil_blend
	head_tilt=lerpf(head_tilt,-facing*.12,mantle_blend)
	head_tilt=lerpf(head_tilt,facing*.18,recoil_blend)
	return {"hip":hip,"shoulder":shoulder,"head":head,"head_facing":head_facing,"head_tilt":head_tilt,"rise":rise,"fall":fall,"weary":weary,"airborne":airborne}

func reachable_hand(shoulder,target):
	return shoulder+(target-shoulder).limit_length(30.5)

func _draw():
	paint_light=local_illumination()
	var s=1.0 if is_girl else .84
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	var pose=body_pose()
	var hip=pose.hip; var shoulder=pose.shoulder; var head=pose.head
	var head_facing=pose.head_facing; var head_tilt=pose.head_tilt
	var rise=pose.rise; var fall=pose.fall; var weary=pose.weary; var airborne=pose.airborne
	var run=run_blend; var gait=fposmod(phase,1)*TAU
	var bleak=float(game.chapter)/4.0 if game!=null else 0
	var ink=lit_color(Color(.14,.19,.22)); var far=lit_color(Color(.20,.25,.27),.80); var cloth=lit_color(Color(.24,.31,.33))
	var edge=lit_color(Color(.67,.70,.61))
	for i in range(2):
		var foot=feet[i]; var leg_hip=hip+Vector2(-2 if i==0 else 2,0)
		var knee=solve_knee(leg_hip,foot,27,25.5,-facing)
		legs[i]=knee
		if i==0:
			tube(leg_hip,knee,foot,5.6,4.5,3.3,far,"stocking" if is_girl else "trouser",.78); boot(foot,far,sole_roll(i),.78)
	var arm_swing=sin(gait+PI)*moving_blend*facing
	var far_hand=shoulder+Vector2(arm_swing*(16+run*5),29-run*10)
	if airborne: far_hand=shoulder+Vector2(-facing*(12+rise*3),17-rise*17+fall*2)
	if danger_blend>.1:
		var guard=shoulder+Vector2(-facing*16,13 if is_girl else 7)
		far_hand=far_hand.lerp(guard,danger_blend*.78)
	if weary>.1: far_hand=far_hand.lerp(shoulder+Vector2(facing*8,14),weary*.55)
	if push_blend>.01: far_hand=far_hand.lerp(shoulder+Vector2(facing*26,6),push_blend)
	if work_blend>.01:
		var work_hand=shoulder+Vector2(facing*(20+sin(anim_time*3.8+PI)*3),15+cos(anim_time*3.8)*2)
		if work_kind=="roof": work_hand=shoulder+Vector2(facing*12,-20+sin(anim_time*4+PI)*2)
		elif work_kind=="fire": work_hand=shoulder+Vector2(facing*19,18)
		far_hand=far_hand.lerp(work_hand,work_blend)
	far_hand=far_hand.lerp(shoulder+Vector2(facing*17,-15),mantle_blend)
	far_hand=reachable_hand(shoulder,far_hand)
	var far_elbow=solve_knee(shoulder,far_hand,15,16,facing)
	tube(shoulder+Vector2(-2,2),far_elbow,far_hand,4.5,3.4,2.7,far,"sleeve",.76)
	draw_hand(far_hand,far_elbow,lit_color(Color(.61,.40,.27),.78),push_blend>.4 or climbing,.78)
	var skirt_wind=sin(gait-.65)*moving_blend*2+cloth_drag+rise*facing*2
	var hem=hip.y+(20 if is_girl else 8)
	var body=[shoulder+Vector2(-8,-1),shoulder+Vector2(7,-1),shoulder+Vector2(11,8),hip+Vector2(9,0),Vector2(15+skirt_wind,hem),Vector2(-16+skirt_wind,hem-1),hip+Vector2(-9,0),shoulder+Vector2(-11,8)]
	draw_colored_polygon(PackedVector2Array(body),cloth)
	painted_cloth(body,shoulder,hem,Rect2(557,86,244,448),lit_color(Color(.98,1.09,1.16,.98) if is_girl else Color(1.03,1.08,1.10,.98)))
	# Cloth seams and edge light move with the silhouette, rather than floating
	# pasted body rectangles. The final anatomy is authored for these children.
	draw_polyline(PackedVector2Array([shoulder+Vector2(-8,1),shoulder+Vector2(-10,10),hip+Vector2(-9,0),Vector2(-15+skirt_wind,hem-2)]),Color(edge,.20),.8,true)
	for i in range(3):
		var x=-7+i*7
		draw_line(Vector2(x,hip.y-2),Vector2(x*1.5+skirt_wind,hem-3),Color(.38,.45,.43,.11),.8,true)
	if not is_girl:
		var lapel=PackedVector2Array([shoulder+Vector2(-3,1),shoulder+Vector2(4,2),shoulder+Vector2(3,12),shoulder+Vector2(-1,8)])
		draw_colored_polygon(lapel,Color(.36,.42,.38,.35))
		draw_line(shoulder+Vector2(4,12),hip+Vector2(4,3),Color(edge,.23),1,true)
		for i in range(3): draw_circle(shoulder+Vector2(5,11+i*7),.9,Color("7e8070"))
		# Worn knee cloth and a small pocket keep the boy's coat distinct from
		# his sister's long skirt without introducing a generic adult costume.
		draw_colored_polygon(PackedVector2Array([hip+Vector2(-7,-5),hip+Vector2(-1,-5),hip+Vector2(-1,1),hip+Vector2(-6,2)]),Color(.14,.20,.21))
	var foot=feet[1]; var near_hip=hip+Vector2(2,0); var knee=legs[1]
	tube(near_hip,knee,foot,5.6,4.5,3.1,ink,"stocking" if is_girl else "trouser"); boot(foot,ink,sole_roll(1))
	if is_girl:
		# The dress is in front of the thighs and has a stable, sculpted hem.
		var hem_shape=PackedVector2Array([hip+Vector2(-10,-4),hip+Vector2(10,-4),Vector2(16+skirt_wind,hem),Vector2(-17+skirt_wind,hem-1)])
		draw_colored_polygon(hem_shape,cloth)
		painted_cloth(hem_shape,hip+Vector2(0,-4),hem,Rect2(546,330,247,210),lit_color(Color(.94,1.08,1.16,.98)))
		draw_line(Vector2(-16+skirt_wind,hem-2),Vector2(15+skirt_wind,hem-1),Color(edge,.25),1,true)
		draw_line(hip+Vector2(-9,-2),hip+Vector2(8,-2),Color(.44,.47,.40,.32),1.2,true)
		var patch=Vector2(-8+skirt_wind*.7,hem-8)
		draw_colored_polygon(PackedVector2Array([patch+Vector2(-3,-3),patch+Vector2(3,-2),patch+Vector2(2,4),patch+Vector2(-3,3)]),Color(.23,.30,.29,.7))
		draw_line(patch+Vector2(-2,-2),patch+Vector2(-2,3),Color(.55,.56,.46,.25),.7,true)
	draw_line(shoulder+Vector2(0,-2),head+Vector2(0,6),lit_color(Color(.50,.32,.20)),6,true)
	draw_set_transform(head*s,head_tilt,Vector2(s*head_facing,s))
	var profile_tint=lit_color(Color(.96,.97,.95))
	if is_girl: draw_texture_rect_region(girl_profile,Rect2(-19,-17,34,32),Rect2(30,15,1135,1000),profile_tint)
	else: draw_texture_rect_region(head_atlas,Rect2(-15,-17,31,34),Rect2(0,0,440,490),profile_tint)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	if is_girl:
		var braid=head+Vector2(-9*head_facing,4)
		for i in range(6):
			var wind=sin(anim_time*5-i*.4)*(.3+run*.8)+braid_drag*(float(i)+1)/6.0
			var center=braid+Vector2(wind,5+i*3.2)
			draw_circle(center,3.3-i*.16,lit_color(Color(.13,.12,.11)))
			paint_joint(center,3.3-i*.16,Rect2(370,270,60,120),lit_color(Color(.97,.98,1.02)),girl_profile)
		var ribbon=braid+Vector2(braid_drag,23)
		draw_colored_polygon(PackedVector2Array([ribbon,ribbon+Vector2(-head_facing*5,-2),ribbon+Vector2(-head_facing*4,3),ribbon+Vector2(head_facing*3,2),ribbon+Vector2(head_facing*4,-2)]),Color("5e8291"))
		draw_line(ribbon,ribbon+Vector2(-head_facing*8+cloth_drag*.3,4+sin(anim_time*5)*1.3),Color("658d9b"),2.0,true)
		draw_line(ribbon,ribbon+Vector2(-head_facing*4,8),Color("537d91"),1.6,true)
	var hand=shoulder+Vector2(-arm_swing*(16+run*5),29-run*10)
	hand=hand.lerp(shoulder+Vector2(facing*22,9),crouch_blend)
	if airborne: hand=shoulder+Vector2(facing*(13+fall*5),10-rise*18)
	if danger_blend>.1 and not hand_active:
		var shelter_hand=shoulder+Vector2(facing*17,-7) if crouching else shoulder+Vector2(-facing*13,18)
		hand=hand.lerp(shelter_hand,danger_blend*.8)
	if weary>.1 and not crouching: hand=hand.lerp(shoulder+Vector2(facing*10,15),weary*.52)
	if push_blend>.01: hand=hand.lerp(shoulder+Vector2(facing*27,10),push_blend)
	if work_blend>.01:
		var work_hand=shoulder+Vector2(facing*24,13)
		if work_kind in ["wheel","pump","bridge","relay"]: work_hand=shoulder+Vector2(facing*(24+sin(anim_time*3.8)*3),6+cos(anim_time*3.8)*3)
		elif work_kind=="roof": work_hand=shoulder+Vector2(facing*18,-18+sin(anim_time*4)*2)
		elif work_kind in ["clear","brace"]: work_hand=shoulder+Vector2(facing*(22+sin(anim_time*2.7)*2),15+cos(anim_time*2.7)*2)
		elif work_kind=="fire": work_hand=shoulder+Vector2(facing*22,17)
		hand=hand.lerp(work_hand,work_blend)
	hand=hand.lerp(shoulder+Vector2(facing*17,-15),mantle_blend)
	if hand_blend>.001: hand=hand.lerp(to_local(smoothed_contact)/s,hand_blend)
	hand=reachable_hand(shoulder,hand)
	var elbow=solve_knee(shoulder,hand,15,16,-facing)
	tube(shoulder+Vector2(1,3),elbow,hand,4.6,3.5,2.5,ink,"sleeve")
	draw_line(shoulder+Vector2(-2,3),elbow+Vector2(-1,0),Color(edge,.20),1,true)
	draw_hand(hand,elbow,lit_color(Color(.67,.43,.28)),climbing or push_blend>.4 or danger_blend>.45)
	# The sleeve cuff ends at the wrist, letting a small hand read separately.
	var cuff=(hand-elbow).normalized()
	var cuff_cross=Vector2(-cuff.y,cuff.x)
	draw_line(hand-cuff*3+cuff_cross*2.7,hand-cuff*3-cuff_cross*2.7,Color(edge,.29),1.2,true)
	# Small folded linen collar; no oversized pale patch or bright eyes.
	draw_colored_polygon(PackedVector2Array([shoulder+Vector2(-3,-1),shoulder+Vector2(6,1),shoulder+Vector2(3,5)]),lit_color(Color(.69,.68,.56,.88)))
	draw_set_transform(Vector2.ZERO)
