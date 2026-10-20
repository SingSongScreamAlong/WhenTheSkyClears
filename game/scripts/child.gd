extends CharacterBody2D

var game
var is_girl = true
var controlled = true
var following = true
var phase = 0.0
var facing = 1.0
var crouching = false
var coyote = 0.0
var jump_buffer = 0.0
var was_floor = false
var footstep_clock = 0.0
var ai_axis = 0.0
var ai_jump = false
var forced_crouch = false
var leap_axis = 0.0
var contact_hand = Vector2.ZERO
var hand_active = false
var col: CollisionShape2D
var anim_time = 0.0
var anim_clip = "Idle_Loop"
var drawn_pose = []
var action_time = 0.0
var hit_time = 0.0
var land_time = 0.0
var boy_atlas = preload("res://assets/characters/boy_atlas.png")
var girl_profile = preload("res://assets/characters/girl_profile.png")

func _process(dt):
	anim_time+=dt
	action_time=maxf(0,action_time-dt); hit_time=maxf(0,hit_time-dt); land_time=maxf(0,land_time-dt)
	var clip="Idle_Loop"
	if action_time>0: clip="Fixing_Kneeling"
	elif hit_time>0: clip="Hit_Head"
	elif game!=null and game.mode=="playing":
		if not is_on_floor(): clip="Jump_Loop"
		elif crouching: clip="Crouch_Fwd_Loop" if abs(velocity.x)>10 else "Crouch_Idle_Loop"
		elif abs(velocity.x)>250: clip="Sprint_Loop"
		elif abs(velocity.x)>155: clip="Jog_Fwd_Loop"
		elif abs(velocity.x)>10: clip="Walk_Loop"
	if clip!=anim_clip: anim_clip=clip; anim_time=0
	if game!=null and not game.motion_data.is_empty():
		var c=game.motion_data.clips[anim_clip]
		var progress=fposmod(anim_time/float(c.duration),1.0)*c.frames.size()
		var a=c.frames[int(progress)%c.frames.size()]
		var b=c.frames[(int(progress)+1)%c.frames.size()]
		if drawn_pose.is_empty():
			for p in a: drawn_pose.append(Vector2(p[0],p[1]))
		for i in range(a.size()):
			var target=Vector2(a[i][0],a[i][1]).lerp(Vector2(b[i][0],b[i][1]),fposmod(progress,1))
			drawn_pose[i]=drawn_pose[i].lerp(target,1-exp(-dt*17))
	queue_redraw()

func _ready():
	collision_layer = 2
	collision_mask = 1
	floor_snap_length = 12.0
	col = CollisionShape2D.new()
	var shape = RectangleShape2D.new()
	shape.size = Vector2(25, 74 if is_girl else 62)
	col.shape = shape
	col.position.y = -shape.size.y / 2.0
	add_child(col)
	queue_redraw()

func _physics_process(dt):
	if game == null or game.mode != "playing":
		queue_redraw()
		return
	var axis = 0.0
	var jump = false
	crouching = forced_crouch
	if controlled:
		axis = Input.get_axis("left", "right")
		jump = Input.is_action_just_pressed("jump")
		crouching = Input.is_action_pressed("crouch")
	else:
		axis = ai_axis
		jump = ai_jump
		ai_jump = false
		if not is_on_floor() and leap_axis!=0: axis=leap_axis
		elif is_on_floor() and not jump: leap_axis=0
	var speed = 204.0
	if Input.is_action_pressed("sprint") and game.stamina > 2.0 and controlled and not crouching:
		speed = 286.0
		if abs(axis) > 0.1: game.stamina = maxf(0, game.stamina - dt * 18.0)
	if not controlled: speed = 235.0 if abs(game.player.position.x - position.x) > 100 else 204.0
	if not controlled and (jump or (not is_on_floor() and leap_axis!=0)): speed=270.0
	if crouching: speed = 82.0
	if controlled and action_time>0: axis=0; jump=false
	velocity.x = move_toward(velocity.x, axis * speed, (1250.0 if is_on_floor() else 600.0) * dt)
	if abs(axis) > 0.1: facing = sign(axis)
	if is_on_floor(): coyote = 0.13
	else: coyote -= dt
	if jump: jump_buffer = 0.14
	else: jump_buffer -= dt
	if jump_buffer > 0 and coyote > 0 and not crouching:
		velocity.y = -525.0
		if not controlled: leap_axis=axis
		coyote = 0
		jump_buffer = 0
		if controlled: game.stamina = maxf(0, game.stamina - 6)
	velocity.y += 1420.0 * dt
	if controlled and Input.is_action_just_released("jump") and not Input.is_action_pressed("jump") and velocity.y < -190: velocity.y *= 0.55
	var height = (45.0 if is_girl else 39.0) if crouching else (74.0 if is_girl else 62.0)
	col.shape.size.y = height
	col.position.y = -height/2
	move_and_slide()
	if is_on_floor() and not was_floor and velocity.y >= 0:
		land_time=.19
		game.spawn_dust(position, 5)
		if controlled: game.play_sfx("step", -19)
	was_floor = is_on_floor()
	if abs(velocity.x) > 8 and is_on_floor():
		phase += abs(velocity.x) * dt / 17.0
		footstep_clock += dt * abs(velocity.x) / 204.0
		if footstep_clock > 0.36:
			footstep_clock = 0
			if controlled: game.play_sfx("step", -26)
	queue_redraw()

func limb(a, b, c, width, color):
	draw_line(a,b,color,width,true)
	draw_line(b,c,color,width * .85,true)
	draw_circle(b,width*.46,color)
	draw_circle(c,width*.38,color)

func _draw_legacy():
	var s = 1.0 if is_girl else .84
	var crouch = 19.0 if crouching else 0.0
	var motion = clampf(abs(velocity.x)/175.0,0,1.35)
	var swing = sin(phase) * motion
	var bob = abs(cos(phase)) * motion * 1.6
	var hip = Vector2(0, -33 + crouch*.4 - bob)
	var shoulder = Vector2(facing * (4 if crouching else 0), -58 + crouch-bob)
	var head = shoulder + Vector2(facing*1.5,-15)
	var ink = Color("141a1a")
	var far = Color("232b29")
	var coat = Color("233232") if is_girl else Color("2b3030")
	var rim = Color("9a9d7a")
	if game != null:
		var bleak = float(game.chapter)/5.0
		coat = coat.lerp(Color("1b2328"), bleak)
		rim = rim.lerp(Color("73848d"), bleak)
	# All character drawings remain original, editable vector strokes.
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	var backfoot = Vector2(-swing*17, -maxf(0, -cos(phase))*motion*11)
	var frontfoot = Vector2(swing*17, -maxf(0, cos(phase))*motion*11)
	if not is_on_floor() and game != null and game.mode == "playing":
		backfoot = Vector2(-11*facing,-12)
		frontfoot = Vector2(14*facing,-4)
	limb(hip+Vector2(-3,0),Vector2(backfoot.x*.6,-17+crouch*.2),backfoot,8,far)
	draw_line(backfoot-Vector2(3,0),backfoot+Vector2(facing*9,1),ink,7,true)
	var backhand = shoulder + Vector2(swing*12,25)
	limb(shoulder,shoulder+Vector2(swing*7,14),backhand,6,far)
	var torso = PackedVector2Array([shoulder+Vector2(-9,0),shoulder+Vector2(8,0),hip+Vector2(12,3),hip+Vector2(-13,4)])
	draw_colored_polygon(torso,coat)
	draw_line(shoulder+Vector2(-8,1),hip+Vector2(-11,0),Color(rim,.27),1.4,true)
	limb(hip+Vector2(3,0),Vector2(frontfoot.x*.4+4,-16+crouch*.2),frontfoot,8,ink)
	draw_line(frontfoot-Vector2(3,0),frontfoot+Vector2(facing*10,1),ink,7,true)
	if is_girl:
		var dress = PackedVector2Array([shoulder+Vector2(-7,4),shoulder+Vector2(8,5),hip+Vector2(18+sin(phase)*2,12),hip+Vector2(-19,12)])
		draw_colored_polygon(dress,coat)
		draw_line(hip+Vector2(-19,12),hip+Vector2(17,12),Color(rim,.25),1,true)
	else:
		draw_line(shoulder+Vector2(4,6),hip+Vector2(5,1),Color(rim,.24),1,true)
		for i in range(3): draw_circle(shoulder+Vector2(5,10+i*7),1,Color("847353"))
	draw_line(shoulder+Vector2(0,-3),head,ink,8,true)
	draw_circle(head,11,ink)
	# Profile nose, fringe, and distinct hair silhouettes. No glowing eyes.
	draw_colored_polygon(PackedVector2Array([head+Vector2(facing*6,-3),head+Vector2(facing*14,1),head+Vector2(facing*8,5)]),ink)
	draw_arc(head,10.6,3.25,5.35,12,Color(rim,.44),1.2,true)
	if is_girl:
		for i in range(5):
			var b = head+Vector2(-facing*(7+sin(phase*.6+i*.3)*1.5),7+i*4)
			draw_circle(b,3.8-i*.25,ink)
		var ribbon = head + Vector2(-facing*10,20)
		draw_line(ribbon,ribbon+Vector2(-facing*9,4+sin(phase*.4)*2),Color("678f9d"),2.8,true)
		draw_line(ribbon,ribbon+Vector2(-facing*5,9),Color("567c90"),2.3,true)
	else:
		for i in range(6):
			var p = head + Vector2(-9+i*3,-7)
			draw_colored_polygon(PackedVector2Array([p,p+Vector2(3,-6-2*sin(i*4)),p+Vector2(7,2)]),ink)
	var hand = shoulder + Vector2(-swing*11,26)
	if hand_active: hand = to_local(contact_hand)/s
	limb(shoulder+Vector2(4,2),shoulder.lerp(hand,.55)+Vector2(3,2),hand,5.5,ink)
	draw_circle(hand,3,ink)
	draw_set_transform(Vector2.ZERO)

func painted_quad(points,uvs,texture,tint):
	draw_polygon(PackedVector2Array(points),PackedColorArray([tint]),PackedVector2Array(uvs),texture)

func painted_bone(a,b,width,source,tint):
	var axis=(b-a).normalized(); var side=Vector2(-axis.y,axis.x)*width/2
	var size=boy_atlas.get_size()
	var uv0=source.position/size; var uv1=source.end/size
	painted_quad([a-side,a+side,b+side,b-side],[uv0,Vector2(uv1.x,uv0.y),uv1,Vector2(uv0.x,uv1.y)],boy_atlas,tint)

func elbow_for(shoulder,hand,bend=1.0):
	var delta=hand-shoulder; var dist=clampf(delta.length(),1,25.8)
	var axis=delta.normalized(); var middle=shoulder+axis*dist*.5
	return middle+Vector2(-axis.y,axis.x)*sqrt(maxf(0,13*13-dist*dist*.25))*bend

func _draw():
	if drawn_pose.is_empty(): _draw_legacy(); return
	var s=1.0 if is_girl else .84
	var pose=[]
	for p in drawn_pose: pose.append(Vector2(p.x*facing,p.y))
	var hip=pose[0]; var shoulder=pose[1]; var head=pose[2]
	var fatigue=clampf((35-game.warmth)/35.0,0,1) if game!=null else 0.0
	shoulder+=Vector2(facing*fatigue*3,fatigue*3)
	head+=Vector2(facing*fatigue*4,fatigue*5)
	if land_time>0: shoulder.y+=sin(land_time/.19*PI)*3
	var bleak=float(game.chapter)/4.0 if game!=null else 0.0
	var tint=Color(.49,.51,.44).lerp(Color(.17,.22,.25),bleak)
	var near_ink=Color("172222"); var far_ink=Color("243030")
	var far_tint=tint.darkened(.31)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	# Far leg, arm, layered torso, near leg, profile, then contact arm.
	for label in ["far","near"]:
		if label=="near": continue
		var knee=pose[5]; var foot=pose[6]
		limb(hip+Vector2(-2,0),knee,foot,8,far_ink)
		painted_bone(hip+Vector2(-2,0),knee,10,Rect2(510,610,225,310),far_tint)
		painted_bone(knee,foot,8,Rect2(510,920,225,295),far_tint)
		draw_texture_rect_region(boy_atlas,Rect2(foot+Vector2(-5,-4),Vector2(15,10)*Vector2(facing,1)),Rect2(815,850,439,345),far_tint)
	limb(shoulder,pose[9],pose[10],6,far_ink)
	painted_bone(shoulder,pose[9],8,Rect2(950,0,250,585),far_tint)
	painted_bone(pose[9],pose[10],6,Rect2(110,620,220,570),far_tint)
	var torso=[shoulder+Vector2(-8,0),shoulder+Vector2(9,1),hip+Vector2(12,6),hip+Vector2(-13,6)]
	draw_colored_polygon(PackedVector2Array(torso),near_ink)
	if is_girl:
		var wind=sin(anim_time*5)*2+clampf(velocity.x/100,-3,3)
		torso=[shoulder+Vector2(-8,0),shoulder+Vector2(9,0),hip+Vector2(18-wind,11),hip+Vector2(-18-wind,10)]
		draw_colored_polygon(PackedVector2Array(torso),Color("203132"))
		# Original profile's painted cloth is registered onto an editable dress.
		painted_quad(torso,[Vector2(.34,.79),Vector2(.79,.83),Vector2(.81,.99),Vector2(.28,.99)],girl_profile,Color(.57,.62,.59).lerp(Color(.24,.29,.31),bleak))
		draw_line(shoulder+Vector2(-6,4),hip+Vector2(-14,8),Color(.47,.54,.48,.42),1,true)
	else:
		painted_quad(torso,[Vector2(540,45)/1280,Vector2(805,45)/1280,Vector2(805,575)/1280,Vector2(530,530)/1280],boy_atlas,tint)
	var near_knee=pose[3]; var near_foot=pose[4]
	limb(hip+Vector2(2,0),near_knee,near_foot,8,near_ink)
	if not is_girl:
		painted_bone(hip+Vector2(2,0),near_knee,10,Rect2(510,610,225,310),tint)
		painted_bone(near_knee,near_foot,8,Rect2(510,920,225,295),tint)
	if is_girl: draw_colored_polygon(PackedVector2Array(torso),Color(.09,.14,.15,.65))
	draw_texture_rect_region(boy_atlas,Rect2(near_foot+Vector2(-5,-4),Vector2(16,10)*Vector2(facing,1)),Rect2(815,850,439,345),tint)
	# Canonical profiles preserve the established faces; the stock mannequin is hidden.
	var head_tint=Color(.53,.56,.49).lerp(Color(.16,.22,.25),bleak)
	draw_set_transform(Vector2(head.x*s,head.y*s),0,Vector2(s*facing,s))
	if is_girl:
		draw_texture_rect_region(girl_profile,Rect2(-16,-15,34,40),Rect2(45,15,1090,1300),head_tint)
	else: draw_texture_rect_region(boy_atlas,Rect2(-15,-16,32,35),Rect2(0,0,440,490),head_tint)
	draw_set_transform(Vector2.ZERO,0,Vector2(s,s))
	var hand=pose[8]; var elbow=pose[7]
	if hand_active:
		hand=to_local(contact_hand)/s
		elbow=elbow_for(shoulder,hand,-facing)
	limb(shoulder,elbow,hand,5.7,near_ink)
	painted_bone(shoulder,elbow,8,Rect2(950,0,250,585),tint)
	painted_bone(elbow,hand,5.5,Rect2(110,620,220,570),tint)
	draw_circle(hand,2.6,Color(.29,.31,.25).lerp(near_ink,bleak))
	if is_girl:
		var ribbon=head+Vector2(-10*facing,18)
		draw_line(ribbon,ribbon+Vector2(-facing*(8+sin(anim_time*6)*2),3),Color("6e9aaa"),1.8,true)
	draw_set_transform(Vector2.ZERO)
