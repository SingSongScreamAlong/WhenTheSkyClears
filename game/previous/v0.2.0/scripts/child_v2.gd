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

func _ready():
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	anim_time=0 if is_girl else .83
	collision_layer=2; collision_mask=1; floor_snap_length=14
	col=CollisionShape2D.new(); col.shape=RectangleShape2D.new(); col.shape.size=Vector2(23,99 if is_girl else 84); col.position.y=-col.shape.size.y/2
	add_child(col); reset_feet()

func reset_feet():
	for i in range(2):
		foot_lock[i]=position+Vector2(-10 if i==0 else 10,0)
		foot_start[i]=foot_lock[i]
		feet[i]=Vector2(-10 if i==0 else 10,0)
	phase=.26; foot_phase=[.26,.76]

func _process(dt):
	anim_time+=dt; action_time=maxf(0,action_time-dt); hit_time=maxf(0,hit_time-dt); land_time=maxf(0,land_time-dt)
	body_lean=lerpf(body_lean,clampf(velocity.x/100,-3.4,3.4),1-exp(-dt*6))
	moving_blend=lerpf(moving_blend,clampf(abs(velocity.x)/100,0,1),1-exp(-dt*10))
	queue_redraw()

func _physics_process(dt):
	if game==null or game.mode!="playing": return
	var axis=Input.get_axis("left","right") if controlled else ai_axis
	var jump=Input.is_action_just_pressed("jump") if controlled else ai_jump
	if not controlled:
		ai_jump=false
		if not is_on_floor() and leap_axis!=0: axis=leap_axis
		elif is_on_floor() and not jump: leap_axis=0
	crouching=Input.is_action_pressed("crouch") if controlled else forced_crouch
	if climbing:
		climb_clock-=dt
		if hit_time>0 or climb_clock<=0:
			climbing=false
		else:
			if position.y>climb_target.y: velocity=Vector2(climb_direction*7,-215)
			else: velocity=Vector2(climb_direction*125,-8)
			move_and_slide()
			if (position.x-climb_target.x)*climb_direction>=0:
				climbing=false; land_time=.2; reset_feet()
			return
	var speed=166.0
	if controlled and Input.is_action_pressed("sprint") and game.stamina>2 and not crouching:
		speed=265
		if abs(axis)>.1: game.stamina=maxf(0,game.stamina-dt*21)
	if not controlled:
		speed=210 if abs(game.player.position.x-position.x)>105 else 172
		if jump or (not is_on_floor() and leap_axis!=0): speed=268
	if crouching: speed=73
	if game.in_water(position.x): speed*=.61
	if controlled and action_time>0: axis=0; jump=false
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
		if not controlled: leap_axis=axis
		if controlled: game.stamina=maxf(0,game.stamina-7)
	velocity.y+=1420*dt
	if controlled and Input.is_action_just_released("jump") and not Input.is_action_pressed("jump") and velocity.y< -170: velocity.y*=.55
	var height=(74.0 if is_girl else 62.0) if crouching else (99.0 if is_girl else 84.0)
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
			if body is RigidBody2D: body.linear_velocity.x=axis*78
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
					if foot_phase[i]>=stance: foot_lock[i]=Vector2(position.x+facing*reach,position.y); step(i)
					feet[i]=(foot_lock[i]-position)/(1.0 if is_girl else .84)
					feet[i].y=0
				else:
					if foot_phase[i]<stance: foot_start[i]=position+feet[i]*(1.0 if is_girl else .84)
					var u=(p-stance)/(1-stance); var smooth=u*u*(3-2*u)
					var end=position+Vector2(facing*reach,0)
					feet[i]=(foot_start[i].lerp(end,smooth)-position)/(1.0 if is_girl else .84)
					feet[i].y=-sin(u*PI)*(18 if abs(velocity.x)>220 else 12)
				foot_phase[i]=p
		else:
			for i in range(2): feet[i]=feet[i].lerp(Vector2((-9 if i==0 else 9),0),1-exp(-dt*12))
	else:
		feet[0]=feet[0].lerp(Vector2(-14*facing,-10),1-exp(-dt*14)); feet[1]=feet[1].lerp(Vector2(18*facing,-23),1-exp(-dt*14))
	was_floor=is_on_floor(); last_direction=facing; moving_last=abs(velocity.x)>5

func step(_side):
	if controlled:
		game.play_step(position,-24 if crouching else -20)
		if abs(velocity.x)>210: game.spawn_dust(position,2)

func solve_knee(hip,foot,length_a=25.0,length_b=24.0,bend=1.0):
	var delta=foot-hip; var dist=clampf(delta.length(),.1,length_a+length_b-.05); var axis=delta.normalized()
	var along=(length_a*length_a-length_b*length_b+dist*dist)/(2*dist)
	return hip+axis*along+Vector2(-axis.y,axis.x)*sqrt(maxf(0,length_a*length_a-along*along))*bend

func tube(a,b,c,width_a,width_b,width_c,color):
	var n1=Vector2(-(b-a).y,(b-a).x).normalized(); var n2=Vector2(-(c-b).y,(c-b).x).normalized(); var middle=(n1+n2).normalized()
	draw_colored_polygon(PackedVector2Array([a+n1*width_a,b+middle*width_b,c+n2*width_c,c-n2*width_c,b-middle*width_b,a-n1*width_a]),color)
	draw_circle(a,width_a*.94,color); draw_circle(b,width_b*.94,color); draw_circle(c,width_c*.94,color)

func cloth_polygon(points,base,tint):
	draw_colored_polygon(PackedVector2Array(points),base)
	var uv=PackedVector2Array()
	for p in points: uv.append(Vector2((620+p.x*5)/1280,(maxf(0,70+p.y)*8)/1280))
	draw_polygon(PackedVector2Array(points),PackedColorArray([tint]),uv,head_atlas)

func boot(ankle,color):
	var f=facing
	var outline=PackedVector2Array([ankle+Vector2(-4,-7),ankle+Vector2(4,-7),ankle+Vector2(5*f,-3),ankle+Vector2(12*f,-1),ankle+Vector2(12*f,2),ankle+Vector2(-5,2)])
	draw_colored_polygon(outline,color)
	draw_line(ankle+Vector2(-4,2),ankle+Vector2(11*f,2),Color(.37,.38,.31,.45),1,true)

func _draw():
	var s=1.0 if is_girl else .84
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	var run=clampf((abs(velocity.x)-160)/105,0,1)
	var gait=fposmod(phase,1)*TAU
	var bob=(1-cos(gait*2))*1.0*moving_blend
	var squat=20.0 if crouching else 0.0
	var landing=sin(land_time/.24*PI)*4 if land_time>0 else 0.0
	var hip=Vector2(body_lean*.65,-43+run*3+squat*.42+bob+landing)
	var shoulder=Vector2(body_lean*1.5,-75+squat+bob+landing)
	var head=shoulder+Vector2(facing*1.2,-15)
	if climbing: shoulder+=Vector2(facing*13,18); head+=Vector2(facing*15,19)
	if hit_time>0: shoulder.x-=facing*4; head.x-=facing*4
	if action_time>0:
		shoulder+=Vector2(facing*7,9); head+=Vector2(facing*8,10)
		if game!=null and not game.pending_action.is_empty() and game.pending_action.kind=="fire":
			hip.y+=9; shoulder.y+=10; head.y+=10
	var bleak=float(game.chapter)/4.0 if game!=null else 0
	var ink=Color("141d20"); var far=Color("273237"); var cloth=Color("213436").lerp(Color("1b262d"),bleak)
	var edge=Color("7b8c81").lerp(Color("617c8c"),bleak)
	var breathe=sin(anim_time*2.8)*.5*(1-moving_blend)
	shoulder.y+=breathe; head.y+=breathe
	for i in range(2):
		var foot=feet[i]; var leg_hip=hip+Vector2(-2 if i==0 else 2,0)
		var knee=solve_knee(leg_hip,foot,25,24,-facing)
		legs[i]=knee
		if i==0:
			tube(leg_hip,knee,foot,5.6,4.5,3.3,far); boot(foot,far)
	var arm_swing=sin(gait+PI)*(.8-run*.4)*moving_blend
	var far_hand=shoulder+Vector2(arm_swing*16,29)
	var far_elbow=solve_knee(shoulder,far_hand,15,16,facing)
	tube(shoulder+Vector2(-2,2),far_elbow,far_hand,4.5,3.4,2.7,far)
	var skirt_wind=sin(gait-.65)*moving_blend*3-body_lean
	var hem=hip.y+(20 if is_girl else 8)
	var body=[shoulder+Vector2(-8,-1),shoulder+Vector2(7,-1),shoulder+Vector2(11,8),hip+Vector2(9,0),Vector2(15+skirt_wind,hem),Vector2(-16+skirt_wind,hem-1),hip+Vector2(-9,0),shoulder+Vector2(-11,8)]
	draw_colored_polygon(PackedVector2Array(body),cloth)
	var uv=PackedVector2Array()
	for p in body: uv.append(Vector2(lerpf(545,800,clampf((p.x+18)/36,0,1))/1280,lerpf(30,565,clampf((p.y-shoulder.y)/maxf(1,hem-shoulder.y),0,1))/1280))
	draw_polygon(PackedVector2Array(body),PackedColorArray([Color(.34,.44,.41,.24)]),uv,head_atlas)
	# Cloth seams and edge light move with the silhouette, rather than floating
	# pasted body rectangles. The final anatomy is authored for these children.
	draw_polyline(PackedVector2Array([shoulder+Vector2(-8,1),shoulder+Vector2(-10,10),hip+Vector2(-9,0),Vector2(-15+skirt_wind,hem-2)]),Color(edge,.30),1.3,true)
	for i in range(3):
		var x=-7+i*7
		draw_line(Vector2(x,hip.y-2),Vector2(x*1.5+skirt_wind,hem-3),Color(.38,.45,.43,.11),.8,true)
	if not is_girl:
		for i in range(3): draw_circle(shoulder+Vector2(5,11+i*7),.9,Color("7e8070"))
	var foot=feet[1]; var near_hip=hip+Vector2(2,0); var knee=legs[1]
	tube(near_hip,knee,foot,5.6,4.5,3.1,ink); boot(foot,ink)
	if is_girl:
		# The dress is in front of the thighs and has a stable, sculpted hem.
		var hem_shape=PackedVector2Array([hip+Vector2(-10,-4),hip+Vector2(10,-4),Vector2(16+skirt_wind,hem),Vector2(-17+skirt_wind,hem-1)])
		draw_colored_polygon(hem_shape,cloth)
		draw_line(Vector2(-16+skirt_wind,hem-2),Vector2(15+skirt_wind,hem-1),Color(edge,.25),1,true)
	draw_line(shoulder+Vector2(0,-2),head+Vector2(0,6),ink,7,true)
	draw_set_transform(head*s,0,Vector2(s*facing,s))
	var profile_tint=Color(.23,.29,.29).lerp(Color(.15,.23,.28),bleak)
	if is_girl: draw_texture_rect_region(girl_profile,Rect2(-19,-17,34,32),Rect2(30,15,1135,1000),profile_tint)
	else: draw_texture_rect_region(head_atlas,Rect2(-15,-17,31,34),Rect2(0,0,440,490),profile_tint)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	if is_girl:
		var braid=head+Vector2(-9*facing,4)
		for i in range(6):
			var wind=sin(anim_time*5-i*.4)*(.5+run*1.5)-body_lean*.6
			draw_circle(braid+Vector2(wind,5+i*3.2),3.3-i*.16,ink)
		var ribbon=braid+Vector2(-body_lean*.6,23)
		draw_line(ribbon,ribbon+Vector2(-facing*9,3+sin(anim_time*5)*1.5),Color("658d9b"),2.3,true)
		draw_line(ribbon,ribbon+Vector2(-facing*5,8),Color("537d91"),1.8,true)
	var hand=shoulder+Vector2(-arm_swing*16,29-run*6)
	if crouching: hand=shoulder+Vector2(facing*22,9)
	if action_time>0: hand=shoulder+Vector2(facing*24,13)
	if action_time>0 and game!=null and not game.pending_action.is_empty():
		if game.pending_action.kind in ["wheel","pump","bridge"]: hand=shoulder+Vector2(facing*(24+sin(anim_time*3.8)*3),6+cos(anim_time*3.8)*3)
		elif game.pending_action.kind=="roof": hand=shoulder+Vector2(facing*23,-15+sin(anim_time*4)*2)
	if climbing: hand=shoulder+Vector2(facing*20,-5)
	if hand_active: hand=to_local(contact_hand)/s
	var elbow=solve_knee(shoulder,hand,15,16,-facing)
	tube(shoulder+Vector2(1,3),elbow,hand,4.6,3.5,2.5,ink)
	draw_line(shoulder+Vector2(-2,3),elbow+Vector2(-1,0),Color(edge,.20),1,true)
	draw_circle(hand,2.6,Color(.19,.25,.24))
	# Small folded linen collar; no oversized pale patch or bright eyes.
	draw_colored_polygon(PackedVector2Array([shoulder+Vector2(-3,-1),shoulder+Vector2(6,1),shoulder+Vector2(3,5)]),Color(.37,.42,.37,.55))
	draw_set_transform(Vector2.ZERO)
