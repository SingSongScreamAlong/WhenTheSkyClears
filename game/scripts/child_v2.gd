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

func _ready():
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	anim_time=0 if is_girl else .83
	collision_layer=2; collision_mask=1; floor_snap_length=14
	col=CollisionShape2D.new(); col.shape=RectangleShape2D.new(); col.shape.size=Vector2(23,99); col.position.y=-col.shape.size.y/2
	add_child(col); reset_feet()

func reset_feet():
	for i in range(2):
		foot_lock[i]=position+Vector2(-10 if i==0 else 10,0)
		foot_lock[i].y=surface_height(foot_lock[i].x,position.y)
		foot_start[i]=foot_lock[i]
		feet[i]=(foot_lock[i]-position)/1.0
	phase=.26; foot_phase=[.26,.76]

func surface_height(world_x,fallback_y):
	# Flat studies and older chapters do not need to implement this query. The
	# native controller still owns the body; only the sole follows the ground.
	if game!=null and game.has_method("surface_y_at"):
		var result=float(game.surface_y_at(world_x,fallback_y))
		if absf(result-fallback_y)<42.0: return result
	return fallback_y

func _process(dt):
	anim_time+=dt; action_time=maxf(0,action_time-dt); hit_time=maxf(0,hit_time-dt); land_time=maxf(0,land_time-dt); takeoff_time=maxf(0,takeoff_time-dt)
	body_lean=lerpf(body_lean,clampf(velocity.x/100,-3.4,3.4),1-exp(-dt*6))
	moving_blend=lerpf(moving_blend,clampf(abs(velocity.x)/100,0,1),1-exp(-dt*10))
	push_blend=lerpf(push_blend,1.0 if pushing else 0.0,1-exp(-dt*9))
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
	if controlled and game.slice_active:
		var alignment=game.last_house.alignment_axis()
		if alignment!=null: axis=alignment
	var jump=Input.is_action_just_pressed("jump") if controlled else ai_jump
	if not controlled:
		ai_jump=false
		if not is_on_floor() and leap_axis!=0: axis=leap_axis
		elif is_on_floor() and not jump: leap_axis=0
	var wants_crouch=Input.is_action_pressed("crouch") if controlled else forced_crouch
	# Keep the smaller collider until the full standing shape is clear.
	crouching=wants_crouch or (crouching and not can_stand())
	if climbing:
		climb_clock-=dt
		if hit_time>0 or climb_clock<=0:
			climbing=false
		else:
			if position.y>climb_target.y: velocity=Vector2(climb_direction*7,-215)
			else: velocity=Vector2(climb_direction*125,-8)
			feet[0]=feet[0].lerp(Vector2(-11*facing,-7),1-exp(-dt*12))
			feet[1]=feet[1].lerp(Vector2(16*facing,-32),1-exp(-dt*12))
			move_and_slide()
			if (position.x-climb_target.x)*climb_direction>=0:
				climbing=false; land_time=.2; reset_feet()
			return
	var speed=166.0
	if controlled and Input.is_action_pressed("sprint") and game.stamina>2 and not crouching:
		speed=265
		if abs(axis)>.1: game.stamina=maxf(0,game.stamina-dt*21)
	if not controlled:
		speed=clampf(166.0+(abs(game.player.position.x-position.x)-70.0)*1.1,166.0,265.0)
		if jump or (not is_on_floor() and leap_axis!=0): speed=268
	if crouching: speed=73
	if game.in_water(position.x,position.y): speed*=.61
	speed*=game.wind_speed_scale(self)
	if action_time>0: axis=0; jump=false; leap_axis=0
	var before=position
	var acceleration=1080 if is_on_floor() else 540
	if axis==0 and is_on_floor(): acceleration=1460
	velocity.x=move_toward(velocity.x,axis*speed,acceleration*dt)
	if abs(axis)>.1: facing=signf(axis)
	if is_on_floor(): coyote=.14
	else: coyote-=dt
	if jump: jump_buffer=.15
	else: jump_buffer-=dt
	if jump_buffer>0 and coyote>0 and not crouching:
		velocity.y=-525; jump_buffer=0; coyote=0
		takeoff_time=.18
		if not controlled: leap_axis=axis
		if controlled:
			game.stamina=maxf(0,game.stamina-7)
			game.remember_jump(position,axis)
	velocity.y+=1420*dt
	if controlled and Input.is_action_just_released("jump") and not Input.is_action_pressed("jump") and velocity.y< -170: velocity.y*=.55
	var height=74.0 if crouching else 99.0
	col.shape.size.y=height; col.position.y=-height/2
	move_and_slide()
	if not is_on_floor() and is_on_wall() and velocity.y> -75 and abs(axis)>.1 and not crouching:
		var ledges=game.level.platforms+game.level.ground
		for ledge in ledges:
			var edge=float(ledge.x) if axis>0 else float(ledge.x)+float(ledge.w)
			var reach=position.y-float(ledge.y)
			if abs(position.x-edge)<18 and reach>10 and reach<86:
				climbing=true; climb_clock=1.15; climb_direction=signf(axis); climb_target=Vector2(edge+climb_direction*22,float(ledge.y)-2); mantle_count+=1; break
	if controlled and Input.is_action_pressed("interact") and abs(axis)>.1:
		for i in range(get_slide_collision_count()):
			var body=get_slide_collision(i).get_collider()
			if body is RigidBody2D:
				body.linear_velocity.x=axis*78; pushing=true
	var distance=absf(position.x-before.x)
	if is_on_floor():
		if not was_floor: land_time=.24; reset_feet(); game.spawn_dust(position,4)
		if abs(velocity.x)>5:
			if not moving_last: reset_feet()
			if facing!=last_direction: reset_feet()
			var stride=116.0 if abs(velocity.x)>220 else 94.0
			if crouching: stride=61.0
			phase+=distance/stride
			for i in range(2):
				var p=fposmod(phase+i*.5,1)
				var stance=.42 if abs(velocity.x)>220 else .50
				var reach=24 if not crouching else 18
				if p<stance:
					if foot_phase[i]>=stance:
						foot_lock[i]=Vector2(position.x+facing*reach,surface_height(position.x+facing*reach,position.y)); step(i)
					feet[i]=(foot_lock[i]-position)/1.0
				else:
					if foot_phase[i]<stance: foot_start[i]=position+feet[i]*1.0
					var u=(p-stance)/(1-stance); var smooth=u*u*(3-2*u)
					var end=Vector2(position.x+facing*reach,surface_height(position.x+facing*reach,position.y))
					feet[i]=(foot_start[i].lerp(end,smooth)-position)/1.0
					feet[i].y-=sin(u*PI)*(18 if abs(velocity.x)>220 else 12)
				foot_phase[i]=p
		else:
			for i in range(2):
				var rest_x=(-9.0 if i==0 else 9.0)
				var sole_y=(surface_height(position.x+rest_x*1.0,position.y)-position.y)/1.0
				feet[i]=feet[i].lerp(Vector2(rest_x,sole_y),1-exp(-dt*12))
	else:
		var rising=clampf(-velocity.y/400.0,0,1)
		var falling=clampf(velocity.y/480.0,0,1)
		feet[0]=feet[0].lerp(Vector2((-18+rising*7)*facing,-9-rising*15+falling*5),1-exp(-dt*14))
		feet[1]=feet[1].lerp(Vector2((15-falling*8)*facing,-12-rising*21+falling*9),1-exp(-dt*14))
		if climbing:
			feet[0]=feet[0].lerp(Vector2(-11*facing,-5),1-exp(-dt*14)); feet[1]=feet[1].lerp(Vector2(16*facing,-31),1-exp(-dt*14))
	was_floor=is_on_floor(); last_direction=facing; moving_last=abs(velocity.x)>5

func can_stand():
	var shape=RectangleShape2D.new(); shape.size=Vector2(22,98)
	var query=PhysicsShapeQueryParameters2D.new()
	query.shape=shape; query.transform=Transform2D(0,global_position+Vector2(0,-50))
	query.collision_mask=1; query.exclude=[get_rid()]
	return get_world_2d().direct_space_state.intersect_shape(query,1).is_empty()

func step(_side):
	game.play_step(position,(-24 if crouching else -20) if controlled else (-32 if crouching else -28))
	if controlled and abs(velocity.x)>210: game.spawn_dust(position,2)

func solve_knee(hip,foot,length_a=25.0,length_b=24.0,bend=1.0):
	var delta=foot-hip; var dist=clampf(delta.length(),.1,length_a+length_b-.05); var axis=delta.normalized()
	var along=(length_a*length_a-length_b*length_b+dist*dist)/(2*dist)
	return hip+axis*along+Vector2(-axis.y,axis.x)*sqrt(maxf(0,length_a*length_a-along*along))*bend

func tube(a,b,c,width_a,width_b,width_c,color,material="",depth=1.0):
	var n1=Vector2(-(b-a).y,(b-a).x).normalized(); var n2=Vector2(-(c-b).y,(c-b).x).normalized(); var middle=(n1+n2).normalized()
	var shape=PackedVector2Array([a+n1*width_a,b+middle*width_b,c+n2*width_c,c-n2*width_c,b-middle*width_b,a-n1*width_a])
	if Geometry2D.triangulate_polygon(shape).is_empty():
		# A fully folded limb can cross its own outline. Paint the two
		# rounded segments directly instead of submitting invalid geometry.
		draw_line(a,b,color,width_a+width_b,true); draw_line(b,c,color,width_b+width_c,true)
		for joint in [[a,width_a],[b,width_b],[c,width_c]]: draw_circle(joint[0],joint[1],color)
		return
	draw_colored_polygon(shape,color)
	draw_circle(a,width_a*.94,color); draw_circle(b,width_b*.94,color); draw_circle(c,width_c*.94,color)
	if not material.is_empty():
		# Only opaque interior paint is sampled. The sleeve/trouser source's
		# transparent cutout edges never become light holes in the moving limbs.
		var region=Rect2(1042,125,68,315) if material=="sleeve" else Rect2(580,690,72,420)
		var split=(b-a).length()/maxf(.01,(b-a).length()+(c-b).length())
		var local_uv=[Vector2(0,0),Vector2(0,split),Vector2(0,1),Vector2(1,1),Vector2(1,split),Vector2(1,0)]
		var uv=PackedVector2Array()
		for point in local_uv: uv.append((region.position+point*region.size)/Vector2(head_atlas.get_size()))
		var tint=Color(.50,.61,.58,.88) if material=="sleeve" else Color(.42,.53,.57,.85)
		tint.r*=depth; tint.g*=depth; tint.b*=depth
		draw_polygon(shape,PackedColorArray([tint]),uv,head_atlas)
		# A quiet fold catches at the elbow/knee, following the bend rather
		# than painting an unchanging rectangular limb over the anatomy.
		draw_line(b-middle*width_b*.58,b+middle*width_b*.36,Color(.08,.14,.15,.24),.65,true)

func painted_cloth(points,origin,end_y,region,tint):
	var uv=PackedVector2Array()
	for p in points:
		var v=clampf((p.y-origin.y)/maxf(1,end_y-origin.y),0,1)
		var center_x=lerpf(origin.x,body_lean*.65,v)
		var u=clampf((p.x-center_x+18)/36.0,0,1)
		uv.append((region.position+Vector2(u,v)*region.size)/Vector2(head_atlas.get_size()))
	var outline=PackedVector2Array(points)
	if not Geometry2D.triangulate_polygon(outline).is_empty(): draw_polygon(outline,PackedColorArray([tint]),uv,head_atlas)

func boot(ankle,color):
	var f=facing
	var outline=PackedVector2Array([ankle+Vector2(-4.5*f,-8),ankle+Vector2(3.5*f,-8),ankle+Vector2(4*f,-4),ankle+Vector2(9*f,-3),ankle+Vector2(12*f,-1),ankle+Vector2(12*f,1.5),ankle+Vector2(6*f,2.5),ankle+Vector2(-5*f,2.5),ankle+Vector2(-5*f,-3)])
	draw_colored_polygon(outline,color)
	draw_polyline(PackedVector2Array([ankle+Vector2(-5*f,1),ankle+Vector2(6*f,1.5),ankle+Vector2(11*f,.5)]),Color(.37,.38,.31,.45),1,true)
	draw_line(ankle+Vector2(-4*f,-7),ankle+Vector2(3*f,-7),Color(.48,.47,.39,.35),1.2,true)
	draw_line(ankle+Vector2(3*f,-4),ankle+Vector2(6*f,-2),Color(.43,.46,.41,.27),.8,true)

func draw_hand(at,elbow,color,open_hand=false):
	var direction=(at-elbow).normalized()
	var across=Vector2(-direction.y,direction.x)
	var points=PackedVector2Array([at-direction*2.2-across*2.0,at+direction*3.0-across*1.9,at+direction*4.3-across*.5,at+direction*3.7+across*1.5,at+direction*.5+across*2.2,at-direction*1.8+across*1.7])
	draw_colored_polygon(points,color)
	draw_line(at-direction,at+direction*1.1+across*3.1,color,1.8,true)
	if open_hand:
		draw_line(at+across*1.0,at+direction*5+across*1.0,color,1.3,true)
		draw_line(at-across*1.0,at+direction*4.4-across*1.0,color,1.2,true)

func _draw():
	var s=1.0
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	var run=clampf((abs(velocity.x)-160)/105,0,1)
	var gait=fposmod(phase,1)*TAU
	var bob=(1-cos(gait*2))*1.0*moving_blend
	var squat=20.0 if crouching else 0.0
	var landing=sin(land_time/.24*PI)*4 if land_time>0 else 0.0
	var airborne=not is_on_floor() and game!=null and game.mode=="playing"
	var rise=clampf(-velocity.y/400,0,1) if airborne else 0.0
	var fall=clampf(velocity.y/500,0,1) if airborne else 0.0
	var weary=fatigue_blend*(1.0-moving_blend*.35)
	var shiver=sin(anim_time*28)*.32*fatigue_blend*(1-moving_blend)
	var hip=Vector2(body_lean*.65-facing*push_blend*4,-47+run*3+squat*.58+bob+landing+push_blend*2)
	var shoulder=Vector2(body_lean*1.5+facing*(weary*2+push_blend*11+rise*2),-75+squat+bob+landing+weary*2+push_blend*8+fall*2)
	if takeoff_time>0:
		var extension=sin(takeoff_time/.18*PI)
		shoulder.y-=extension*1.7; hip.y-=extension*.8
	if climbing: shoulder+=Vector2(facing*12,15)
	if hit_time>0: shoulder.x-=facing*4
	if action_time>0:
		shoulder+=Vector2(facing*7,9)
		if game!=null and not game.pending_action.is_empty() and game.pending_action.kind=="fire":
			hip.y+=9; shoulder.y+=10
	var bleak=float(game.chapter)/4.0 if game!=null else 0
	var ink=Color("141d20"); var far=Color("273237"); var cloth=Color("213436").lerp(Color("1b262d"),bleak)
	var edge=Color("7b8c81").lerp(Color("617c8c"),bleak)
	var breathe=sin(anim_time*(2.8+weary*.7))*(.5+weary*.3)*(1-moving_blend)
	shoulder+=Vector2(shiver,breathe)
	var head=shoulder+Vector2(facing*(1.2+weary*2),-15+weary*1.7)
	var head_facing=facing
	if glance_blend>.55 and glance_direction!=facing: head_facing=glance_direction
	head.x+=head_facing*glance_blend*1.6
	var head_tilt=facing*(-run*.055+weary*.13+fall*.05)-head_facing*glance_blend*.035
	if climbing: head+=Vector2(facing*2,-1); head_tilt=-facing*.12
	if hit_time>0: head+=Vector2(-facing*2,1); head_tilt=facing*.18
	for i in range(2):
		var foot=feet[i]; var leg_hip=hip+Vector2(-2 if i==0 else 2,0)
		var knee=solve_knee(leg_hip,foot,25,24,-facing)
		legs[i]=knee
		if i==0:
			tube(leg_hip,knee,foot,5.6,4.5,3.3,far,"" if is_girl else "trouser",.76); boot(foot,far)
	var arm_swing=sin(gait+PI)*(.8-run*.4)*moving_blend
	var far_hand=shoulder+Vector2(arm_swing*16,29)
	if airborne: far_hand=shoulder+Vector2(-facing*(12+rise*3),17-rise*17+fall*2)
	if danger_blend>.1:
		var guard=shoulder+Vector2(-facing*16,13 if is_girl else 7)
		far_hand=far_hand.lerp(guard,danger_blend*.78)
	if weary>.1: far_hand=far_hand.lerp(shoulder+Vector2(facing*8,14),weary*.55)
	if push_blend>.01: far_hand=far_hand.lerp(shoulder+Vector2(facing*26,6),push_blend)
	if climbing: far_hand=shoulder+Vector2(facing*17,-15)
	var far_elbow=solve_knee(shoulder,far_hand,15,16,facing)
	tube(shoulder+Vector2(-2,2),far_elbow,far_hand,4.5,3.4,2.7,far,"sleeve",.76)
	draw_hand(far_hand,far_elbow,far,push_blend>.4 or climbing)
	var skirt_wind=sin(gait-.65)*moving_blend*2+cloth_drag+rise*facing*2
	var hem=hip.y+(20 if is_girl else 8)
	var body=[shoulder+Vector2(-8,-1),shoulder+Vector2(7,-1),shoulder+Vector2(11,8),hip+Vector2(9,0),Vector2(15+skirt_wind,hem),Vector2(-16+skirt_wind,hem-1),hip+Vector2(-9,0),shoulder+Vector2(-11,8)]
	draw_colored_polygon(PackedVector2Array(body),cloth)
	painted_cloth(body,shoulder,hem,Rect2(638,260,96,246),Color(.50,.60,.56,.88).lerp(Color(.39,.51,.53,.88),bleak))
	# Cloth seams and edge light move with the silhouette, rather than floating
	# pasted body rectangles. The final anatomy is authored for these children.
	draw_polyline(PackedVector2Array([shoulder+Vector2(-8,1),shoulder+Vector2(-10,10),hip+Vector2(-9,0),Vector2(-15+skirt_wind,hem-2)]),Color(edge,.30),1.3,true)
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
	tube(near_hip,knee,foot,5.6,4.5,3.1,ink,"" if is_girl else "trouser"); boot(foot,ink)
	if is_girl:
		# The dress is in front of the thighs and has a stable, sculpted hem.
		var hem_shape=PackedVector2Array([hip+Vector2(-10,-4),hip+Vector2(10,-4),Vector2(16+skirt_wind,hem),Vector2(-17+skirt_wind,hem-1)])
		draw_colored_polygon(hem_shape,cloth)
		painted_cloth(hem_shape,hip+Vector2(0,-4),hem,Rect2(590,430,120,85),Color(.46,.57,.53,.87).lerp(Color(.35,.46,.49,.87),bleak))
		draw_line(Vector2(-16+skirt_wind,hem-2),Vector2(15+skirt_wind,hem-1),Color(edge,.25),1,true)
		draw_line(hip+Vector2(-9,-2),hip+Vector2(8,-2),Color(.44,.47,.40,.32),1.2,true)
		var patch=Vector2(-8+skirt_wind*.7,hem-8)
		draw_colored_polygon(PackedVector2Array([patch+Vector2(-3,-3),patch+Vector2(3,-2),patch+Vector2(2,4),patch+Vector2(-3,3)]),Color(.23,.30,.29,.7))
		draw_line(patch+Vector2(-2,-2),patch+Vector2(-2,3),Color(.55,.56,.46,.25),.7,true)
	draw_line(shoulder+Vector2(0,-2),head+Vector2(0,6),ink,7,true)
	draw_set_transform(head*s,head_tilt,Vector2(s*head_facing,s))
	var profile_tint=Color(.23,.29,.29).lerp(Color(.15,.23,.28),bleak)
	if is_girl: draw_texture_rect_region(girl_profile,Rect2(-19,-17,34,32),Rect2(30,15,1135,1000),profile_tint)
	else: draw_texture_rect_region(head_atlas,Rect2(-15,-17,31,34),Rect2(0,0,440,490),profile_tint)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	if is_girl:
		var braid=head+Vector2(-9*head_facing,4)
		for i in range(6):
			var wind=sin(anim_time*5-i*.4)*(.3+run*.8)+braid_drag*(float(i)+1)/6.0
			draw_circle(braid+Vector2(wind,5+i*3.2),3.3-i*.16,ink)
		var ribbon=braid+Vector2(braid_drag,23)
		draw_colored_polygon(PackedVector2Array([ribbon,ribbon+Vector2(-head_facing*5,-2),ribbon+Vector2(-head_facing*4,3),ribbon+Vector2(head_facing*3,2),ribbon+Vector2(head_facing*4,-2)]),Color("5e8291"))
		draw_line(ribbon,ribbon+Vector2(-head_facing*8+cloth_drag*.3,4+sin(anim_time*5)*1.3),Color("658d9b"),2.0,true)
		draw_line(ribbon,ribbon+Vector2(-head_facing*4,8),Color("537d91"),1.6,true)
	var hand=shoulder+Vector2(-arm_swing*16,29-run*6)
	if crouching: hand=shoulder+Vector2(facing*22,9)
	if airborne: hand=shoulder+Vector2(facing*(13+fall*5),10-rise*18)
	if danger_blend>.1 and not hand_active:
		var shelter_hand=shoulder+Vector2(facing*17,-7) if crouching else shoulder+Vector2(-facing*13,18)
		hand=hand.lerp(shelter_hand,danger_blend*.8)
	if weary>.1 and not crouching: hand=hand.lerp(shoulder+Vector2(facing*10,15),weary*.52)
	if push_blend>.01: hand=hand.lerp(shoulder+Vector2(facing*27,10),push_blend)
	if action_time>0: hand=shoulder+Vector2(facing*24,13)
	if action_time>0 and game!=null and not game.pending_action.is_empty():
		if game.pending_action.kind in ["wheel","pump","bridge","relay"]: hand=shoulder+Vector2(facing*(24+sin(anim_time*3.8)*3),6+cos(anim_time*3.8)*3)
		elif game.pending_action.kind=="roof": hand=shoulder+Vector2(facing*23,-15+sin(anim_time*4)*2)
		elif game.pending_action.kind in ["clear","brace"]: hand=shoulder+Vector2(facing*(22+sin(anim_time*2.7)*2),15+cos(anim_time*2.7)*2)
	if climbing: hand=shoulder+Vector2(facing*17,-15)
	if hand_active: hand=to_local(contact_hand)/s
	var elbow=solve_knee(shoulder,hand,15,16,-facing)
	tube(shoulder+Vector2(1,3),elbow,hand,4.6,3.5,2.5,ink,"sleeve")
	draw_line(shoulder+Vector2(-2,3),elbow+Vector2(-1,0),Color(edge,.20),1,true)
	draw_hand(hand,elbow,Color(.19,.25,.24),climbing or push_blend>.4 or danger_blend>.45)
	# The sleeve cuff ends at the wrist, letting a small hand read separately.
	var cuff=(hand-elbow).normalized()
	var cuff_cross=Vector2(-cuff.y,cuff.x)
	draw_line(hand-cuff*3+cuff_cross*2.7,hand-cuff*3-cuff_cross*2.7,Color(edge,.29),1.2,true)
	# Small folded linen collar; no oversized pale patch or bright eyes.
	draw_colored_polygon(PackedVector2Array([shoulder+Vector2(-3,-1),shoulder+Vector2(6,1),shoulder+Vector2(3,5)]),Color(.37,.42,.37,.55))
	draw_set_transform(Vector2.ZERO)
