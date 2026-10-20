extends Node2D

const Child = preload("res://scripts/child.gd")
const World = preload("res://scripts/world.gd")
const HUD = preload("res://scripts/hud.gd")
var save_path = "user://journey_v1.json"
var settings_path = "user://settings_v1.json"
var mode = "menu"
var chapter = 0
var level = {}
var levels = []
var player
var boy
var camera: Camera2D
var world
var hud
var solids
var gate_bodies = []
var flags = {}
var memories = {}
var unlocked = 0
var rations = 2
var scrap = 0
var medicine = 1
var health = 100.0
var warmth = 100.0
var food = 100.0
var stamina = 100.0
var clock = 0.0
var playtime = 0.0
var shell_clock = 0.0
var shell_warning = 0.0
var flash = 0.0
var shake = 0.0
var exposure = 0.0
var invulnerable = 0.0
var checkpoint_x = 180.0
var trail = []
var dust = []
var chapter_card = 0.0
var message = ""
var message_time = 0.0
var prompt = ""
var near_item = {}
var sheltered = false
var muted = false
var reduced_motion = false
var volume = .6
var save_exists = false
var journey_active = false
var journey_completed = false
var settings_return = "menu"
var recovery_clock = 0.0
var sfx = {}
var ambience
var smoke_test = false
var qa_args = []
var death_count = 0
var test_log = []
var motion_data = {}
var cache_remaining = {}
const CAPACITY = {"rations":4,"scrap":6,"medicine":2}

func _ready():
	get_tree().auto_accept_quit=false
	qa_args=OS.get_cmdline_user_args()
	smoke_test="--smoke" in qa_args or "--traverse" in qa_args or "--survival" in qa_args or "--capture" in qa_args or "--capture-uhd" in qa_args
	motion_data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/motion/child_motion.json"))
	setup_input()
	for i in range(1,6):
		levels.append(JSON.parse_string(FileAccess.get_file_as_string("res://levels/%02d.json" % i)))
	load_save()
	world = World.new(); world.game=self; add_child(world)
	camera = Camera2D.new(); camera.position=Vector2(800,450); add_child(camera); camera.make_current()
	var layer = CanvasLayer.new(); layer.layer=20; add_child(layer)
	hud = HUD.new(); hud.game=self; hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); layer.add_child(hud)
	setup_audio()
	load_chapter(0,false)
	mode="menu"
	player.position.x=1240; boy.position.x=1188; camera.position.x=1050
	qa_args = OS.get_cmdline_user_args()
	if "--smoke" in qa_args:
		smoke_test=true
		call_deferred("run_smoke")
	if "--capture" in qa_args or "--capture-uhd" in qa_args:
		smoke_test=true
		call_deferred("capture_review")
	if "--traverse" in qa_args:
		smoke_test=true
		call_deferred("traverse_journey")
	if "--survival" in qa_args:
		call_deferred("run_survival_tests")
	if "--chapter" in qa_args:
		var idx = qa_args.find("--chapter")
		if idx+1<qa_args.size():
			load_chapter(clampi(int(qa_args[idx+1])-1,0,4)); mode="playing"

func setup_input():
	var bindings = {"left":[KEY_A,KEY_LEFT],"right":[KEY_D,KEY_RIGHT],"jump":[KEY_SPACE,KEY_W,KEY_UP],"crouch":[KEY_S,KEY_DOWN],"sprint":[KEY_SHIFT],"interact":[KEY_E],"companion":[KEY_Q],"pack":[KEY_TAB],"heal":[KEY_H],"restart":[KEY_R],"pause":[KEY_ESCAPE],"fullscreen":[KEY_F11,KEY_F],"mute":[KEY_M]}
	for action in bindings:
		if not InputMap.has_action(action): InputMap.add_action(action)
		for key in bindings[action]:
			var ev = InputEventKey.new(); ev.physical_keycode=key; InputMap.action_add_event(action,ev)
	var buttons = {"jump":JOY_BUTTON_A,"crouch":JOY_BUTTON_B,"interact":JOY_BUTTON_X,"companion":JOY_BUTTON_Y,"pause":JOY_BUTTON_START,"pack":JOY_BUTTON_BACK,"sprint":JOY_BUTTON_RIGHT_SHOULDER,"left":JOY_BUTTON_DPAD_LEFT,"right":JOY_BUTTON_DPAD_RIGHT}
	for action in buttons:
		var ev = InputEventJoypadButton.new(); ev.button_index=buttons[action]; InputMap.action_add_event(action,ev)
	for action in ["left","right"]:
		var ev = InputEventJoypadMotion.new(); ev.axis=JOY_AXIS_LEFT_X; ev.axis_value=-1.0 if action=="left" else 1.0; InputMap.action_add_event(action,ev)

func setup_audio():
	for name in ["step","collect","warning","blast","wheel"]: sfx[name]=load("res://assets/audio/"+name+".wav")
	ambience=AudioStreamPlayer.new()
	var stream=load("res://assets/audio/horizon.wav")
	stream.loop_mode=AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin=0; stream.loop_end=int(stream.get_length()*stream.mix_rate)
	ambience.stream=stream; ambience.volume_db=-14; add_child(ambience)
	if not smoke_test: ambience.play()
	apply_volume()

func play_sfx(name,db=-12):
	if not sfx.has(name) or smoke_test: return
	var a=AudioStreamPlayer.new(); a.stream=sfx[name]; a.volume_db=db; a.pitch_scale=randf_range(.94,1.04) if name=="step" else 1.0
	add_child(a); a.finished.connect(a.queue_free); a.play()

func apply_volume():
	AudioServer.set_bus_volume_db(0,linear_to_db(maxf(volume,.001)))
	AudioServer.set_bus_mute(0,muted)

func load_chapter(idx, announce=true):
	chapter=idx; level=levels[idx]
	if is_instance_valid(solids):
		remove_child(solids); solids.queue_free()
	solids=Node2D.new(); solids.name="Collisions"; add_child(solids)
	gate_bodies.clear()
	for p in level.ground+level.platforms: solid_rect(Rect2(p.x,p.y,p.w,p.h))
	# Keep the left edge physical. The right edge advances only with both children.
	solid_rect(Rect2(-60,-500,60,1800))
	solid_rect(Rect2(float(level.width),-500,60,1800))
	for g in level.gates:
		var body=solid_rect(Rect2(g.x-13,g.y-g.h,26,g.h))
		gate_bodies.append({"data":g,"body":body})
	if is_instance_valid(player): remove_child(player); player.queue_free()
	if is_instance_valid(boy): remove_child(boy); boy.queue_free()
	player=Child.new(); player.game=self; player.name="Girl"; player.position=Vector2(180,698); add_child(player)
	boy=Child.new(); boy.is_girl=false; boy.controlled=false; boy.game=self; boy.name="Boy"; boy.position=Vector2(123,698); add_child(boy)
	checkpoint_x=180; trail.clear(); shell_clock=0; shell_warning=0; exposure=0; invulnerable=2
	camera.position=Vector2(800,450); camera.reset_smoothing()
	chapter_card=5.5 if announce else 0
	if announce: announce_message(level.objective,7)

func solid_rect(rect):
	var body=StaticBody2D.new(); body.collision_layer=1; body.collision_mask=2
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=rect.size; shape.shape=box; shape.position=rect.position+rect.size/2
	body.add_child(shape); solids.add_child(body); return body

func new_journey():
	journey_active=true; journey_completed=false
	flags={}; memories={}; cache_remaining={}; rations=2; scrap=0; medicine=1
	health=100; warmth=100; food=100; stamina=100; playtime=0; death_count=0
	load_chapter(0); mode="playing"; write_save()

func continue_journey():
	journey_active=true
	load_save(true); mode="playing"

func _unhandled_input(event):
	if event.is_action_pressed("fullscreen"):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode()==DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
	if event.is_action_pressed("mute"): muted=not muted; apply_volume()
	if event.is_action_pressed("pause"):
		if mode=="playing": mode="pause"; hud.selected=0; write_save()
		elif mode in ["pause","inventory"]: mode="playing"
		elif mode in ["settings","chapters"]: mode=settings_return
	if event.is_action_pressed("pack") and mode in ["playing","inventory"]:
		mode="inventory" if mode=="playing" else "playing"
	if mode!="playing": return
	if event.is_action_pressed("interact"): interact()
	if event.is_action_pressed("companion"):
		boy.following=not boy.following
		announce_message("He’s coming. Keep a little room for him." if boy.following else "He’ll wait here. Don’t go too far.",3)
	if event.is_action_pressed("heal"):
		if medicine>0 and health<100:
			medicine-=1; health=minf(100,health+45); announce_message("A clean dressing. It will have to be enough.",4); write_save()
		elif medicine==0: announce_message("No medicine left. Search bags and cupboards.",4)
		else: announce_message("Save the dressing. You may need it later.",3)
	if event.is_action_pressed("restart"): recover(false)

func _process(dt):
	clock+=dt; flash=move_toward(flash,0,dt*2.5); shake=move_toward(shake,0,dt*11)
	message_time=maxf(0,message_time-dt)
	if mode=="playing": chapter_card=maxf(0,chapter_card-dt)
	if mode=="recovering":
		recovery_clock-=dt
		if recovery_clock<=0: respawn()
	var target=clampf(player.position.x+235,800,float(level.width)-800)
	if mode=="menu": target=1050
	camera.position.x=lerpf(camera.position.x,target,1-exp(-dt*3.5))
	camera.position.y=450+clampf((player.position.y-700)*.14,-45,35)
	if not reduced_motion and shake>0: camera.offset=Vector2(sin(clock*63),cos(clock*51))*shake
	else: camera.offset=Vector2.ZERO
	for p in dust:
		p.p+=p.v*dt; p.v.y-=dt*8; p.life-=dt
	dust=dust.filter(func(p): return p.life>0)

func _physics_process(dt):
	if mode!="playing": return
	playtime+=dt; invulnerable=maxf(0,invulnerable-dt)
	if not Input.is_action_pressed("sprint") or abs(player.velocity.x)<15: stamina=minf(100,stamina+dt*15)
	food=maxf(0,food-dt*.38)
	sheltered=is_covered(player) and is_covered(boy)
	var cold=float(level.cold) * (.22 if sheltered else 1.0)
	warmth=clampf(warmth-dt*cold,0,100)
	if food<12 or warmth<8: health=maxf(0,health-dt*.7)
	update_companion(dt)
	for gb in gate_bodies:
		gb.body.collision_layer=0 if gate_open(gb.data) else 1
	update_prompt()
	for m in level.memories:
		if not memories.has(m.id) and player.position.distance_to(Vector2(m.x,m.y))<62:
			memories[m.id]=m.text; play_sfx("collect",-13); announce_message(m.text,7); write_save()
	for cp in level.checkpoints:
		if player.position.x>cp and cp>checkpoint_x and abs(player.position.x-boy.position.x)<240:
			checkpoint_x=cp; write_save()
	if level.has("danger"):
		var in_danger=player.position.x>level.danger[0] and player.position.x<level.danger[1]
		if in_danger:
			shell_clock+=dt
			shell_warning=clampf((shell_clock-8.2)/2.6,0,1)
			if shell_clock>=8.2 and shell_clock-dt<8.2:
				play_sfx("warning",-14); announce_message("The sky is warning you. Reach cover. Stay low.",3)
			if shell_clock>=10.8:
				flash=1; shake=8; play_sfx("blast",-9)
				if not sheltered: hurt(65,"The shockwave caught them in the open.")
				shell_clock=0; shell_warning=0
		else: shell_clock=maxf(0,shell_clock-dt*2); shell_warning=0
	if level.get("searchlight",false) and player.position.x>650 and player.position.x<4600:
		var caught=(abs(player.position.x-beam_x())<130 and not is_covered(player)) or (abs(boy.position.x-beam_x())<130 and not is_covered(boy))
		exposure=clampf(exposure+dt*(1 if caught else -2.0),0,1.8)
		if exposure>=1.75:
				hurt(34,"They saw movement. Keep both children low behind cover."); exposure=0
	if player.position.y>1030 or boy.position.y>1050:
		recover(true,"The road gave way. Try again, together.")
	if health<=0: recover(true,"They need a safer way through.")
	if player.position.x>float(level.width)-110:
		if abs(player.position.x-boy.position.x)<180:
			if chapter<4:
				unlocked=maxi(unlocked,chapter+1); load_chapter(chapter+1); write_save()
		else:
			player.position.x=float(level.width)-115
			announce_message("Wait for him. Press Q to call him back.",2)

func update_companion(_dt):
	trail.append(Vector3(player.position.x,player.position.y,1 if player.crouching else 0))
	if trail.size()>2000: trail.pop_front()
	boy.forced_crouch=player.crouching and abs(player.position.x-boy.position.x)<160
	boy.ai_axis=0
	var gap=player.position.x-boy.position.x
	if boy.following:
		if abs(gap)>42: boy.ai_axis=sign(gap)
		# Jump from the same edge, before walking into the void. Physics stays native.
		var forward=sign(gap)
		if boy.is_on_floor() and abs(gap)>55:
			var ahead=boy.position.x+forward*22
			if not ground_at(ahead): boy.ai_jump=true
			for p in level.platforms:
				if ahead>p.x-4 and ahead<p.x+p.w and p.y<boy.position.y-12 and p.y>boy.position.y-145: boy.ai_jump=true
			for point in trail:
				if abs(point.x-boy.position.x)<22 and point.y<boy.position.y-48:
					boy.ai_jump=true; break
		if abs(gap)>390 and boy.is_on_floor(): announce_message("He’s falling behind. Slow down and call him [Q].",2)
	var close=abs(gap)<49 and abs(player.position.y-boy.position.y)<17 and not player.crouching
	player.hand_active=close; boy.hand_active=close
	var hand=(player.position+boy.position)*.5+Vector2(0,-47)
	player.contact_hand=hand; boy.contact_hand=hand

func ground_at(x):
	for g in level.ground:
		if x>=g.x and x<=g.x+g.w: return true
	return false

func is_covered(child):
	for c in level.covers:
		if abs(child.position.x-c.x)<c.w/2.0 and (child.crouching or c.kind=="tent") and child.position.y>640: return true
	return false

func beam_x(): return 2650+sin(clock*.29)*1970

func gate_open(g):
	if flags.get(g.key,false): return true
	if g.has("plate"):
		return (abs(player.position.x-g.plate)<45 and player.position.y>680) or (abs(boy.position.x-g.plate)<45 and boy.position.y>680)
	return false

func update_prompt():
	prompt=""; near_item={}
	for p in level.interact:
		if p.kind=="cache" and flags.get(p.id,false): continue
		if p.kind in ["wheel","latch","repair"] and flags.get(p.id,false): continue
		if abs(player.position.x-p.x)<86 and abs(player.position.y-p.y)<100:
			near_item=p; prompt="E   "+p.label; break
	if prompt=="":
		for tutorial in level.tutorials:
			if abs(player.position.x-tutorial.x)<180: prompt=tutorial.text; break

func interact():
	if player.action_time>0: return
	if near_item.is_empty(): return
	var p=near_item
	match p.kind:
		"cache":
			if flags.get(p.id,false): return
			var remaining=cache_remaining.get(p.id,{"rations":int(p.get("rations",0)),"scrap":int(p.get("scrap",0)),"medicine":int(p.get("medicine",0))})
			var taken={}
			for resource in CAPACITY:
				var amount=mini(int(remaining.get(resource,0)),int(CAPACITY[resource])-int(get(resource)))
				taken[resource]=amount; set(resource,int(get(resource))+amount); remaining[resource]=int(remaining.get(resource,0))-amount
			cache_remaining[p.id]=remaining
			flags[p.id]=int(remaining.rations)+int(remaining.scrap)+int(remaining.medicine)==0
			var found=[]
			if taken.rations>0: found.append("%d food"%taken.rations)
			if taken.scrap>0: found.append("%d salvage"%taken.scrap)
			if taken.medicine>0: found.append("%d medicine"%taken.medicine)
			if found.is_empty(): announce_message("The pack is full. Leave this here for the way back.",4); return
			announce_message("Found "+", ".join(found)+". Share what you can carry.",4); play_sfx("collect")
		"wheel","latch":
			flags[p.id]=true; announce_message("The way is open. Call him through [Q].",4); play_sfx("wheel")
		"repair":
			if scrap>=2:
				scrap-=2; flags[p.id]=true; announce_message("A door that closes. For tonight, that is enough.",5); play_sfx("wheel")
			else: announce_message("Two pieces of salvage. Search the tool roll and the rucksack.",5)
		"fire":
			if abs(player.position.x-boy.position.x)>180:
				announce_message("Bring him close before resting [Q].",4); return
			if rations>0:
				rations-=1; food=minf(100,food+36); warmth=minf(100,warmth+52); health=minf(100,health+22)
				announce_message("They share a little bread and wait for their hands to warm.",6)
			else:
				warmth=minf(100,warmth+8); announce_message("A little warmth, but nothing left to eat.",4)
			checkpoint_x=maxf(180,player.position.x); shell_clock=0
		"end":
			if abs(player.position.x-boy.position.x)<120:
				mode="ending"; journey_completed=true; unlocked=4; write_save(); play_sfx("collect",-19)
			else: announce_message("Wait for him. You made it this far together.",4)
	player.action_time=.75; boy.action_time=.75 if p.kind=="fire" else 0.0
	write_save(); update_prompt()

func hurt(amount,reason):
	if invulnerable>0: return
	health=maxf(0,health-amount); invulnerable=3; flash=.65; shake=5; announce_message(reason,4)
	player.hit_time=.35; boy.hit_time=.35

func recover(count=true,reason="Take another breath. Try a different path."):
	if mode!="playing": return
	if count: death_count+=1
	mode="recovering"; recovery_clock=1.4; announce_message(reason,4)

func respawn():
	player.position=Vector2(checkpoint_x,695); boy.position=Vector2(maxf(40,checkpoint_x-54),695)
	player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO; boy.following=true
	trail.clear(); health=maxf(55,health); warmth=maxf(35,warmth); food=maxf(30,food); stamina=100
	shell_clock=0; shell_warning=0; invulnerable=4; exposure=0; mode="playing"
	camera.position.x=clampf(checkpoint_x+235,800,float(level.width)-800)
	# Existing supplies and puzzle progress persist so failure never consumes a finite cache.

func announce_message(text,duration=4): message=text; message_time=duration

func spawn_dust(pos,count):
	for i in range(count): dust.append({"p":pos+Vector2(randf_range(-10,10),-3),"v":Vector2(randf_range(-20,20),randf_range(-16,-3)),"size":randf_range(1,4),"life":randf_range(.3,.8)})

func write_save():
	if smoke_test: return
	var prefs=FileAccess.open(settings_path,FileAccess.WRITE)
	if prefs: prefs.store_string(JSON.stringify({"volume":volume,"muted":muted,"reduced_motion":reduced_motion})); prefs.close()
	if not journey_active: return
	var data={"schema":1,"chapter":chapter,"checkpoint":checkpoint_x,"flags":flags,"memories":memories,"cache_remaining":cache_remaining,"unlocked":unlocked,"rations":rations,"scrap":scrap,"medicine":medicine,"health":health,"warmth":warmth,"food":food,"playtime":playtime,"volume":volume,"muted":muted,"reduced_motion":reduced_motion,"completed":journey_completed}
	var f=FileAccess.open(save_path+".tmp",FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data,"\t")); f.close()
		DirAccess.rename_absolute(save_path+".tmp",save_path)
		save_exists=true

func load_save(resume=false):
	if FileAccess.file_exists(settings_path):
		var prefs=JSON.parse_string(FileAccess.get_file_as_string(settings_path))
		if prefs is Dictionary:
			volume=clampf(float(prefs.get("volume",.6)),0,1); muted=prefs.get("muted",false); reduced_motion=prefs.get("reduced_motion",false)
	if not FileAccess.file_exists(save_path): return
	var d=JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if not d is Dictionary or d.get("schema",0)!=1: return
	save_exists=true; unlocked=clampi(int(d.get("unlocked",0)),0,4)
	if not resume: return
	journey_active=true; journey_completed=d.get("completed",false)
	flags=d.get("flags",{}); memories=d.get("memories",{})
	cache_remaining=d.get("cache_remaining",{})
	rations=clampi(int(d.get("rations",2)),0,4); scrap=clampi(int(d.get("scrap",0)),0,6); medicine=clampi(int(d.get("medicine",1)),0,2)
	health=clampf(float(d.get("health",100)),30,100); warmth=clampf(float(d.get("warmth",100)),20,100); food=clampf(float(d.get("food",100)),20,100)
	playtime=float(d.get("playtime",0)); load_chapter(clampi(int(d.get("chapter",0)),0,4))
	checkpoint_x=clampf(float(d.get("checkpoint",180)),180,float(level.width)-250); respawn(); apply_volume()

func _notification(what):
	if what==NOTIFICATION_WM_CLOSE_REQUEST: quit_game()
	if what==NOTIFICATION_APPLICATION_FOCUS_OUT and mode=="playing" and not smoke_test and not "--capture" in qa_args and not "--traverse" in qa_args: mode="pause"

func quit_game(code=0):
	write_save()
	if is_instance_valid(ambience): ambience.stop(); ambience.stream=null
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().quit(code)

func assert_check(name,condition,details=""):
	test_log.append({"check":name,"passed":condition,"details":details})
	if not condition: push_error("TEST FAILED: "+name+" "+str(details))

func report_path(file):
	var idx=qa_args.find("--evidence-dir")
	var folder="res://evidence" if OS.has_feature("editor") else "user://qa_evidence"
	if idx>=0 and idx+1<qa_args.size(): folder=qa_args[idx+1]
	DirAccess.make_dir_recursive_absolute(folder)
	return folder.path_join(file)

func run_smoke():
	# Actual engine/physics checks. No user save is touched in test mode.
	mode="playing"
	for i in range(5):
		load_chapter(i,false); mode="playing"
		await get_tree().physics_frame; await get_tree().physics_frame
		assert_check("chapter_%d_geometry"%(i+1),solids.get_child_count()==level.ground.size()+level.platforms.size()+level.gates.size()+2)
		for frame in range(30): await get_tree().physics_frame
		assert_check("chapter_%d_ground_contact"%(i+1),player.is_on_floor() and boy.is_on_floor())
		Input.action_press("right")
		var start=player.position.x
		for frame in range(90): await get_tree().physics_frame
		Input.action_release("right")
		assert_check("chapter_%d_native_movement"%(i+1),player.position.x-start>220)
		assert_check("chapter_%d_companion_follows"%(i+1),boy.position.x>start+120 and abs(boy.position.x-player.position.x)<160)
		Input.action_press("jump")
		for frame in range(12): await get_tree().physics_frame
		Input.action_release("jump")
		assert_check("chapter_%d_native_jump"%(i+1),player.position.y<670)
		for frame in range(65): await get_tree().physics_frame
		assert_check("chapter_%d_jump_lands"%(i+1),player.is_on_floor())
		for p in level.interact:
			player.position=Vector2(p.x,699); boy.position=Vector2(p.x-50,699); boy.velocity=Vector2.ZERO; player.velocity=Vector2.ZERO
			for frame in range(4): await get_tree().physics_frame
			near_item=p
			player.action_time=0
			if p.kind=="cache": rations=0; scrap=0; medicine=0
			if p.kind=="repair": scrap=maxi(2,scrap)
			if p.kind=="fire": warmth=40; rations=maxi(1,rations)
			interact()
			if p.kind in ["cache","wheel","repair","latch"]: assert_check("chapter_%d_%s_%s"%[i+1,p.kind,p.id],flags.get(p.id,false))
			if p.kind=="fire": assert_check("chapter_%d_shelter_rest"%(i+1),warmth>80)
			if p.kind=="end": assert_check("story_ending",mode=="ending"); mode="playing"
		if i==1:
			flags.erase("forest_latch"); boy.position=Vector2(2230,699); boy.following=false; player.position=Vector2(2480,699)
			assert_check("companion_pressure_plate_opens_gate",gate_open(level.gates[0]))
			boy.position.x=2000; assert_check("unoccupied_plate_closes_gate",not gate_open(level.gates[0]))
		if level.has("danger"):
			var c=level.covers[1]
			player.position=Vector2(c.x+24,699); boy.position=Vector2(c.x-24,699); boy.following=true
			Input.action_press("crouch")
			for frame in range(3): await get_tree().physics_frame
			assert_check("chapter_%d_both_in_cover"%(i+1),is_covered(player) and is_covered(boy))
			invulnerable=0; var before=health; shell_clock=10.78
			for frame in range(4): await get_tree().physics_frame
			assert_check("chapter_%d_cover_blocks_blast"%(i+1),health==before)
			Input.action_release("crouch")
			player.position.x=c.x+350; boy.position.x=c.x+300; invulnerable=0; before=health; shell_clock=10.78
			for frame in range(4): await get_tree().physics_frame
			assert_check("chapter_%d_exposure_damages"%(i+1),health<before)
		invulnerable=0; checkpoint_x=level.checkpoints[1]; player.position.y=1100
		await get_tree().physics_frame; await get_tree().physics_frame
		assert_check("chapter_%d_fall_recovery"%(i+1),mode=="recovering")
		respawn(); assert_check("chapter_%d_checkpoint_respawn"%(i+1),abs(player.position.x-checkpoint_x)<1 and boy.following)
	# Real disk persistence in unique, isolated user files; never overwrite a
	# player's journey. Exercise readback, resume, and title-screen preservation.
	save_path="user://qa_journey_"+str(Time.get_ticks_usec())+".json"
	settings_path=save_path+".settings"
	smoke_test=false; journey_active=true; chapter=3; checkpoint_x=3020; flags["qa_persist"]=true; rations=2; warmth=44; health=63
	write_save()
	assert_check("atomic_save_file_exists",FileAccess.file_exists(save_path) and not FileAccess.file_exists(save_path+".tmp"))
	flags={}; rations=0; load_save(true)
	assert_check("save_resume_readback",chapter==3 and checkpoint_x==3020 and flags.get("qa_persist",false) and rations==2 and warmth==44)
	journey_active=false; var previous=FileAccess.get_file_as_string(save_path); chapter=0; write_save()
	assert_check("title_screen_preserves_journey",FileAccess.get_file_as_string(save_path)==previous)
	DirAccess.remove_absolute(save_path); DirAccess.remove_absolute(settings_path); smoke_test=true
	var passed=true
	for result in test_log:
		if not result.passed: passed=false
	var report={"engine":Engine.get_version_info(),"checks":test_log,"all_passed":passed,"method":"Actual Godot runtime: native CharacterBody2D physics, Input action simulation, authored interactions, cover and damage, death recovery. Targeted interaction checks reposition actors; these are not a complete human playthrough."}
	var f=FileAccess.open(report_path("runtime_smoke.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("WTSC_SMOKE_RESULT ",JSON.stringify(report))
	call_deferred("quit_game",0 if passed else 1)

func capture_review():
	if "--capture-uhd" in qa_args:
		# An actual UHD render target avoids desktop/window-size clamping.
		var target=SubViewport.new(); target.size=Vector2i(3840,2160)
		target.size_2d_override=Vector2i(1600,900); target.size_2d_override_stretch=true
		target.render_target_update_mode=SubViewport.UPDATE_ALWAYS
		get_tree().root.add_child(target); reparent(target); camera.make_current()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(report_path("00_title.png"))
	for i in range(5):
		load_chapter(i,false); mode="playing"; chapter_card=0
		message_time=0
		player.position=Vector2([1850,2210,2000,1830,2130][i],696)
		boy.position=player.position-Vector2(54,0)
		if i>=2: Input.action_press("crouch")
		for frame in range(45): await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(report_path("0%d_chapter.png"%(i+1)))
		Input.action_release("crouch")
	print("WTSC_CAPTURE_COMPLETE")
	call_deferred("quit_game")

func traverse_journey():
	# A continuous Input-driven traversal. No actor repositioning, collision bypass,
	# invulnerability changes, skipped gates, or resource grants occur here.
	new_journey()
	var reached=[]
	var last_chapter=-1
	var farthest=0.0
	var stalled=0
	var jump_hold=0
	var jump_sprinting=false
	var completed=false
	var failure=""
	var searched={}
	for frame in range(21000):
		await get_tree().physics_frame
		if mode=="ending": completed=true; break
		if mode=="recovering": continue
		if chapter!=last_chapter:
			last_chapter=chapter; reached.append(chapter+1); farthest=0; stalled=0
			print("TRAVERSE_CHAPTER ",chapter+1)
		if player.position.x>farthest+3: farthest=player.position.x; stalled=0
		else: stalled+=1
		if stalled>600:
			failure="Stalled in chapter %d at x=%d, boy=%d, y=%d"%[chapter+1,player.position.x,boy.position.x,player.position.y]; break
		Input.action_release("left"); Input.action_press("right")
		Input.action_release("crouch"); Input.action_release("sprint")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		# Stop for a usable supply cache, wheel, or fire. Interactions use the same
		# distance-gated prompt and inventory code as the player.
		update_prompt()
		if not near_item.is_empty():
			var p=near_item
			if p.kind in ["wheel","latch","repair","end"] or (p.kind=="cache" and not searched.has(p.id)):
				interact()
				if p.kind=="cache" and player.action_time>0: searched[p.id]=true
			if p.kind=="fire" and abs(player.position.x-boy.position.x)<120 and rations>0 and (health<85 or warmth<65 or food<55): interact()
		if health<52 and medicine>0:
			medicine-=1; health=minf(100,health+45)
		# Solve the logging gate through the companion's actual plate contact.
		if chapter==1 and not flags.get("forest_latch",false):
			if player.position.x>2280 and boy.following:
				Input.action_release("right")
				if abs(boy.position.x-2230)<39: boy.following=false
			if not boy.following: Input.action_press("right")
		elif not boy.following: boy.following=true
		if abs(player.position.x-boy.position.x)>155 and boy.following:
			Input.action_release("right")
		# Jump from the physical edge and from steps. Full jump is held to apex.
		var need_jump=false
		var gap_leap=false
		if player.is_on_floor():
			if not ground_at(player.position.x+30): need_jump=true; gap_leap=true; Input.action_press("sprint")
			for p in level.platforms:
				if p.x-player.position.x>0 and p.x-player.position.x<45 and p.y<player.position.y-12 and p.y>player.position.y-110: need_jump=true
		if need_jump and jump_hold==0:
			Input.action_press("jump"); jump_hold=24; jump_sprinting=gap_leap
		# Keep sprint through the jump instead of braking in the air over a gap.
		if not player.is_on_floor() and jump_sprinting: Input.action_press("sprint")
		# Read the shell warning and stop in existing cover when it is reachable.
		if shell_warning>.05:
			for c in level.covers:
				if abs(player.position.x-c.x)<c.w*.35 and abs(boy.position.x-c.x)<c.w*.45:
					Input.action_release("right"); Input.action_press("crouch"); break
		if frame%1800==0: print("TRAVERSE_PROGRESS ",chapter+1," ",int(player.position.x)," boy=",int(boy.position.x)," deaths=",death_count)
	for action in ["left","right","jump","sprint","crouch"]: Input.action_release(action)
	var report={"completed":completed,"chapters_reached":reached,"failure":failure,"deaths":death_count,"simulated_seconds":playtime,"rations_remaining":rations,"medicine_remaining":medicine,"health":health,"method":"Continuous native physics traversal driven with Input actions; no position changes, gate bypass, resource grants or damage immunity. Interactions use the live distance-gated game functions. This is automated traversal, not human artistic acceptance."}
	var f=FileAccess.open(report_path("continuous_traversal.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("TRAVERSE_RESULT ",JSON.stringify(report))
	call_deferred("quit_game",0 if completed else 1)

func run_survival_tests():
	# Deliberate hazard scenarios measure outcomes for each child separately.
	# These targeted setups are independent of the no-teleport journey traversal.
	var measurements=[]
	load_chapter(2,false); mode="playing"
	var c=level.covers[2]
	for scenario in ["girl_only","boy_only","both"]:
		health=100; invulnerable=0; shell_clock=0; exposure=0
		player.position=Vector2(c.x+(c.w*.5+23 if scenario=="boy_only" else 20),699)
		boy.position=Vector2(c.x+(c.w*.5+23 if scenario=="girl_only" else -20),699)
		boy.following=false; player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO
		Input.action_press("crouch")
		for frame in range(4): await get_tree().physics_frame
		var girl_safe=is_covered(player); var boy_safe=is_covered(boy)
		if scenario=="boy_only":
			# This cover is a low wall: the waiting child must also stay crouched.
			boy.forced_crouch=true; boy.crouching=true
			boy_safe=is_covered(boy)
		shell_clock=10.78
		for frame in range(4): await get_tree().physics_frame
		measurements.append({"scenario":scenario,"girl_in_cover":girl_safe,"boy_in_cover":boy_safe,"strength_after_blast":health})
		assert_check("blast_"+scenario,health==100 if scenario=="both" else health==35,str(health))
	Input.action_release("crouch")
	health=100; invulnerable=0; player.position=Vector2(3350,699); boy.position=Vector2(3300,699); boy.following=false
	for frame in range(3): await get_tree().physics_frame
	for hit in range(2):
		invulnerable=0; shell_clock=10.78
		for frame in range(4): await get_tree().physics_frame
	assert_check("ignoring_two_blasts_ends_attempt",mode=="recovering" and health==0)
	measurements.append({"scenario":"ignore_two_warnings","strength":health,"mode":mode})
	respawn(); health=100; invulnerable=0; shell_clock=0
	# Isolate detection of the boy while the girl is safely inside a tent.
	c=level.covers[1]; player.position=Vector2(c.x,699); boy.position=Vector2(c.x+225,699); boy.following=false
	player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO
	clock=asin((float(c.x)+225-2650)/1970.0)/.29
	exposure=1.74
	for frame in range(4): await get_tree().physics_frame
	assert_check("searchlight_detects_exposed_boy",is_covered(player) and not is_covered(boy) and health==66,str(health))
	measurements.append({"scenario":"girl_sheltered_boy_detected","strength":health})
	load_chapter(4,false); mode="playing"; health=100; warmth=0; food=0
	for frame in range(122): await get_tree().physics_frame
	assert_check("cold_and_hunger_reduce_strength",health<99 and health>95,str(health))
	measurements.append({"scenario":"two_seconds_cold_and_hungry","strength":health})
	var fire=level.interact[1]
	player.position=Vector2(fire.x,699); boy.position=Vector2(fire.x-42,699); boy.following=false
	health=40; warmth=20; food=20; rations=1; near_item=fire; player.action_time=0
	interact()
	assert_check("rest_spends_finite_ration",rations==0 and health==62 and warmth==72 and food==56)
	var p=level.interact[0]; flags.erase(p.id); cache_remaining.erase(p.id)
	player.position=Vector2(p.x,699); boy.position=Vector2(p.x-42,699); rations=4; medicine=2; near_item=p; player.action_time=0
	interact()
	assert_check("full_pack_leaves_supplies_in_world",not flags.get(p.id,false) and rations==4 and medicine==2)
	rations=0; medicine=0; near_item=p; player.action_time=0; interact()
	var after_food=rations; var after_med=medicine
	near_item=p; player.action_time=0; interact()
	assert_check("searched_cache_cannot_duplicate_supplies",rations==after_food and medicine==after_med and flags.get(p.id,false))
	load_chapter(0,false); mode="playing"; stamina=0; player.action_time=0
	Input.action_press("right"); Input.action_press("sprint")
	for frame in range(40): await get_tree().physics_frame
	assert_check("exhaustion_prevents_sprinting",player.velocity.x<=204.1 and stamina<1,str(player.velocity.x))
	Input.action_release("right"); Input.action_release("sprint")
	boy.following=false; boy.position=Vector2(4500,699); player.position=Vector2(5150,699); player.velocity=Vector2.ZERO
	for frame in range(4): await get_tree().physics_frame
	assert_check("chapter_exit_waits_for_both_children",chapter==0 and player.position.x<=5085)
	load_chapter(4,false); mode="playing"; var end=level.interact[-1]
	player.position=Vector2(end.x,699); boy.position=Vector2(end.x-400,699); near_item=end; player.action_time=0; interact()
	assert_check("ending_requires_companion",mode=="playing")
	boy.position=Vector2(end.x-42,699); near_item=end; player.action_time=0; interact()
	assert_check("ending_accepts_reunited_children",mode=="ending")
	var passed=true
	for result in test_log:
		if not result.passed: passed=false
	var report={"all_passed":passed,"checks":test_log,"measurements":measurements,"scope":"Real Godot physics and damage/rest/cache rules. Deliberate scenario setup repositions actors and sets initial conditions; continuous_traversal.json tests uninterrupted navigation separately."}
	var f=FileAccess.open(report_path("survival_consequences.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("SURVIVAL_RESULT ",JSON.stringify(report))
	call_deferred("quit_game",0 if passed else 1)
