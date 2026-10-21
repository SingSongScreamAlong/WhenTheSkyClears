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
var girl_cloth:Texture2D
var work_clock=0.0
var work_contacts={}
var work_signature=""
var cold_blend=0.0
var care_blend=0.0
var care_target=Vector2.ZERO
var landing_approach=0.0
var turn_time=0.0
var pose_facing=1.0
var boy_cloth:Texture2D
var protect_blend=0.0
var protect_direction=-1.0
var steady_target=Vector2.ZERO
var steady_reachable=false
var stance_load=0.0
var previous_crouch=0.0
var held_contact_snapshot={}
var head_angles:Texture2D
var head_yaw=1.0
var head_goal=1.0
var head_from=1.0
var head_request=1.0
var head_request_clock=0.0
var head_turn_elapsed=.34
var head_turn_count=0
var last_work_shoulder=Vector2.ZERO
var last_work_hip=Vector2.ZERO
var support_delta=Vector2.ZERO

func _ready():
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	if ResourceLoader.exists("res://assets/characters/girl_cloth_v042.png"):
		girl_cloth=load("res://assets/characters/girl_cloth_v042.png")
	if ResourceLoader.exists("res://assets/characters/boy_cloth_v043.png"):
		boy_cloth=load("res://assets/characters/boy_cloth_v043.png")
	if ResourceLoader.exists("res://assets/characters/head_angles_v044.png"):
		head_angles=load("res://assets/characters/head_angles_v044.png")
	head_yaw=facing; head_goal=facing; head_from=facing; head_request=facing
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
	work_contacts={}
	if game!=null and game.has_method("character_work_contacts") and is_on_floor() and not climbing:
		var contacts=game.character_work_contacts(self)
		if contacts is Dictionary: work_contacts=contacts
	var external_weight=clampf(float(work_contacts.get("weight",1.0)),0,1) if work_contacts.has("kind") else 0.0
	var working=action_time>0 or external_weight>0
	var next_kind=str(work_contacts.get("kind",game.pending_action.get("kind",work_kind))) if working else work_kind
	var signature=next_kind+":"+str(game.pending_action.get("id",""))
	if working and signature!=work_signature:
		work_clock=0; work_signature=signature; last_work_shoulder=Vector2.ZERO; last_work_hip=Vector2.ZERO
	if working: work_clock+=dt; work_kind=next_kind
	work_blend=lerpf(work_blend,maxf(1.0 if action_time>0 else 0.0,external_weight),1-exp(-dt*11))
	recoil_blend=lerpf(recoil_blend,1.0 if hit_time>0 else 0.0,1-exp(-dt*18))
	mantle_blend=lerpf(mantle_blend,1.0 if climbing else 0.0,1-exp(-dt*14))
	turn_time=maxf(0,turn_time-dt)
	if facing!=pose_facing: turn_time=.20; pose_facing=facing
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
	var cold=0.0
	var care=0.0
	var protect=0.0
	steady_reachable=false
	var stance_change=absf(crouch_blend-previous_crouch)/maxf(dt,.001)
	stance_load=lerpf(stance_load,clampf(stance_change/8.0,0,1),1-exp(-dt*13))
	previous_crouch=crouch_blend
	if game!=null:
		threat=maxf(float(game.shell_warning),clampf(float(game.exposure)/1.4,0,1))
		var lane_notice=game.get("lane_warning")
		if lane_notice!=null and not str(lane_notice).is_empty(): threat=maxf(threat,.72)
		tired=maxf(clampf((38-float(game.warmth))/38.0,0,1),clampf((32-float(game.health))/32.0,0,1))
		tired=maxf(tired,float(game.wetness)*.45)
		cold=maxf(clampf((40-float(game.warmth))/40.0,0,1),float(game.wetness)*.6)
		if controlled: tired=maxf(tired,clampf((24-float(game.stamina))/24.0,0,1)*.6)
		var companion=game.boy if is_girl else game.player
		if is_instance_valid(companion) and not climbing and action_time<=0 and external_weight<=0:
			var gap=companion.position-position
			var separation=clampf((absf(gap.x)-68)/95.0,0,1)
			var under_cover=game.is_covered(self) if game.has_method("is_covered") else false
			var grounded=is_on_floor() and absf(gap.y)<38
			if is_girl and grounded and absf(velocity.x)<150:
				protect=maxf(threat*(.9 if crouching or under_cover else .4),separation*(.55 if under_cover else .25))
				protect_direction=signf(gap.x) if absf(gap.x)>4 else -facing
				var companion_height=float(companion.col.shape.size.y)
				steady_target=companion.global_position+Vector2(-protect_direction*8,-companion_height*.62)
				steady_reachable=absf(gap.x)<44 and absf(gap.y)<18
		if is_girl and is_instance_valid(companion) and is_on_floor() and absf(velocity.x)<8 and action_time<=0 and external_weight<=0 and not climbing:
			var gap=companion.position-position
			var care_beat=fposmod(anim_time,11.8)
			if absf(gap.x)>18 and absf(gap.x)<43 and absf(gap.y)<16 and threat<.25 and (tired>.25 or float(game.health)<65) and care_beat>7.3 and care_beat<9.0:
				care=sin((care_beat-7.3)/1.7*PI)
				care_target=companion.global_position+Vector2(signf(-gap.x)*9,-float(companion.col.shape.size.y)*.68)
		if is_instance_valid(companion) and game.mode=="playing" and not climbing and action_time<=0:
			var gap=companion.position.x-position.x
			# Attention follows a real separation or warning. Quiet idle does not
			# repeat a timed checking gesture when both children are already safe.
			if absf(gap)>34 and absf(velocity.x)<185 and (absf(gap)>82 or threat>.35):
				glance=1.0
				glance_direction=signf(gap)
	danger_blend=lerpf(danger_blend,threat,1-exp(-dt*4.5))
	fatigue_blend=lerpf(fatigue_blend,tired,1-exp(-dt*2.0))
	cold_blend=lerpf(cold_blend,cold,1-exp(-dt*3))
	care_blend=lerpf(care_blend,care,1-exp(-dt*7))
	protect_blend=lerpf(protect_blend,protect,1-exp(-dt*7))
	glance_blend=lerpf(glance_blend,glance,1-exp(-dt*5.0))
	update_head_attention(dt)
	var approaching=0.0
	if not is_on_floor() and velocity.y>90 and not climbing:
		var ray=PhysicsRayQueryParameters2D.create(global_position+Vector2(0,2),global_position+Vector2(0,112),1,[get_rid()])
		var ground=get_world_2d().direct_space_state.intersect_ray(ray)
		if not ground.is_empty(): approaching=clampf(1-global_position.distance_to(ground.position)/105.0,0,1)*clampf(velocity.y/350,0,1)
	landing_approach=lerpf(landing_approach,approaching,1-exp(-dt*17))
	# Damped follow-through responds to acceleration as well as the gait.
	var inertia=clampf((velocity.x-previous_horizontal)*.035,-4,4)
	previous_horizontal=velocity.x
	cloth_velocity+=(-body_lean*1.4-cloth_drag)*dt*54-inertia
	cloth_velocity*=exp(-dt*10)
	cloth_drag=clampf(cloth_drag+cloth_velocity*dt,-6,6)
	braid_drag=lerpf(braid_drag,-body_lean*1.7+sin(anim_time*4.6)*.45,1-exp(-dt*5))
	if work_blend>.001 and (work_contacts.has("near") or work_contacts.has("far")):
		var pose=body_pose()
		last_work_shoulder=pose.contact_shoulder/maxf(.001,work_blend)
		last_work_hip=pose.contact_hip/maxf(.001,work_blend)
	queue_redraw()

func desired_head_direction():
	var direction=facing
	if glance_blend>.55 and glance_direction!=facing: direction=glance_direction
	if brake_blend>.30 and input_axis!=0: direction=signf(input_axis)
	if care_blend>.20: direction=signf(care_target.x-global_position.x)
	if protect_blend>.28 and is_girl: direction=protect_direction
	if work_contacts.has("look") and work_blend>.25:
		var look=work_contacts.look-global_position
		if absf(look.x)>5: direction=signf(look.x)
	return direction

func update_head_attention(dt):
	var request=desired_head_direction()
	if request!=head_request: head_request=request; head_request_clock=0.0
	else: head_request_clock+=dt
	if request!=head_goal and head_request_clock>=.035:
		head_from=head_yaw; head_goal=request; head_turn_elapsed=0.0; head_turn_count+=1
	head_turn_elapsed=minf(.34,head_turn_elapsed+dt)
	# A held anticipation beat precedes the drawn quarter/front turn. Rapid
	# retargets start from the presented angle instead of flipping a profile.
	var u=clampf((head_turn_elapsed-.055)/.265,0,1)
	var eased=u*u*(3-2*u)
	head_yaw=lerpf(head_from,head_goal,eased)

func head_render_profile():
	var angle=absf(head_yaw)
	# Opaque drawn angle changes sit on the continuous neck turn. Blending two
	# translucent portraits would ghost the eyes and reveal the background.
	var profile=1.0 if angle>=.76 else 0.0
	var quarter=1.0 if angle>=.24 and angle<.76 else 0.0
	var front=1.0 if angle<.24 else 0.0
	return {"profile":profile,"quarter":quarter,"front":front,"yaw":head_yaw}

func draw_painted_head(pose,scale_body):
	var mix=head_render_profile(); var tint=lit_color(Color(.96,.97,.95))
	var direction=-1.0 if head_yaw<0 else 1.0
	if head_angles==null: mix={"profile":1.0,"quarter":0.0,"front":0.0}
	draw_set_transform(pose.head*scale_body,pose.head_tilt,Vector2(scale_body*direction,scale_body))
	if mix.profile>.001:
		var color=Color(tint,tint.a*mix.profile)
		if is_girl: draw_texture_rect_region(girl_profile,Rect2(-19,-17,34,32),Rect2(30,15,1135,1000),color)
		else: draw_texture_rect_region(head_atlas,Rect2(-15,-17,31,34),Rect2(0,0,440,490),color)
	if head_angles!=null and mix.quarter>.001:
		var source=Rect2(38,11,614,616) if is_girl else Rect2(54,629,595,576)
		var target=Rect2(-16.5,-17,32.5,32) if is_girl else Rect2(-17,-17,34,34)
		draw_texture_rect_region(head_angles,target,source,Color(tint,tint.a*mix.quarter))
	if head_angles!=null and mix.front>.001:
		draw_set_transform(pose.head*scale_body,pose.head_tilt,Vector2(scale_body,scale_body))
		var source=Rect2(664,23,556,610) if is_girl else Rect2(676,639,548,580)
		var target=Rect2(-15,-17,30,32) if is_girl else Rect2(-16,-17,32,34)
		draw_texture_rect_region(head_angles,target,source,Color(tint,tint.a*mix.front))
	draw_set_transform(Vector2.ZERO,0,Vector2(scale_body,scale_body))

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
	var supported_before=is_on_floor()
	support_delta=Vector2.ZERO
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
	if supported_before and is_on_floor():
		# Native platform transport moves the body before its own velocity.
		# Carry the drawn support anchors with that same contact motion.
		support_delta=get_platform_velocity()*dt
		if not support_delta.is_zero_approx():
			for i in range(2): foot_lock[i]+=support_delta; foot_start[i]+=support_delta
			idle_settle_start+=support_delta; idle_settle_target+=support_delta
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
			if body is RigidBody2D and not bool(body.get_meta("mechanism_drive_only",false)):
				body.linear_velocity.x=axis*78; pushing=true
	var distance=absf(position.x-before.x-support_delta.x)
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

func soft_contour(points,amount=.8):
	# Round the silhouette geometrically; the painted texture remains crisp.
	# The cut stays inside each adjacent edge, even on a compressed coat fold.
	var result=PackedVector2Array()
	for index in range(points.size()):
		var at=points[index]; var previous=points[(index+points.size()-1)%points.size()]; var next=points[(index+1)%points.size()]
		var cut=minf(amount,minf(at.distance_to(previous),at.distance_to(next))*.22)
		var enter=at.move_toward(previous,cut); var leave=at.move_toward(next,cut)
		result.append(enter)
		for step in [1,2,3]:
			var t=step/3.0
			result.append(enter.lerp(at,t).lerp(at.lerp(leave,t),t))
	return result

func limb_strip(a,b,width_a,width_b):
	var normal=Vector2(-(b-a).y,(b-a).x).normalized()
	var middle=(a+b)*.5
	var fullness=(width_a+width_b)*.5+.38
	return soft_contour(PackedVector2Array([a+normal*width_a,middle+normal*fullness,b+normal*width_b,b-normal*width_b,middle-normal*fullness,a-normal*width_a]),.65)

func tube(a,b,c,width_a,width_b,width_c,color,material="",depth=1.0):
	var n1=Vector2(-(b-a).y,(b-a).x).normalized(); var n2=Vector2(-(c-b).y,(c-b).x).normalized()
	# Separate convex bone strips cannot fold across themselves at a tightly
	# bent elbow. A single six-point contour could disappear during hand contact.
	var sections=[]
	if a.distance_squared_to(b)>.0001: sections.append({"points":limb_strip(a,b,width_a,width_b),"upper":true,"start":a,"end":b,"wide":width_a,"narrow":width_b})
	if b.distance_squared_to(c)>.0001: sections.append({"points":limb_strip(b,c,width_b,width_c),"upper":false,"start":b,"end":c,"wide":width_b,"narrow":width_c})
	for section in sections: draw_colored_polygon(section.points,color)
	draw_circle(a,width_a*.94,color); draw_circle(b,width_b*.94,color); draw_circle(c,width_c*.94,color)
	if not material.is_empty():
		# Only opaque interior paint is sampled. The sleeve/trouser source's
		# transparent cutout edges never become light holes in the moving limbs.
		var texture=girl_profile if material=="stocking" else head_atlas
		var region=Rect2(1042,125,68,315) if material=="sleeve" else (Rect2(640,1100,220,220) if material=="stocking" else Rect2(580,690,72,420))
		var split=(b-a).length()/maxf(.01,(b-a).length()+(c-b).length())
		var tint=lit_color(Color(.99,1.08,1.12,.98) if material=="sleeve" else (Color(.69,.78,.88,.98) if material=="stocking" else Color(.91,.98,1.04,.98)),depth)
		var dedicated=is_girl and material=="sleeve" and girl_cloth!=null
		if dedicated: texture=girl_cloth; tint=lit_color(Color(.97,1.01,1.02,.99),depth)
		var boy_material=not is_girl and boy_cloth!=null and material in ["sleeve","trouser"]
		if boy_material:
			texture=boy_cloth
			tint=lit_color(Color(.97,1.01,1.03,.99) if material=="sleeve" else Color(.86,.93,.83,.99),depth)
		for section in sections:
			var low=0.0 if section.upper else split; var high=split if section.upper else 1.0
			var source=region
			if dedicated:
				source=Rect2(884,180,115,180) if section.upper else Rect2(310,755,85,130)
				low=0; high=1
			if boy_material:
				source=(Rect2(868,184,120,360) if section.upper else Rect2(351,760,101,373)) if material=="sleeve" else Rect2(867,756,133,422)
				if material=="sleeve": low=0; high=1
			var uv=PackedVector2Array()
			var axis=(section.end-section.start).normalized(); var normal=Vector2(-axis.y,axis.x)
			var length=maxf(.01,section.start.distance_to(section.end))
			for point in section.points:
				var along=clampf((point-section.start).dot(axis)/length,0,1)
				var width=lerpf(float(section.wide),float(section.narrow),along)+sin(along*PI)*.38
				var across=clampf(.5-(point-section.start).dot(normal)/maxf(.1,width)*.5,0,1)
				uv.append((source.position+Vector2(across,lerpf(low,high,along))*source.size)/Vector2(texture.get_size()))
			draw_polygon(section.points,painted_colors(section.points,tint),uv,texture)
			var edge_normal=n1 if section.upper else n2
			var start=a if section.upper else b; var end=b if section.upper else c
			var width=width_a if section.upper else width_b
			draw_line(start-edge_normal*width*.68,start.lerp(end,.86)-edge_normal*width*.58,Color(.09,.13,.14,.16*depth),.9,true)
		# Cloth continues around the elbow/knee instead of leaving an unpainted
		# dark circular hinge between two illustrated bone sections.
		var joint_region=Rect2(region.position+region.size*Vector2(.22,.38),region.size*Vector2(.56,.22))
		if dedicated: joint_region=Rect2(900,230,60,75)
		if boy_material: joint_region=Rect2(915,411,68,91) if material=="sleeve" else Rect2(902,979,70,91)
		paint_joint(b,width_b*.97,joint_region,tint,texture)
		# A quiet fold catches at the elbow/knee, following the bend rather
		# than painting an unchanging rectangular limb over the anatomy.
		draw_line(b-n2*width_b*.58,b+n2*width_b*.36,Color(.10,.15,.17,.18),.65,true)

func painted_cloth(points,origin,end_y,region,tint,texture=null):
	if texture==null: texture=head_atlas
	var uv=PackedVector2Array()
	for p in points:
		var v=clampf((p.y-origin.y)/maxf(1,end_y-origin.y),0,1)
		var center_x=lerpf(origin.x,body_lean*.65,v)
		var u=clampf(((p.x-center_x)*facing+18)/36.0,0,1)
		uv.append((region.position+Vector2(u,v)*region.size)/Vector2(texture.get_size()))
	draw_polygon(PackedVector2Array(points),painted_colors(points,tint),uv,texture)

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
	var texture=girl_cloth if girl_cloth!=null else head_atlas
	if texture==girl_cloth: leather=Rect2(710,817,499,389)
	for p in [Vector2(-4.5*f,-8),Vector2(3.5*f,-8),Vector2(4*f,-4),Vector2(9*f,-3),Vector2(12*f,-1),Vector2(12*f,1.5),Vector2(6*f,2.5),Vector2(-5*f,2.5),Vector2(-5*f,-3)]:
		outline.append(ankle+p.rotated(roll))
		uv.append((leather.position+Vector2(clampf((p.x*f+5)/17.0,0,1),clampf((p.y+8)/10.5,0,1))*leather.size)/Vector2(texture.get_size()))
	draw_colored_polygon(outline,lit_color(Color(.22,.17,.13),depth))
	draw_polygon(outline,painted_colors(outline,lit_color(Color(1.00,.99,.96,.98),depth)),uv,texture)
	draw_polyline(PackedVector2Array([ankle+Vector2(-5*f,1).rotated(roll),ankle+Vector2(6*f,1.5).rotated(roll),ankle+Vector2(11*f,.5).rotated(roll)]),Color(.37,.38,.31,.45),1,true)
	draw_line(ankle+Vector2(-4*f,-7).rotated(roll),ankle+Vector2(3*f,-7).rotated(roll),Color(.48,.47,.39,.35),1.2,true)
	draw_line(ankle+Vector2(3*f,-4).rotated(roll),ankle+Vector2(6*f,-2).rotated(roll),Color(.43,.46,.41,.27),.8,true)

func draw_hand(at,elbow,color,open_hand=false,depth=1.0):
	var direction=(at-elbow).normalized()
	var across=Vector2(-direction.y,direction.x)
	var points=soft_contour(PackedVector2Array([at-direction*2.2-across*2.0,at+direction*3.0-across*1.9,at+direction*4.3-across*.5,at+direction*3.7+across*1.5,at+direction*.5+across*2.2,at-direction*1.8+across*1.7]),.3)
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

func work_profile():
	# Each task has a different line of effort. External mechanism contacts
	# replace these grips, while these offsets still carry weight through hips.
	var f=facing
	var drive=.5-.5*cos(work_clock*5.2)
	var p={"hip":Vector2.ZERO,"shoulder":Vector2(f*5,3),"near":Vector2(f*23,10),"far":Vector2(f*12,19),"nod":.05}
	match work_kind:
		"pump":
			p.hip=Vector2(-f*2,1+drive*2); p.shoulder=Vector2(f*(5+drive*3),3+drive*5)
			p.near=Vector2(f*25,5+drive*8); p.far=Vector2(f*20,11+drive*6); p.nod=.05+drive*.08
		"wheel":
			p.hip=Vector2(-f*2,2); p.shoulder=Vector2(f*(6+sin(work_clock*4)*2),5)
			p.near=Vector2(f*(23+sin(work_clock*4)*4),8+cos(work_clock*4)*7)
			p.far=Vector2(f*(21-sin(work_clock*4)*4),8-cos(work_clock*4)*7)
		"relay","bridge","repair":
			p.hip=Vector2(-f*3,4); p.shoulder=Vector2(f*9,8+sin(work_clock*2.3)*.8)
			p.near=Vector2(f*26,5); p.far=Vector2(f*22,12); p.nod=.10
		"balance_hold":
			p.hip=Vector2(-f*2,1); p.shoulder=Vector2(-f*4,2+sin(work_clock*2.1)*.4)
			p.near=Vector2(f*16,13); p.far=Vector2(f*10,11); p.nod=-.025
		"winch","freight_winch":
			p.hip=Vector2(-f*3,2); p.shoulder=Vector2(f*3,-1+sin(work_clock*2.6)*.45)
			p.near=Vector2(f*17,7); p.far=Vector2(f*16,3); p.nod=.015
		"cart_push":
			p.hip=Vector2(-f*3,4); p.shoulder=Vector2(-f*6,4)
			p.near=Vector2(f*18,7); p.far=Vector2(f*17,4); p.nod=-.015
		"roof","brace":
			p.hip=Vector2(-f*2,1); p.shoulder=Vector2(f*4,-2+sin(work_clock*2.1)*.6)
			p.near=Vector2(f*17,-22); p.far=Vector2(f*8,-19); p.nod=-.15
		"clear":
			p.hip=Vector2(-f*3,8); p.shoulder=Vector2(f*12,17+sin(work_clock*2.7)*1.4)
			p.near=Vector2(f*(23+sin(work_clock*2.7)*2),16); p.far=Vector2(f*14,22); p.nod=.17
		"cache":
			p.hip=Vector2(-f*2,8); p.shoulder=Vector2(f*10,19)
			p.near=Vector2(f*(17+sin(work_clock*4.1)*3),25); p.far=Vector2(-f*6,26); p.nod=.22
		"fire":
			p.hip=Vector2(-f,12); p.shoulder=Vector2(f*4,16)
			var rub=sin(work_clock*3.0)*1.5
			p.near=Vector2(f*(18+rub),15); p.far=Vector2(f*(13-rub),18); p.nod=.12
	return p

func body_pose():
	# Mechanism artwork advances at render rate; read its current geometry for
	# this whole pose instead of carrying a physics-step-old grip into drawing.
	# This is read-only: clocks, blends, feet and the controller stay in physics.
	var contacts=current_work_contacts()
	var run=run_blend
	var gait=fposmod(phase,1)*TAU
	var bob=(1-cos(gait*2))*(.7+run*.7)*moving_blend
	var stance=1-pow(1-crouch_blend,1.12)
	var squat=30.0*stance
	var landing=sin(sqrt(clampf(1-land_time/.24,0,1))*PI)*(1+land_impact*6.2) if land_time>0 else 0.0
	var airborne=not is_on_floor() and game!=null and game.mode=="playing"
	var rise=clampf(-velocity.y/400,0,1) if airborne else 0.0
	var fall=clampf(velocity.y/500,0,1) if airborne else 0.0
	var weary=fatigue_blend*(1.0-moving_blend*.35)
	var shiver=sin(anim_time*28)*.18*cold_blend*(1-moving_blend)
	var twist=sin(gait)*moving_blend*(.7+run*1.2)
	var pushing_weight=push_blend*(1-work_blend*.8) if work_kind=="cart_push" else push_blend
	var turn=sin(clampf(1-turn_time/.20,0,1)*PI) if turn_time>0 else 0.0
	var hip=Vector2(body_lean*.65-facing*pushing_weight*4-facing*(twist*.45+stance*2.5+turn),-45+run*2+squat*.58+bob+landing+pushing_weight*2+landing_approach*3+stance_load*1.8)
	var shoulder=Vector2(body_lean*1.5+facing*(weary*2+pushing_weight*11+rise*2-brake_blend*4+twist+stance*4-turn*1.6),-75+squat+bob+landing*1.18+weary*2+pushing_weight*8+fall*2+landing_approach*4.5+stance_load*1.3+turn*.7)
	if takeoff_time>0:
		var extension=sin(takeoff_time/.18*PI)
		shoulder+=Vector2(facing*2,-3.8)*extension; hip.y-=extension*2
	shoulder+=Vector2(facing*12,15)*mantle_blend
	shoulder.x-=facing*4*recoil_blend
	var work=work_profile()
	hip+=work.hip*work_blend; shoulder+=work.shoulder*work_blend
	var contact_shoulder=Vector2.ZERO; var contact_hip=Vector2.ZERO
	if work_blend>.001 and (contacts.has("near") or contacts.has("far")):
		var contact_origin=shoulder
		var target=Vector2.ZERO; var targets=0
		var scale_body=1.0 if is_girl else .84
		for grip in ["near","far"]:
			if contacts.has(grip): target+=to_local(contacts[grip])/scale_body; targets+=1
		target/=maxi(1,targets)
		if work_kind in ["cart_push","winch","freight_winch"]:
			# The chassis stops the feet close to its rear handle. Keep the
			# chest behind that real grip; leaning past it folds the elbow up
			# across the face even though the fingers remain correctly placed.
			var ahead=(shoulder.x-(target.x-facing*12.5))*facing
			shoulder.x-=facing*maxf(0,ahead)*work_blend
		var reach=target-shoulder
		var effort=(reach-reach.limit_length(24.5)).limit_length(28)
		# A small child bends through the waist to follow a low lever instead
		# of silently stretching the forearm or detaching the fingers from it.
		shoulder+=effort*work_blend
		contact_shoulder=shoulder-contact_origin
		contact_hip=Vector2(effort.x*.24,maxf(0,effort.y)*.48)*work_blend
		hip+=contact_hip
	elif work_blend>.001:
		# A released grip lets the loaded torso settle through its last effort
		# instead of losing the reach displacement in a single render frame.
		contact_shoulder=last_work_shoulder*work_blend; contact_hip=last_work_hip*work_blend
		shoulder+=contact_shoulder; hip+=contact_hip
	shoulder+=Vector2(signf(care_target.x-global_position.x)*3,3)*care_blend
	shoulder+=Vector2(protect_direction*2,1.2)*protect_blend*(1-work_blend)
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
	var head=shoulder+Vector2(head_yaw*(1.2+weary*2),-15+weary*1.7+crouch_blend*4)
	var head_facing=-1.0 if head_yaw<0 else 1.0
	var attention=sin(clampf(head_turn_elapsed/.34,0,1)*PI) if head_turn_elapsed<.34 else 0.0
	head+=Vector2(head_goal*attention*.9,attention*.55)
	head.x+=head_yaw*glance_blend*1.6
	var head_tilt=facing*(-run*.055+weary*.13+fall*.05)-head_facing*glance_blend*.035
	head_tilt+=facing*(landing_approach*.09+landing*.015)+head_goal*attention*.035
	head_tilt=lerpf(head_tilt,head_facing*work.nod,work_blend)
	if work_kind=="balance_hold":
		# Keep the face behind a high physical rail while the arms brace ahead.
		head+=Vector2(-facing*6,1.2)*work_blend
		head_tilt-=facing*.035*work_blend
	head_tilt=lerpf(head_tilt,-head_facing*.06,care_blend)
	head+=Vector2(0,danger_blend*1.8*(1-work_blend))
	head+=Vector2(facing*2,-1)*mantle_blend+Vector2(-facing*2,1)*recoil_blend
	head_tilt=lerpf(head_tilt,-facing*.12,mantle_blend)
	head_tilt=lerpf(head_tilt,facing*.18,recoil_blend)
	return {"hip":hip,"shoulder":shoulder,"head":head,"head_facing":head_facing,"head_tilt":head_tilt,"rise":rise,"fall":fall,"weary":weary,"airborne":airborne,"landing":landing,"twist":twist,"work":work,"contacts":contacts,"stance":stance,"contact_shoulder":contact_shoulder,"contact_hip":contact_hip,"head_yaw":head_yaw,"attention":attention}

func current_work_contacts():
	# Some mechanisms stop publishing live contacts in a modal screen. Hold
	# the last presented geometry too, so pausing cannot unhook the visible hands.
	if game!=null and game.mode!="playing": return held_contact_snapshot
	if game!=null and game.has_method("character_work_contacts") and is_on_floor() and not climbing:
		var contacts=game.character_work_contacts(self)
		if contacts is Dictionary:
			held_contact_snapshot=contacts
			return contacts
	held_contact_snapshot={}
	return {}

func reachable_hand(shoulder,target):
	return shoulder+(target-shoulder).limit_length(30.5)

func arm_pose(pose):
	var f=facing; var run=run_blend; var gait=fposmod(phase,1)*TAU
	var swing=sin(gait+PI)*moving_blend
	var near_shoulder=pose.shoulder+Vector2(f*(1.3+pose.twist*.45),1.4)
	var far_shoulder=pose.shoulder+Vector2(-f*(1.8+pose.twist*.45),.6)
	var near=near_shoulder+Vector2(-swing*f*(16+run*5),27-absf(swing)*5-run*5)
	var far=far_shoulder+Vector2(swing*f*(15+run*5),27-absf(swing)*4-run*6)
	near=near.lerp(near_shoulder+Vector2(f*22,9),crouch_blend)
	if pose.airborne:
		near=near_shoulder+Vector2(f*(13+pose.fall*5),10-pose.rise*18)
		far=far_shoulder+Vector2(-f*(12+pose.rise*3),17-pose.rise*17+pose.fall*2)
		var launch=clampf((takeoff_time-.075)/.105,0,1)
		near=near.lerp(near_shoulder+Vector2(-f*12,22),launch)
		far=far.lerp(far_shoulder+Vector2(-f*22,13),launch)
		near=near.lerp(near_shoulder+Vector2(f*19,20),landing_approach*.75)
		far=far.lerp(far_shoulder+Vector2(-f*13,24),landing_approach*.75)
	elif brake_blend>.01:
		near=near.lerp(near_shoulder+Vector2(-f*15,18),brake_blend*.7)
		far=far.lerp(far_shoulder+Vector2(f*19,12),brake_blend*.7)
	var cold=cold_blend*(1-moving_blend*.9)*(1-crouch_blend*.25)
	if not pose.airborne:
		near=near.lerp(near_shoulder+Vector2(-f*2,17),cold*.82)
		far=far.lerp(far_shoulder+Vector2(f*13,11),cold*.88)
		var tired=clampf(fatigue_blend-cold_blend*.65,0,1)*(1-moving_blend)
		near=near.lerp(near_shoulder+Vector2(f*8,27),tired*.55)
		if danger_blend>.1:
			near=near.lerp(near_shoulder+Vector2(f*14,-2) if crouching else near_shoulder+Vector2(-f*13,14),danger_blend*.8)
			far=far.lerp(far_shoulder+Vector2(-f*8,13),danger_blend*.72)
	if care_blend>.01 and is_girl: far=far.lerp(to_local(care_target),care_blend)
	if protect_blend>.01 and is_girl:
		var steady=to_local(steady_target) if steady_reachable else far_shoulder+Vector2(protect_direction*22,8)
		far=far.lerp(steady,protect_blend*(1-work_blend))
		near=near.lerp(near_shoulder+Vector2(f*11,15),protect_blend*(1-work_blend)*.6)
	near=near.lerp(near_shoulder+Vector2(f*27,10),push_blend)
	far=far.lerp(far_shoulder+Vector2(f*26,6),push_blend)
	near=near.lerp(near_shoulder+pose.work.near,work_blend)
	far=far.lerp(far_shoulder+pose.work.far,work_blend)
	var s=1.0 if is_girl else .84
	# Contact weight scales effort, while a settled real grip still meets its
	# authored rail. Normalize the ease to that contact's requested strength.
	var grip_blend=clampf(work_blend/maxf(.001,float(pose.contacts.get("weight",1.0))),0,1)
	if pose.contacts.has("near"): near=near.lerp(to_local(pose.contacts.near)/s,grip_blend)
	if pose.contacts.has("far"): far=far.lerp(to_local(pose.contacts.far)/s,grip_blend)
	var ledge=(climb_target-position)/s-Vector2(climb_direction*14,0)
	var pull=clampf((ledge.y+60)/60,0,1)
	near=near.lerp(near_shoulder+Vector2(f*19,lerpf(-19,22,pull)),mantle_blend)
	far=far.lerp(far_shoulder+Vector2(f*11,lerpf(-17,17,pull)),mantle_blend)
	if hand_blend>.001: near=near.lerp(to_local(smoothed_contact)/s,hand_blend*(1-work_blend))
	return {"near_shoulder":near_shoulder,"far_shoulder":far_shoulder,"near":reachable_hand(near_shoulder,near),"far":reachable_hand(far_shoulder,far)}

func near_elbow(shoulder,hand,head):
	# Keep the elbow below/forward of overhead work for the whole stroke. A
	# per-frame flip between the two IK solutions would make the elbow snap.
	if work_kind in ["cart_push","winch","freight_winch"] and work_blend>.02:
		return solve_knee(shoulder,hand,15,16,facing)
	if work_blend>.2 and work_kind in ["pump","roof","brace"]:
		return solve_knee(shoulder,hand,15,16,facing)
	# Rest a low crouch on a lowered elbow. The standing swing solution folds
	# upward beside the cheek when a cart grip has fully eased out.
	if crouch_blend>.45 and hand.y>shoulder.y-2:
		return solve_knee(shoulder,hand,15,16,facing)
	var preferred=solve_knee(shoulder,hand,15,16,-facing)
	if (work_blend>.2 or mantle_blend>.2) and hand.y<shoulder.y-2:
		var alternate=solve_knee(shoulder,hand,15,16,facing)
		var close=Geometry2D.get_closest_point_to_segment(head,preferred,hand).distance_squared_to(head)
		var clear=Geometry2D.get_closest_point_to_segment(head,alternate,hand).distance_squared_to(head)
		if clear>close+9: return alternate
	return preferred

func coat_contour(pose,wind):
	var hip=pose.hip; var shoulder=pose.shoulder; var f=facing
	var hem=hip.y+(20 if is_girl else 8)
	var points=PackedVector2Array([shoulder+Vector2(-f*7,-1),shoulder+Vector2(f*6,-1),shoulder+Vector2(f*10,6),shoulder.lerp(hip,.82)+Vector2(f*8,0),hip+Vector2(f*9,0),Vector2(hip.x+f*15+wind,hem),Vector2(hip.x-f*16+wind,hem-1),hip+Vector2(-f*9,-1),shoulder.lerp(hip,.46)+Vector2(-f*9,0),shoulder.lerp(hip,.18)+Vector2(-f*9,0)])
	return soft_contour(points,1.1)

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
	var arms=arm_pose(pose)
	var far_hand=arms.far; var far_shoulder=arms.far_shoulder
	var far_elbow=solve_knee(far_shoulder,far_hand,15,16,facing)
	tube(far_shoulder,far_elbow,far_hand,4.5,3.4,2.7,far,"sleeve",.78)
	draw_hand(far_hand,far_elbow,lit_color(Color(.61,.40,.27),.78),push_blend>.4 or climbing or work_kind=="balance_hold",.78)
	var skirt_wind=sin(gait-.65)*moving_blend*2+cloth_drag+rise*facing*2
	var hem=hip.y+(20 if is_girl else 8)
	var f=facing
	var body=coat_contour(pose,skirt_wind)
	draw_colored_polygon(PackedVector2Array(body),cloth)
	if is_girl and girl_cloth!=null: painted_cloth(body,shoulder,hem,Rect2(350,65,210,625),lit_color(Color(.98,1.02,1.04,.99)),girl_cloth)
	elif not is_girl and boy_cloth!=null: painted_cloth(body,shoulder,hem,Rect2(386,115,138,529),lit_color(Color(.99,1.03,1.06,.99)),boy_cloth)
	else: painted_cloth(body,shoulder,hem,Rect2(557,86,244,448),lit_color(Color(.98,1.09,1.16,.98) if is_girl else Color(1.03,1.08,1.10,.98)))
	# Cloth seams and edge light move with the silhouette, rather than floating
	# pasted body rectangles. The final anatomy is authored for these children.
	draw_polyline(PackedVector2Array([shoulder+Vector2(-f*7,1),shoulder.lerp(hip,.46)+Vector2(-f*9,0),hip+Vector2(-f*9,0),Vector2(hip.x-f*15+skirt_wind,hem-2)]),Color(edge,.17),.7,true)
	var compression=clampf(crouch_blend+work_blend*.8+pose.landing*.1,0,1)
	for crease in range(2):
		var at=hip+Vector2(-f*7,-7+crease*4)
		draw_line(at,at+Vector2(f*(11-crease*2),-2-compression*2),Color(.08,.13,.15,.18*compression),.9,true)
	for i in range(3):
		var x=-7+i*7
		draw_line(Vector2(x,hip.y-2),Vector2(x*1.5+skirt_wind,hem-3),Color(.38,.45,.43,.11),.8,true)
	if not is_girl:
		var lapel=PackedVector2Array([shoulder+Vector2(-3,1),shoulder+Vector2(4,2),shoulder+Vector2(3,12),shoulder+Vector2(-1,8)])
		draw_colored_polygon(lapel,Color(.36,.42,.38,.35))
		draw_line(shoulder+Vector2(4,12),hip+Vector2(4,3),Color(edge,.23),1,true)
		for i in range(3): draw_circle(shoulder+Vector2(5,11+i*7),.9,Color("7e8070"))
		# Worn knee cloth and a small pocket keep the boy's coat distinct from
		# the girl's long dress without introducing a generic adult costume.
		draw_colored_polygon(PackedVector2Array([hip+Vector2(-7,-5),hip+Vector2(-1,-5),hip+Vector2(-1,1),hip+Vector2(-6,2)]),Color(.14,.20,.21))
	var foot=feet[1]; var near_hip=hip+Vector2(2,0); var knee=legs[1]
	tube(near_hip,knee,foot,5.6,4.5,3.1,ink,"stocking" if is_girl else "trouser"); boot(foot,ink,sole_roll(1))
	if is_girl:
		# The dress is in front of the thighs and has a stable, sculpted hem.
		var hem_shape=soft_contour(PackedVector2Array([hip+Vector2(-f*10,-4),hip+Vector2(f*10,-4),Vector2(hip.x+f*16+skirt_wind,hem),Vector2(hip.x-f*17+skirt_wind,hem-1)]),.7)
		draw_colored_polygon(hem_shape,cloth)
		if girl_cloth!=null: painted_cloth(hem_shape,hip+Vector2(0,-4),hem,Rect2(270,400,290,295),lit_color(Color(.96,1.01,1.03,.99)),girl_cloth)
		else: painted_cloth(hem_shape,hip+Vector2(0,-4),hem,Rect2(546,330,247,210),lit_color(Color(.94,1.08,1.16,.98)))
		draw_line(Vector2(hip.x-f*16+skirt_wind,hem-2),Vector2(hip.x+f*15+skirt_wind,hem-1),Color(edge,.21),.8,true)
		draw_line(hip+Vector2(-9,-2),hip+Vector2(8,-2),Color(.44,.47,.40,.32),1.2,true)
		var patch=Vector2(-8+skirt_wind*.7,hem-8)
		draw_colored_polygon(PackedVector2Array([patch+Vector2(-3,-3),patch+Vector2(3,-2),patch+Vector2(2,4),patch+Vector2(-3,3)]),Color(.23,.30,.29,.7))
		draw_line(patch+Vector2(-2,-2),patch+Vector2(-2,3),Color(.55,.56,.46,.25),.7,true)
	draw_line(shoulder+Vector2(0,-2),head+Vector2(0,6),lit_color(Color(.50,.32,.20)),6,true)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	if is_girl:
		var braid=head+Vector2(-9*head_yaw,4)
		for i in range(6):
			var wind=sin(anim_time*5-i*.4)*(.3+run*.8)+braid_drag*(float(i)+1)/6.0
			var center=braid+Vector2(wind,5+i*3.2)
			draw_circle(center,3.3-i*.16,lit_color(Color(.13,.12,.11)))
			paint_joint(center,3.3-i*.16,Rect2(370,270,60,120),lit_color(Color(.97,.98,1.02)),girl_profile)
		var ribbon=braid+Vector2(braid_drag,23)
		# Reuse the original painted ribbon. Flat triangular loops and thick
		# tails previously read as bright sleeve stripes whenever the arm bent.
		draw_set_transform(ribbon*s,cloth_drag*.012,Vector2(s*head_facing,s))
		draw_texture_rect_region(girl_profile,Rect2(-5,-2.6,10,5.2),Rect2(118,1003,257,137),lit_color(Color(.96,1.03,1.08)))
		draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	draw_painted_head(pose,s)
	var hand=arms.near; var near_shoulder=arms.near_shoulder
	var elbow=near_elbow(near_shoulder,hand,head)
	tube(near_shoulder,elbow,hand,4.7,3.5,2.5,ink,"sleeve")
	draw_line(near_shoulder+Vector2(-facing*2,3),elbow+Vector2(-facing,0),Color(edge,.14),.8,true)
	draw_hand(hand,elbow,lit_color(Color(.67,.43,.28)),climbing or push_blend>.4 or danger_blend>.45 or work_kind in ["fire","balance_hold"] and work_blend>.3)
	# The sleeve cuff ends at the wrist, letting a small hand read separately.
	var cuff=(hand-elbow).normalized()
	var cuff_cross=Vector2(-cuff.y,cuff.x)
	draw_line(hand-cuff*3+cuff_cross*2.7,hand-cuff*3-cuff_cross*2.7,Color(edge,.29),1.2,true)
	# A narrow rounded linen fold sits inside the neckline. Broad flat collar
	# triangles used to compete with the face and look like sleeve cutouts.
	var collar=soft_contour(PackedVector2Array([shoulder+Vector2(-3,-.7),shoulder+Vector2(4.5,.3),shoulder+Vector2(3,2.8),shoulder+Vector2(-.5,2)]),.4)
	draw_colored_polygon(collar,lit_color(Color(.42,.46,.43,.85)))
	if girl_cloth!=null:
		var collar_uv=PackedVector2Array()
		for point in collar:
			var relative=point-shoulder
			collar_uv.append((Vector2(330,55)+Vector2(clampf((relative.x+3)/7.5,0,1),clampf((relative.y+.7)/3.5,0,1))*Vector2(80,25))/Vector2(girl_cloth.get_size()))
		draw_polygon(collar,painted_colors(collar,lit_color(Color(.70,.75,.73,.88))),collar_uv,girl_cloth)
	draw_set_transform(Vector2.ZERO)
