extends Node2D

const LastHouse = preload("res://scripts/last_house.gd")
const Child = preload("res://scripts/child_v2.gd")
const Pushable = preload("res://scripts/pushable.gd")
const World = preload("res://scripts/world.gd")
const HUD = preload("res://scripts/hud.gd")
const Foreground = preload("res://scripts/foreground.gd")
const SideRouteChecks = preload("res://scripts/side_route_checks.gd")
var journey_save_path="user://journey_v3.json"
var rehearsal_save_path="user://freight_crossing_v040.json"
var save_path = "user://journey_v3.json"
var save_notice=""
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
var companion_jumps=[]
var companion_alert_clock=0.0
var section_preview=false
var slice_active=false
var last_house
var last_house_save_path="user://last_house_v050.json"
var child_detection={"Girl":0.0,"Boy":0.0}
var child_injury={"Girl":0.0,"Boy":0.0}
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
var pending_action={}
var action_progress=0.0
var action_duration=0.0
var bridge_bodies=[]
var pushables=[]
var wetness=0.0
var action_interrupts=0
var encounter_events=[]
var impacts=[]
var water_offsets={}
var step_sounds={}
var hazard_exposure={}
var hazard_cues={}
var sector_seen={}
var lane_warning=""
var wind_strain=false

func _ready():
	get_tree().auto_accept_quit=false
	DisplayServer.window_set_title("When the Sky Clears · Development 0.5.0")
	qa_args=OS.get_cmdline_user_args()
	smoke_test="--smoke" in qa_args or "--traverse" in qa_args or "--survival" in qa_args or "--encounters" in qa_args or "--motion" in qa_args or "--capture" in qa_args or "--capture-uhd" in qa_args or "--journey-checks" in qa_args or "--capture-new" in qa_args or "--side-routes" in qa_args
	motion_data=JSON.parse_string(FileAccess.get_file_as_string("res://assets/motion/child_motion.json"))
	if "--crossing-checks" in qa_args or "--crossing-capture" in qa_args or "--trust-checks" in qa_args: smoke_test=true
	last_house=LastHouse.new(self)
	if "--slice-checks" in qa_args or "--slice-capture" in qa_args: smoke_test=true
	setup_input()
	for i in range(1,6):
		levels.append(JSON.parse_string(FileAccess.get_file_as_string("res://levels/%02d.json" % i)))
	load_save()
	world = World.new(); world.game=self; add_child(world)
	var foreground=Foreground.new(); foreground.game=self; foreground.z_index=10; add_child(foreground)
	camera = Camera2D.new(); camera.position=Vector2(800,450); camera.zoom=Vector2(1.12,1.12); add_child(camera); camera.make_current()
	var layer = CanvasLayer.new(); layer.layer=20; add_child(layer)
	hud = HUD.new(); hud.game=self; hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); layer.add_child(hud)
	setup_audio()
	load_chapter(0,false)
	mode="menu"
	player.position.x=1240; boy.position.x=1188; camera.position.x=1050
	qa_args = OS.get_cmdline_user_args()
	if "--last-house" in qa_args: last_house.start.call_deferred(true)
	if "--slice-checks" in qa_args: load("res://scripts/last_house_checks.gd").run.call_deferred(self)
	if "--slice-capture" in qa_args: load("res://scripts/last_house_checks.gd").capture.call_deferred(self)
	if "--trust-checks" in qa_args: load("res://scripts/trust_checks.gd").run.call_deferred(self)
	if "--crossing-checks" in qa_args: call_deferred("run_crossing_checks")
	if "--crossing-capture" in qa_args: call_deferred("capture_crossing")
	if "--freight-crossing" in qa_args: call_deferred("start_crossing")
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
	if "--encounters" in qa_args:
		smoke_test=true; call_deferred("run_encounter_tests")
	if "--motion" in qa_args: call_deferred("run_motion_review")
	if "--journey-checks" in qa_args: call_deferred("run_journey_checks")
	if "--capture-new" in qa_args: call_deferred("capture_new_journey")
	if "--side-routes" in qa_args: SideRouteChecks.run.call_deferred(self)
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
	var buttons = {"jump":JOY_BUTTON_A,"crouch":JOY_BUTTON_B,"interact":JOY_BUTTON_X,"companion":JOY_BUTTON_Y,"pause":JOY_BUTTON_START,"pack":JOY_BUTTON_BACK,"sprint":JOY_BUTTON_RIGHT_SHOULDER,"heal":JOY_BUTTON_LEFT_SHOULDER,"left":JOY_BUTTON_DPAD_LEFT,"right":JOY_BUTTON_DPAD_RIGHT}
	for action in buttons:
		var ev = InputEventJoypadButton.new(); ev.button_index=buttons[action]; InputMap.action_add_event(action,ev)
	for action in ["left","right"]:
		var ev = InputEventJoypadMotion.new(); ev.axis=JOY_AXIS_LEFT_X; ev.axis_value=-1.0 if action=="left" else 1.0; InputMap.action_add_event(action,ev)

func setup_audio():
	for material in ["grass","concrete","wood"]:
		step_sounds[material]=[]
		for variant in range(5): step_sounds[material].append(load("res://assets/audio/foley/footstep_%s_%03d.ogg"%[material,variant]))
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

func play_step(pos,db=-20):
	if smoke_test: return
	var material="concrete" if chapter>=2 else "grass"
	for bridge in level.get("bridges",[]):
		if pos.x>bridge.x and pos.x<bridge.x+bridge.w: material="wood"
	for p in level.platforms:
		if pos.x>p.x and pos.x<p.x+p.w and pos.y<p.y+7: material="wood" if p.kind in ["log","crate"] else "concrete"
	var a=AudioStreamPlayer.new(); a.stream=step_sounds[material].pick_random(); a.volume_db=db; a.pitch_scale=randf_range(.93,1.07)
	add_child(a); a.finished.connect(a.queue_free); a.play()

func apply_volume():
	AudioServer.set_bus_volume_db(0,linear_to_db(maxf(volume,.001)))
	AudioServer.set_bus_mute(0,muted)

func load_chapter(idx, announce=true):
	chapter=idx; level=last_house.data if slice_active and idx==2 else levels[idx]
	if is_instance_valid(solids):
		remove_child(solids); solids.queue_free()
	solids=Node2D.new(); solids.name="Collisions"; add_child(solids)
	gate_bodies.clear(); bridge_bodies.clear(); pushables.clear(); pending_action={}; action_progress=0
	for p in level.ground+level.platforms: solid_terrain(p)
	# Keep the left edge physical. The right edge advances only with both children.
	solid_rect(Rect2(-60,-500,60,1800))
	solid_rect(Rect2(float(level.width),-500,60,1800))
	for g in level.gates:
		var body=solid_rect(Rect2(g.x-13,g.y-g.h,26,g.h))
		gate_bodies.append({"data":g,"body":body})
	for bridge in level.get("bridges",[]):
		var body=solid_rect(Rect2(bridge.x,bridge.y,bridge.w,bridge.h)); body.collision_layer=1 if flags.get(bridge.key,false) else 0
		bridge_bodies.append({"data":bridge,"body":body})
	for p in level.get("pushables",[]):
		var body=Pushable.new(); body.object_id=p.id; body.game=self; body.origin=Vector2(p.x,p.y); body.position=body.origin; solids.add_child(body); pushables.append(body)
	if is_instance_valid(player): remove_child(player); player.queue_free()
	if is_instance_valid(boy): remove_child(boy); boy.queue_free()
	player=Child.new(); player.game=self; player.name="Girl"; player.position=Vector2(180,698); add_child(player)
	boy=Child.new(); boy.is_girl=false; boy.controlled=false; boy.game=self; boy.name="Boy"; boy.position=Vector2(123,698); add_child(boy)
	checkpoint_x=180; trail.clear(); companion_jumps.clear(); shell_clock=0; shell_warning=0; exposure=0; invulnerable=2
	hazard_exposure.clear(); hazard_cues.clear(); sector_seen.clear(); child_detection={"Girl":0.0,"Boy":0.0}; child_injury={"Girl":0.0,"Boy":0.0}
	camera.position=Vector2(800,450); camera.reset_smoothing()
	chapter_card=5.5 if announce else 0
	if announce: announce_message(level.objective,7)

func solid_rect(rect):
	var body=StaticBody2D.new(); body.collision_layer=1; body.collision_mask=2
	var shape=CollisionShape2D.new(); var box=RectangleShape2D.new(); box.size=rect.size; shape.shape=box; shape.position=rect.position+rect.size/2
	body.add_child(shape); solids.add_child(body); return body

func profile_y(p,x):
	var profile=p.get("profile",[])
	if profile.is_empty(): return float(p.y)
	var local_x=clampf(x-float(p.x),0,float(p.w))
	for i in range(1,profile.size()):
		if local_x<=float(profile[i][0]):
			var a=profile[i-1]; var b=profile[i]
			return float(p.y)+lerpf(float(a[1]),float(b[1]),clampf((local_x-float(a[0]))/maxf(.01,float(b[0])-float(a[0])),0,1))
	return float(p.y)+float(profile[-1][1])

func solid_terrain(p):
	if not p.has("profile"): return solid_rect(Rect2(p.x,p.y,p.w,p.h))
	var body=StaticBody2D.new(); body.collision_layer=1; body.collision_mask=2
	var shape=CollisionPolygon2D.new(); var polygon=PackedVector2Array()
	for point in p.profile: polygon.append(Vector2(float(p.x)+float(point[0]),float(p.y)+float(point[1])))
	polygon.append(Vector2(float(p.x)+float(p.w),float(p.y)+float(p.h)))
	polygon.append(Vector2(float(p.x),float(p.y)+float(p.h)))
	shape.polygon=polygon; body.add_child(shape); solids.add_child(body); return body

func surface_y_at(x,fallback_y=700.0):
	var closest=float(fallback_y); var distance=INF
	for p in level.ground+level.platforms:
		if x>=float(p.x) and x<=float(p.x)+float(p.w):
			var y=profile_y(p,x)
			if absf(y-fallback_y)<distance: closest=y; distance=absf(y-fallback_y)
	for bridge in level.get("bridges",[]):
		if flags.get(bridge.key,false) and x>=bridge.x and x<=bridge.x+bridge.w:
			if absf(bridge.y-fallback_y)<distance: closest=float(bridge.y); distance=absf(bridge.y-fallback_y)
	return closest

func new_journey():
	save_path=journey_save_path; section_preview=false; slice_active=false
	journey_active=true; journey_completed=false
	flags={}; memories={}; cache_remaining={}; rations=2; scrap=0; medicine=1
	wetness=0; encounter_events=[]; action_interrupts=0
	health=100; warmth=100; food=100; stamina=100; playtime=0; clock=0; death_count=0
	load_chapter(0); mode="playing"; write_save()

func continue_journey():
	save_path=journey_save_path; section_preview=false; slice_active=false; journey_active=false
	if not load_save(true):
		mode="menu"; return false
	mode="ending" if journey_completed else "playing"
	return true

func return_to_title():
	write_save()
	section_preview=false; slice_active=false; journey_active=false; save_path=journey_save_path
	save_exists=false; unlocked=0; load_save(false); mode="menu"

func open_chapters():
	if section_preview: return_to_title()
	save_path=journey_save_path; save_exists=false; unlocked=0; load_save(false)
	settings_return="menu"; mode="chapters"

func choose_chapter(index):
	save_path=journey_save_path; section_preview=false; slice_active=false
	if not load_save(true): new_journey()
	if index<=unlocked:
		journey_active=true; load_chapter(index); mode="playing"; write_save()

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
		if slice_active and last_house.is_helping(): announce_message("Finish the passage together before calling him.",3)
		else:
			boy.following=not boy.following
			announce_message("He’s coming. Keep a little room for him." if boy.following else "He’ll wait here. Don’t go too far.",3)
	if event.is_action_pressed("heal"):
		if medicine>0 and health<100:
			medicine-=1; health=minf(100,health+45); announce_message("A clean dressing. It will have to be enough.",4); write_save()
		elif medicine==0: announce_message("No medicine left. Search bags and cupboards.",4)
		else: announce_message("Save the dressing. You may need it later.",3)
	if event.is_action_pressed("restart"): recover(false)

func _process(dt):
	if mode=="playing": clock+=dt
	flash=move_toward(flash,0,dt*2.5); shake=move_toward(shake,0,dt*11)
	message_time=maxf(0,message_time-dt)
	if mode=="playing": chapter_card=maxf(0,chapter_card-dt)
	if mode=="recovering":
		recovery_clock-=dt
		if recovery_clock<=0: respawn()
	var look=clampf(player.velocity.x*.48,-110,150)
	var target=clampf(player.position.x+170+look,740,float(level.width)-740)
	if mode=="menu": target=1050
	camera.position.x=lerpf(camera.position.x,target,1-exp(-dt*3.5))
	camera.position.y=480+clampf((player.position.y-700)*.14,-45,35)
	if not reduced_motion and shake>0: camera.offset=Vector2(sin(clock*63),cos(clock*51))*shake
	else: camera.offset=Vector2.ZERO
	for p in dust:
		p.p+=p.v*dt; p.v.y-=dt*8; p.life-=dt
	dust=dust.filter(func(p): return p.life>0)
	for p in impacts: p.age+=dt
	impacts=impacts.filter(func(p):return p.age<4)
	for zone in level.get("water_zones",[]): water_offsets[zone.key]=move_toward(float(water_offsets.get(zone.key,0)),62.0 if flags.get(zone.key,false) else 0.0,dt*24)

func _physics_process(dt):
	if mode!="playing": return
	playtime+=dt; invulnerable=maxf(0,invulnerable-dt)
	for name in child_injury: child_injury[name]=maxf(0,float(child_injury[name])-dt)
	tick_action(dt)
	if (not Input.is_action_pressed("sprint") or abs(player.velocity.x)<15) and not wind_strain: stamina=minf(100,stamina+dt*15)
	food=maxf(0,food-dt*.38)
	sheltered=is_covered(player) and is_covered(boy)
	var under_roof=in_safe_zone(player.position.x,player.position.y) and in_safe_zone(boy.position.x,boy.position.y)
	var cold=float(level.cold) * (.08 if under_roof else (.22 if sheltered else 1.0))
	var soaked=in_water(player.position.x,player.position.y) or in_water(boy.position.x,boy.position.y)
	wetness=clampf(wetness+dt*(.20 if soaked else -.009),0,1)
	if chapter==2 and not slice_active and under_roof and not flags.get("shelter_roof",false): wetness=minf(1,wetness+dt*.045); cold=.4
	cold+=wetness*.65
	warmth=clampf(warmth-dt*cold,0,100)
	if food<12 or warmth<8: health=maxf(0,health-dt*.7)
	update_companion(dt)
	tick_hazard_lanes(dt)
	if slice_active: last_house.tick(dt)
	for sector in level.get("zones",[]):
		if player.position.x>=sector.x and player.position.x<sector.x+sector.w and not sector_seen.has(sector.x):
			sector_seen[sector.x]=true
			if sector.has("caption"): announce_message(sector.caption,5)
	for gb in gate_bodies:
		gb.body.collision_layer=0 if gate_open(gb.data) else 1
	for bridge in bridge_bodies: bridge.body.collision_layer=1 if flags.get(bridge.data.key,false) else 0
	update_prompt()
	for m in level.memories:
		if not memories.has(m.id) and player.position.distance_to(Vector2(m.x,m.y))<62:
			memories[m.id]=m.text; play_sfx("collect",-13); announce_message(m.text,7); write_save()
	for cp in level.checkpoints:
		if player.position.x>cp and cp>checkpoint_x and abs(player.position.x-boy.position.x)<240:
			checkpoint_x=cp; write_save()
	if level.has("danger"):
		var in_danger=(player.position.x>level.danger[0] and player.position.x<level.danger[1]) or (boy.position.x>level.danger[0] and boy.position.x<level.danger[1])
		if in_danger:
			shell_clock+=dt
			shell_warning=clampf((shell_clock-8.2)/2.6,0,1)
			if shell_clock>=8.2 and shell_clock-dt<8.2:
				play_sfx("warning",-14); announce_message("The sky is warning you. Reach cover. Stay low.",3)
			if shell_clock>=10.8:
				flash=1; shake=8; play_sfx("blast",-9)
				impacts.append({"p":Vector2(player.position.x+310,693),"age":0.0})
				if not sheltered: hurt(65,"The shockwave caught them in the open.")
				shell_clock=0; shell_warning=0
		else: shell_clock=maxf(0,shell_clock-dt*2); shell_warning=0
	if level.get("searchlight",false):
		var caught=(player.position.x>650 and player.position.x<4600 and abs(player.position.x-beam_x())<130 and not is_covered(player)) or (boy.position.x>650 and boy.position.x<4600 and abs(boy.position.x-beam_x())<130 and not is_covered(boy))
		exposure=clampf(exposure+dt*(1 if caught else -2.0),0,1.8)
		if exposure>=1.75:
				hurt(34,"They saw movement. Keep both children low behind cover."); exposure=0
	if player.position.y>1030 or boy.position.y>1050:
		recover(true,"The road gave way. Try again, together.")
	if health<=0: recover(true,"They need a safer way through.")
	if not slice_active and player.position.x>float(level.width)-110:
		if abs(player.position.x-boy.position.x)<180:
			if chapter<4:
				unlocked=maxi(unlocked,chapter+1); load_chapter(chapter+1); write_save()
		else:
			player.position.x=float(level.width)-115
			announce_message("Wait for him. Press Q to call him back.",2)

func remember_jump(at,direction):
	if absf(direction)<.1: return
	companion_jumps.append({"at":at,"direction":signf(direction),"time":playtime})
	if companion_jumps.size()>12: companion_jumps.pop_front()

func update_companion(dt):
	# Recent takeoff cues replace scanning every old airborne position. Each cue
	# is consumed once, and expires before a later return to the same location.
	for i in range(companion_jumps.size()-1,-1,-1):
		if playtime-float(companion_jumps[i].time)>12: companion_jumps.remove_at(i)
	companion_alert_clock=maxf(0,companion_alert_clock-dt)
	boy.ai_axis=0; boy.ai_jump=false
	var gap=player.position.x-boy.position.x
	var cover_target=companion_cover_target()
	var follow_gap=gap if cover_target==null else float(cover_target)-boy.position.x
	boy.forced_crouch=player.crouching if boy.following else true
	if boy.following:
		var forward=signf(gap)
		# Ease into the following distance instead of alternating full speed.
		if cover_target!=null:
			boy.ai_axis=clampf(follow_gap/15.0,-1,1) if absf(follow_gap)>4 else 0.0
		elif absf(gap)>42: boy.ai_axis=forward*clampf((absf(gap)-42)/30.0,0,1)
		if boy.is_on_floor() and absf(gap)>55:
			var ahead=boy.position.x+forward*22
			var edge=not ground_at(ahead) and boy.position.y>660
			if edge:
				var landing=false
				for reach in [50,90,130,170,200]:
					if ground_at(ahead+forward*reach): landing=true; break
				if landing and boy.can_stand(): boy.ai_jump=true; boy.forced_crouch=false
				else: boy.ai_axis=0
			for p in level.platforms:
				if ahead>p.x-4 and ahead<p.x+p.w and p.y<boy.position.y-12 and p.y>boy.position.y-145 and boy.can_stand(): boy.ai_jump=true; boy.forced_crouch=false
			for i in range(companion_jumps.size()):
				var cue=companion_jumps[i]
				if cue.direction==forward and absf(cue.at.x-boy.position.x)<28 and absf(cue.at.y-boy.position.y)<32 and boy.can_stand():
					boy.ai_jump=true; boy.forced_crouch=false; companion_jumps.remove_at(i); break
		if absf(gap)>390 and companion_alert_clock<=0:
			announce_message("He is falling behind. Slow down and call him [Q].",3); companion_alert_clock=6
	if slice_active: last_house.companion_override()
	var close=absf(gap)<58 and absf(player.position.y-boy.position.y)<17 and not player.crouching and player.is_on_floor() and boy.is_on_floor() and player.action_time<=0 and boy.action_time<=0
	player.hand_active=close; boy.hand_active=close
	var hand=(player.position+boy.position)*.5+Vector2(0,-53)
	player.contact_hand=hand; boy.contact_hand=hand

func companion_cover_target():
	if not boy.following or not player.crouching or absf(player.velocity.x)>20: return null
	for c in level.covers:
		if absf(player.position.x-c.x)>=c.w*.5-8 or absf(player.position.y-surface_y_at(c.x,700))>45: continue
		var lo=float(c.x)-float(c.w)*.5+22; var hi=float(c.x)+float(c.w)*.5-22
		var target=clampf(player.position.x-player.facing*48,lo,hi)
		if absf(target-player.position.x)<30: target=clampf(player.position.x+player.facing*48,lo,hi)
		if ground_at(target): return target
	return null

func child_status(child):
	var key=str(child.name)
	if float(child_injury.get(key,0))>0: return "HURT"
	if float(child_detection.get(key,0))>.08: return "SEEN"
	return "COVERED" if is_covered(child) else "OPEN"

func ground_at(x):
	for bridge in level.get("bridges",[]):
		if flags.get(bridge.key,false) and x>=bridge.x and x<=bridge.x+bridge.w: return true
	for g in level.ground:
		if x>=g.x and x<=g.x+g.w: return true
	return false

func is_covered(child):
	if in_safe_zone(child.position.x,child.position.y): return true
	for c in level.covers:
		if abs(child.position.x-c.x)<c.w/2.0 and (child.crouching or c.kind=="tent") and abs(child.position.y-surface_y_at(c.x,700))<65: return true
	return false

func beam_x(): return 2650+sin(clock*.29)*1970

func gate_open(g):
	if slice_active and g.key=="passage_braced": return last_house.gate_held()
	if flags.get(g.key,false): return true
	if g.has("plate"):
		for body in pushables:
			if abs(body.position.x-g.plate)<48 and body.position.y>655: return true
		return (abs(player.position.x-g.plate)<45 and player.position.y>680) or (abs(boy.position.x-g.plate)<45 and boy.position.y>680)
	return false

func cache_has_room(p):
	var remaining=cache_remaining.get(p.id,{"rations":int(p.get("rations",0)),"scrap":int(p.get("scrap",0)),"medicine":int(p.get("medicine",0))})
	for resource in CAPACITY:
		if int(remaining.get(resource,0))>0 and int(get(resource))<int(CAPACITY[resource]): return true
	return false

func update_prompt():
	prompt=""; near_item={}; var best_score=INF; var full_cache={}
	for p in level.interact:
		if p.kind=="cache" and flags.get(p.id,false): continue
		if p.kind in ["wheel","latch","repair","roof","pump","bridge","relay","clear","brace","inspect","reciprocal","bag","share","quiet"] and flags.get(p.id,false): continue
		if abs(player.position.x-p.x)>=86 or abs(player.position.y-p.y)>=100: continue
		if p.kind=="cache" and not cache_has_room(p): full_cache=p; continue
		# World work wins over a co-located cache. Distance breaks ties of one kind.
		var priority=180.0 if p.kind=="cache" else (90.0 if p.kind=="fire" else 0.0)
		var score=priority+absf(player.position.x-float(p.x))
		if score<best_score: best_score=score; near_item=p
	if not near_item.is_empty(): prompt=last_house.prompt_for(near_item) if slice_active else "HOLD E   "+near_item.label
	elif not full_cache.is_empty(): prompt="PACK FULL - supplies remain here"
	else:
		for tutorial in level.tutorials:
			if abs(player.position.x-tutorial.x)<180: prompt=tutorial.text; break

func in_safe_zone(x,feet_y=INF):
	for zone in level.get("safe_zones",[]):
		if abs(x-zone.x)<zone.w/2.0 and (not zone.has("key") or flags.get(zone.key,false)):
			if zone.has("y") and absf(feet_y-float(zone.y))>float(zone.get("height_tolerance",45)): continue
			return true
	return false

func current_objective():
	if slice_active: return last_house.objective()
	for p in level.interact:
		if p.kind in ["relay","clear","brace"] and not p.get("optional",false) and not flags.get(p.id,false) and player.position.x>p.x-900:
			return p.get("objective",p.label)
	if chapter==1 and not flags.get("forest_bridge",false): return "Lower the washed-out crossing at the forester’s winch."
	if chapter==2:
		if not flags.get("shelter_door",false): return "Find two salvage. Clear and brace the shelter door."
		if not flags.get("shelter_roof",false): return "The roof leaks. One salvage can make it dry."
		return "Bring him to the stove. Leave when you are ready."
	if chapter==3 and flags.get("school_gate",false) and not flags.get("school_drain",false): return "Find the pump. Drain the flooded yard."
	return level.objective

func in_water(x,feet_y=INF):
	for zone in level.get("water_zones",[]):
		if x>zone.x and x<zone.x+zone.w and feet_y>=float(zone.top) and not flags.get(zone.key,false): return true
	return false

func wind_speed_scale(child):
	if child.crouching or is_covered(child): return 1.0
	for h in level.get("hazard_lanes",[]):
		if h.kind=="wind" and child.position.x>h.x and child.position.x<h.x+h.w and hazard_active(h): return .56
	return 1.0

func hazard_phase(h):
	return fposmod(playtime+float(h.get("offset",0)),maxf(1,float(h.get("period",12))))

func hazard_active(h):
	if h.has("key") and flags.get(h.key,false): return false
	return hazard_phase(h)<float(h.get("active",2.5))

func hazard_warning(h):
	if h.has("key") and flags.get(h.key,false): return false
	return hazard_phase(h)>float(h.get("period",12))-1.6

func tick_hazard_lanes(dt):
	lane_warning=""
	wind_strain=false
	for h in level.get("hazard_lanes",[]):
		if h.has("key") and flags.get(h.key,false): continue
		var near=maxf(player.position.x,boy.position.x)>h.x-230 and minf(player.position.x,boy.position.x)<h.x+h.w+160
		if not near: continue
		var active=hazard_active(h); var warning=hazard_warning(h)
		if active or warning:
			lane_warning={"debris":"LOOSE MASONRY · WAIT FOR THE DUST TO SETTLE","sweep":"PATROL LIGHT · KEEP BOTH CHILDREN LOW","wind":"CROSSWIND · CROUCH TO STEADY YOURSELVES"}.get(h.kind,"WAIT FOR A CLEAR MOMENT")
		if warning:
			var cue=str(h.x)+"_"+str(int((playtime+float(h.get("offset",0)))/float(h.period)))
			if not hazard_cues.has(cue): hazard_cues[cue]=true; play_sfx("warning",-19)
		if not active: continue
		var at_risk=false
		for child in [player,boy]:
			if child.position.x<h.x or child.position.x>h.x+h.w: continue
			if h.kind=="wind":
				if not child.crouching and not is_covered(child):
					child.velocity.x-=dt*195; stamina=maxf(0,stamina-dt*5)
					at_risk=true
			elif not is_covered(child): at_risk=true
		var key=str(h.x)
		if h.kind=="sweep":
			hazard_exposure[key]=maxf(0,float(hazard_exposure.get(key,0))+dt*(1.0 if at_risk else -2.0))
			if hazard_exposure[key]>1.25: hurt(28,"The light found a moving silhouette. Wait in cover for the next pass."); hazard_exposure[key]=0
		elif h.kind=="debris" and at_risk:
			hurt(42,"The masonry gave way. Watch the falling dust before crossing.")
		elif h.kind=="wind" and at_risk: wind_strain=true

func interact():
	if slice_active and not near_item.is_empty() and last_house.try_interact(near_item): return
	if not pending_action.is_empty() or near_item.is_empty(): return
	if player.action_time>0: return
	pending_action=near_item.duplicate(); action_progress=0; action_duration=float(pending_action.get("hold_seconds",1.1))
	if pending_action.kind=="end" and abs(player.position.x-boy.position.x)>120:
		pending_action={}; announce_message("Wait for him. You made it this far together.",3)
	elif pending_action.get("companion_required",false) and (abs(player.position.x-boy.position.x)>95 or abs(player.position.y-boy.position.y)>40):
		pending_action={}; announce_message("This needs two pairs of hands. Bring him close [Q].",4)
	elif pending_action.kind=="brace" and scrap<1:
		pending_action={}; announce_message("One sound piece of timber or wire. Search nearby.",4)

func tick_action(dt):
	if pending_action.is_empty(): return
	if not Input.is_action_pressed("interact") or abs(player.position.x-pending_action.x)>100:
		action_interrupts+=1; pending_action={}; action_progress=0; player.action_time=0; return
	player.action_time=.12
	if pending_action.get("companion_required",false):
		if abs(player.position.x-boy.position.x)>105 or abs(player.position.y-boy.position.y)>45:
			action_interrupts+=1; pending_action={}; action_progress=0; player.action_time=0; return
		boy.action_time=.12
		stamina=maxf(0,stamina-dt*4)
	if pending_action.kind=="fire": boy.action_time=.12
	action_progress+=dt
	if action_progress>=action_duration:
		var task=pending_action; pending_action={}; player.action_time=0
		complete_interaction(task)

func complete_interaction(task={}):
	if player.action_time>0: return
	if task.is_empty() and near_item.is_empty(): return
	var p=near_item if task.is_empty() else task
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
		"wheel","latch","bridge":
			flags[p.id]=true; announce_message("The way is open. Call him through [Q].",4); play_sfx("wheel")
		"repair":
			if scrap>=2:
				scrap-=2; flags[p.id]=true; announce_message("A door that closes. For tonight, that is enough.",5); play_sfx("wheel")
			else: announce_message("Two pieces of salvage. Search the tool roll and the rucksack.",5)
		"roof":
			if scrap>=1: scrap-=1; flags[p.id]=true; wetness=maxf(0,wetness-.35); announce_message("The drip stops. He can sleep without shivering.",5)
			else: announce_message("One useful piece of canvas or wire. Search the camp.",4)
		"pump":
			flags[p.id]=true; wetness=maxf(0,wetness-.15); play_sfx("wheel"); announce_message("The water begins to fall. Get him through before the next warning.",5)
		"relay":
			if abs(player.position.x-boy.position.x)>105: return
			flags[p.id]=true; play_sfx("wheel"); announce_message("Together, the weight begins to move.",4)
		"clear":
			flags[p.id]=true; stamina=maxf(0,stamina-12); play_sfx("wheel"); spawn_dust(Vector2(p.x,p.y),8); announce_message("A narrow way through. Let him pass first.",4)
		"brace":
			if scrap<1: return
			scrap-=1; flags[p.id]=true; play_sfx("wheel"); announce_message("The beam holds. The way is safer for both of you.",4)
		"fire":
			if abs(player.position.x-boy.position.x)>180:
				announce_message("Bring him close before resting [Q].",4); return
			if rations>0:
				rations-=1; food=minf(100,food+36); warmth=minf(100,warmth+52); health=minf(100,health+22)
				announce_message("They share a little bread and wait for their hands to warm.",6)
				wetness=maxf(0,wetness-.6)
			else:
				warmth=minf(100,warmth+8); announce_message("A little warmth, but nothing left to eat.",4)
			checkpoint_x=maxf(180,player.position.x); shell_clock=0
		"end":
			if abs(player.position.x-boy.position.x)<120:
				mode="ending"; journey_completed=true; unlocked=4; write_save(); play_sfx("collect",-19)
			else: announce_message("Wait for him. You made it this far together.",4)
	player.action_time=.75; boy.action_time=.75 if p.kind=="fire" else 0.0
	encounter_events.append({"kind":p.kind,"id":p.get("id",""),"chapter":chapter,"time":playtime})
	write_save(); update_prompt()

func hurt(amount,reason,affected=[]):
	if invulnerable>0: return
	health=maxf(0,health-amount); invulnerable=3; flash=.65; shake=5; announce_message(reason,4)
	if affected.is_empty(): affected=[player,boy]
	for child in affected:
		child.hit_time=.35; child_injury[str(child.name)]=2.5
	pending_action={}; action_progress=0

func recover(count=true,reason="Take another breath. Try a different path."):
	if mode!="playing": return
	if count: death_count+=1
	encounter_events.append({"kind":"recovery","chapter":chapter,"reason":reason,"time":playtime})
	mode="recovering"; recovery_clock=1.4; announce_message(reason,4)

func respawn(reset_survival=true):
	player.position=Vector2(checkpoint_x,surface_y_at(checkpoint_x,700)-5); boy.position=Vector2(maxf(40,checkpoint_x-54),surface_y_at(checkpoint_x-54,700)-5)
	player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO; boy.following=true
	for child in [player,boy]:
		child.climbing=false; child.climb_clock=0; child.jump_buffer=0; child.coyote=0; child.leap_axis=0; child.ai_jump=false; child.action_time=0; child.hit_time=0; child.was_floor=false; child.moving_last=false
	player.reset_feet(); boy.reset_feet(); pending_action={}
	for body in pushables: body.reset_to_origin()
	trail.clear(); companion_jumps.clear()
	if slice_active: last_house.reset_after_recovery()
	if reset_survival: health=maxf(55,health); warmth=maxf(35,warmth); food=maxf(30,food); stamina=100
	wind_strain=false
	shell_clock=0; shell_warning=0; invulnerable=4; exposure=0; mode="playing"
	camera.position.x=clampf(checkpoint_x+235,800,float(level.width)-800)
	# Existing supplies and puzzle progress persist so failure never consumes a finite cache.

func announce_message(text,duration=4): message=text; message_time=duration

func spawn_dust(pos,count):
	for i in range(count): dust.append({"p":pos+Vector2(randf_range(-10,10),-3),"v":Vector2(randf_range(-20,20),randf_range(-16,-3)),"size":randf_range(1,4),"life":randf_range(.3,.8)})

func valid_save_data(data):
	if not data is Dictionary or data.get("schema",0)!=1: return false
	for key in ["flags","memories","cache_remaining"]:
		if not data.get(key,{}) is Dictionary: return false
	for key in data.get("flags",{}):
		if not key is String or not data.flags[key] is bool: return false
	for key in data.get("memories",{}):
		if not key is String or not data.memories[key] is String: return false
	for id in data.get("cache_remaining",{}):
		var cache=data.cache_remaining[id]
		if not id is String or not cache is Dictionary: return false
		for key in cache:
			if key not in CAPACITY or not (cache[key] is int or cache[key] is float) or not is_finite(float(cache[key])) or float(cache[key])<0: return false
	for key in ["chapter","checkpoint","unlocked","rations","scrap","medicine","health","warmth","food","wetness","stamina","playtime","volume"]:
		var value=data.get(key,0)
		if not (value is int or value is float) or not is_finite(float(value)): return false
	for key in ["completed","muted","reduced_motion"]:
		if not data.get(key,false) is bool: return false
	return true

func read_valid_save(path):
	if not FileAccess.file_exists(path): return null
	var data=JSON.parse_string(FileAccess.get_file_as_string(path))
	return data if valid_save_data(data) else null

func write_save():
	if smoke_test: return
	var prefs=FileAccess.open(settings_path,FileAccess.WRITE)
	if prefs: prefs.store_string(JSON.stringify({"volume":volume,"muted":muted,"reduced_motion":reduced_motion})); prefs.close()
	if not journey_active: return
	var data={"schema":1,"build":"0.5.0","chapter":chapter,"checkpoint":checkpoint_x,"flags":flags,"memories":memories,"cache_remaining":cache_remaining,"unlocked":unlocked,"rations":rations,"scrap":scrap,"medicine":medicine,"health":health,"warmth":warmth,"food":food,"wetness":wetness,"stamina":stamina,"playtime":playtime,"volume":volume,"muted":muted,"reduced_motion":reduced_motion,"completed":journey_completed,"scenario":"last_house" if slice_active else ("rehearsal" if section_preview else "journey")}
	var f=FileAccess.open(save_path+".tmp",FileAccess.WRITE)
	if not f: save_notice="Could not save. Check the save folder before leaving."; return
	f.store_string(JSON.stringify(data,"\t")); f.close()
	if read_valid_save(save_path)!=null: DirAccess.copy_absolute(save_path,save_path+".bak")
	var err=DirAccess.rename_absolute(save_path+".tmp",save_path)
	if err!=OK: save_notice="Could not finish saving. Your last saved journey is preserved."; return
	if not section_preview: save_exists=true
	save_notice=""

func load_save(resume=false):
	if FileAccess.file_exists(settings_path):
		var prefs=JSON.parse_string(FileAccess.get_file_as_string(settings_path))
		if prefs is Dictionary:
			var v=prefs.get("volume",.6)
			if (v is int or v is float) and is_finite(float(v)): volume=clampf(float(v),0,1)
			if prefs.get("muted",false) is bool: muted=prefs.get("muted",false)
			if prefs.get("reduced_motion",false) is bool: reduced_motion=prefs.get("reduced_motion",false)
	var d=read_valid_save(save_path)
	if d==null:
		d=read_valid_save(save_path+".bak")
		if d!=null: save_notice="Recovered the last valid save."
		elif FileAccess.file_exists(save_path): save_notice="This save could not be read. Begin a new journey, or restore a backup."
	if d==null: save_exists=false; return false
	save_exists=true; unlocked=clampi(int(d.get("unlocked",0)),0,4)
	if not resume: return true
	journey_active=true; journey_completed=d.get("completed",false)
	flags=d.get("flags",{}); memories=d.get("memories",{})
	cache_remaining=d.get("cache_remaining",{})
	wetness=clampf(float(d.get("wetness",0)),0,1)
	rations=clampi(int(d.get("rations",2)),0,4); scrap=clampi(int(d.get("scrap",0)),0,6); medicine=clampi(int(d.get("medicine",1)),0,2)
	health=clampf(float(d.get("health",100)),0,100); warmth=clampf(float(d.get("warmth",100)),0,100); food=clampf(float(d.get("food",100)),0,100); stamina=clampf(float(d.get("stamina",100)),0,100)
	playtime=float(d.get("playtime",0)); load_chapter(clampi(int(d.get("chapter",0)),0,4))
	checkpoint_x=clampf(float(d.get("checkpoint",180)),180,float(level.width)-250); respawn(false); apply_volume()
	return true

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
		assert_check("chapter_%d_geometry"%(i+1),solids.get_child_count()==level.ground.size()+level.platforms.size()+level.gates.size()+level.get("bridges",[]).size()+pushables.size()+2)
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
			if p.kind in ["repair","roof","brace"]: scrap=maxi(3,scrap)
			if p.kind=="fire": warmth=40; rations=maxi(1,rations)
			await test_action(p)
			if p.kind in ["cache","wheel","repair","latch","roof","pump","bridge","relay","clear","brace"]: assert_check("chapter_%d_%s_%s"%[i+1,p.kind,p.id],flags.get(p.id,false))
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
	for frame in range(90000):
		await get_tree().physics_frame
		if mode=="ending": completed=true; break
		if mode=="recovering": continue
		if chapter!=last_chapter:
			last_chapter=chapter; reached.append(chapter+1); farthest=0; stalled=0
			print("TRAVERSE_CHAPTER ",chapter+1)
		if player.position.x>farthest+3: farthest=player.position.x; stalled=0
		else: stalled+=1
		if not pending_action.is_empty() or player.action_time>0: stalled=0
		if stalled>600:
			failure="Stalled in chapter %d at x=%d, boy=%d, y=%d"%[chapter+1,player.position.x,boy.position.x,player.position.y]; break
		Input.action_release("left"); Input.action_press("right")
		Input.action_release("crouch"); Input.action_release("sprint")
		if not pending_action.is_empty(): Input.action_press("interact")
		else: Input.action_release("interact")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		# Stop for a usable supply cache, wheel, or fire. Interactions use the same
		# distance-gated prompt and inventory code as the player.
		update_prompt()
		if not near_item.is_empty():
			var p=near_item
			if p.get("companion_required",false) and abs(player.position.x-boy.position.x)>85:
				Input.action_release("right")
			if p.kind in ["wheel","latch","repair","roof","pump","bridge","relay","clear","brace","end"] or (p.kind=="cache" and not p.get("optional",false) and not searched.has(p.id)):
				Input.action_press("interact")
				interact()
				if p.kind=="cache" and not pending_action.is_empty(): searched[p.id]=true
			if p.kind=="fire" and abs(player.position.x-boy.position.x)<120 and rations>0 and (health<85 or warmth<65 or food<55): Input.action_press("interact"); interact()
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
				if p.x-player.position.x>0 and p.x-player.position.x<45 and p.y<player.position.y-12 and p.y>player.position.y-145: need_jump=true
			for body in pushables:
				if body.position.x-player.position.x>0 and body.position.x-player.position.x<78: need_jump=true
		if need_jump and jump_hold==0:
			Input.action_press("jump"); jump_hold=24; jump_sprinting=gap_leap
		# Keep sprint through the jump instead of braking in the air over a gap.
		if not player.is_on_floor() and jump_sprinting: Input.action_press("sprint")
		# Read the shell warning and stop in existing cover when it is reachable.
		if shell_warning>.05:
			for c in level.covers:
				if abs(player.position.x-c.x)<c.w*.35 and abs(boy.position.x-c.x)<c.w*.45:
					Input.action_release("right"); Input.action_press("crouch"); break
		# Observe a lane from its safe entrance. Wait for enough clear time to
		# bring the follower through as well, rather than charging a periodic trap.
		for h in level.get("hazard_lanes",[]):
			if h.has("key") and flags.get(h.key,false): continue
			if player.position.x>h.x-145 and player.position.x<h.x-20:
				var clear_time=float(h.period)-hazard_phase(h)
				var crossing=(float(h.w)+180.0)/166.0+1.0
				if hazard_active(h) or clear_time<crossing:
					Input.action_release("right"); Input.action_press("crouch"); stalled=0
		if frame%1800==0: print("TRAVERSE_PROGRESS ",chapter+1," ",int(player.position.x)," boy=",int(boy.position.x)," deaths=",death_count)
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)
	var report={"build":"0.5.0","completed":completed,"chapters_reached":reached,"failure":failure,"deaths":death_count,"simulated_seconds":playtime,"rations_remaining":rations,"medicine_remaining":medicine,"health":health,"encounters":encounter_events,"method":"Continuous native physics traversal driven with Input actions; no position changes, gate bypass, resource grants or damage immunity. Interactions require held input and complete their actual duration. This is automated traversal, not human artistic acceptance."}
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
	await test_action(fire)
	assert_check("rest_spends_finite_ration",rations==0 and health>60 and warmth>68 and food>53)
	var p=level.interact[0]; flags.erase(p.id); cache_remaining.erase(p.id)
	player.position=Vector2(p.x,699); boy.position=Vector2(p.x-42,699); rations=4; medicine=2; near_item=p; player.action_time=0
	await test_action(p)
	assert_check("full_pack_leaves_supplies_in_world",not flags.get(p.id,false) and rations==4 and medicine==2)
	rations=0; medicine=0; near_item=p; player.action_time=0; await test_action(p)
	var after_food=rations; var after_med=medicine
	near_item=p; player.action_time=0; await test_action(p)
	assert_check("searched_cache_cannot_duplicate_supplies",rations==after_food and medicine==after_med and flags.get(p.id,false))
	load_chapter(0,false); mode="playing"; stamina=0; player.action_time=0
	Input.action_press("right"); Input.action_press("sprint")
	for frame in range(40): await get_tree().physics_frame
	assert_check("exhaustion_prevents_sprinting",player.velocity.x<=204.1 and stamina<1,str(player.velocity.x))
	Input.action_release("right"); Input.action_release("sprint")
	boy.following=false; boy.position=Vector2(float(level.width)-700,699); player.position=Vector2(float(level.width)-50,699); player.velocity=Vector2.ZERO
	for frame in range(4): await get_tree().physics_frame
	assert_check("chapter_exit_waits_for_both_children",chapter==0 and player.position.x<=float(level.width)-115)
	load_chapter(4,false); mode="playing"; var end=level.interact[-1]
	player.position=Vector2(end.x,699); boy.position=Vector2(end.x-400,699); near_item=end; player.action_time=0; interact()
	assert_check("ending_requires_companion",mode=="playing")
	boy.position=Vector2(end.x-42,699); near_item=end; player.action_time=0; await test_action(end)
	assert_check("ending_accepts_reunited_children",mode=="ending")
	var passed=true
	for result in test_log:
		if not result.passed: passed=false
	var report={"all_passed":passed,"checks":test_log,"measurements":measurements,"scope":"Real Godot physics and damage/rest/cache rules. Deliberate scenario setup repositions actors and sets initial conditions; continuous_traversal.json tests uninterrupted navigation separately."}
	var f=FileAccess.open(report_path("survival_consequences.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("SURVIVAL_RESULT ",JSON.stringify(report))
	call_deferred("quit_game",0 if passed else 1)

func test_action(p):
	pending_action={}; near_item=p; player.action_time=0
	Input.action_press("interact"); interact()
	for frame in range(ceili(float(p.get("hold_seconds",1.1))*60)+5): await get_tree().physics_frame
	Input.action_release("interact")

func run_encounter_tests():
	load_chapter(0,false); mode="playing"
	var body=pushables[0]; var begin=body.position.x
	player.position=Vector2(begin-68,699); boy.position=player.position-Vector2(44,0)
	Input.action_press("right"); Input.action_press("interact")
	for frame in range(150): await get_tree().physics_frame
	Input.action_release("right"); Input.action_release("interact")
	assert_check("crate_moves_under_native_push",body.position.x>begin+75,str(body.position.x-begin))
	load_chapter(1,false); mode="playing"; flags.erase("forest_bridge")
	var winch=level.interact[1]
	player.position=Vector2(winch.x,699); boy.position=Vector2(winch.x-44,699)
	near_item=winch; Input.action_press("interact"); interact()
	for frame in range(45): await get_tree().physics_frame
	assert_check("winch_does_not_complete_instantly",not flags.get("forest_bridge",false) and action_progress>.5)
	Input.action_release("interact")
	for frame in range(3): await get_tree().physics_frame
	assert_check("release_cancels_winch",pending_action.is_empty() and not ground_at(1300))
	await test_action(winch)
	for frame in range(2): await get_tree().physics_frame
	assert_check("lowered_bridge_has_real_collision",ground_at(1300) and bridge_bodies[0].body.collision_layer==1)
	flags.erase("forest_latch"); player.position=Vector2(1952,699); boy.position=Vector2(2700,699); boy.following=false
	player.action_time=0; Input.action_press("right"); Input.action_press("interact")
	for frame in range(420):
		await get_tree().physics_frame
		if pushables[0].position.x>2218: break
	Input.action_release("right"); Input.action_release("interact")
	assert_check("crate_can_hold_gate_instead_of_child",gate_open(level.gates[0]),str(pushables[0].position))
	load_chapter(3,false); mode="playing"; flags.erase("school_drain"); wetness=0; warmth=100
	player.position=Vector2(3090,699); boy.position=Vector2(3050,699); boy.following=false
	Input.action_press("right")
	for frame in range(60): await get_tree().physics_frame
	Input.action_release("right")
	assert_check("flood_slows_wading_and_soaks_clothes",player.velocity.x<110 and wetness>.18,str(wetness))
	var pump=level.interact[-1]
	player.position=Vector2(pump.x,699); player.velocity=Vector2.ZERO; boy.position=Vector2(pump.x-44,699); shell_clock=0
	await test_action(pump)
	assert_check("pump_removes_water_hazard",flags.get("school_drain",false) and not in_water(pump.x))
	load_chapter(2,false); mode="playing"; flags["shelter_door"]=true; flags.erase("shelter_roof"); wetness=0
	player.position=Vector2(5030,699); boy.position=Vector2(4986,699); boy.following=false
	for frame in range(120): await get_tree().physics_frame
	assert_check("unrepaired_shelter_still_leaks",wetness>.07,str(wetness))
	var roof={}
	for p in level.interact:
		if p.kind=="roof": roof=p
	player.position=Vector2(roof.x,699); player.velocity=Vector2.ZERO; boy.position=Vector2(roof.x-44,699); scrap=1; shell_clock=0
	await test_action(roof)
	assert_check("roof_patch_costs_one_salvage",flags.get("shelter_roof",false) and scrap==0)
	var before=wetness
	for frame in range(90): await get_tree().physics_frame
	assert_check("patched_shelter_stays_dry",wetness<=before)
	var passed=true
	for result in test_log:
		if not result.passed: passed=false
	var report={"build":"0.5.0","all_passed":passed,"checks":test_log,"method":"Native rigid-body push, timed held input and interruption, bridge collision activation, crate pressure plate, wading and wetness, pump, shelter roof consumption and thermal behavior. Deliberate test setups are separate from full journey navigation."}
	var f=FileAccess.open(report_path("encounter_checks.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("ENCOUNTER_RESULT ",JSON.stringify(report)); call_deferred("quit_game",0 if passed else 1)

func run_motion_review():
	# A labeled locomotion study on an isolated flat route. Original level files
	# are untouched; the full journey is validated independently.
	var fixture=levels[0].duplicate(true); fixture.ground=[{"x":0,"y":700,"w":8000,"h":600,"kind":"earth"}]; fixture.width=8000
	fixture.platforms=[]; fixture.gates=[]; fixture.covers=[]; fixture.interact=[]; fixture.pushables=[]; fixture.checkpoints=[]; fixture.memories=[]; fixture.tutorials=[]; fixture.hazard_lanes=[]; fixture.zones=[]
	levels[0]=fixture; load_chapter(0,false); mode="playing"; chapter_card=0
	var folder=report_path("motion_frames"); DirAccess.make_dir_recursive_absolute(folder)
	var drifts=[]; var previous_feet=[]; var previous_phase=[]
	for frame in range(360):
		for action in ["right","jump","sprint","crouch"]: Input.action_release(action)
		var label="WALK"
		if frame<90: Input.action_press("right")
		elif frame<120: label="STOP & BREATHE"
		elif frame<180: Input.action_press("right"); Input.action_press("crouch"); label="CROUCH WALK"
		elif frame<240: Input.action_press("right"); Input.action_press("sprint"); label="RUN"
		elif frame<270:
			Input.action_press("right"); Input.action_press("sprint"); label="JUMP & LAND"
			if frame<252: Input.action_press("jump")
		elif frame<300: label="SETTLE"
		else: Input.action_press("crouch"); label="LOW COVER POSE"
		message="LOCOMOTION STUDY  ·  "+label; message_time=1
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_jpg(folder.path_join("%04d.jpg"%frame),.86)
		var current=[]
		for i in range(2):
			var world_foot=player.position+player.feet[i]
			current.append(world_foot)
			var stance=.42 if abs(player.velocity.x)>220 else .50
			if previous_feet.size()==2 and player.foot_phase[i]<stance and previous_phase[i]<stance and player.is_on_floor() and abs(player.velocity.x)>50 and absf(player.foot_phase[i]-previous_phase[i])<.14:
				drifts.append(abs(world_foot.x-previous_feet[i].x))
		previous_feet=current; previous_phase=player.foot_phase.duplicate()
	var maximum=0.0
	for drift in drifts: maximum=maxf(maximum,drift)
	var report={"build":"0.5.0","frames":360,"fps":30,"duration_seconds":12,"scene":"Isolated flat locomotion study using the actual runtime controller and renderer. Not a campaign playthrough.","stance_samples":drifts.size(),"maximum_stance_world_x_drift_pixels":maximum,"grounded_pose_solver":"distance-driven stance locks, two-bone knees, authored arm/garment/ribbon motion"}
	var f=FileAccess.open(report_path("motion_review.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("MOTION_REVIEW_COMPLETE ",JSON.stringify(report)); call_deferred("quit_game")

func run_journey_checks():
	# Targeted native setups complement the separate continuous input-only route.
	var total=0
	for l in levels: total+=int(l.width)
	assert_check("journey_more_than_twice_previous_route",total>=55200,str(total))
	for index in range(5):
		load_chapter(index,false); mode="playing"; level=level.duplicate(true)
		level.erase("danger"); level.searchlight=false; level.hazard_lanes=[]
		var profile={}
		for p in level.ground:
			if p.has("profile") and p.profile.size()>2: profile=p; break
		# Camp's first mandatory gate lies on its slope. This isolated terrain
		# check uses the slope beyond that gate; the full traversal must clear it.
		var start=float(profile.x)+(850 if index==2 else 160)
		player.position=Vector2(start,surface_y_at(start,700)-2); boy.position=Vector2(start-52,surface_y_at(start-52,700)-2)
		player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO; player.reset_feet(); boy.reset_feet()
		for frame in range(15): await get_tree().physics_frame
		Input.action_press("right")
		var floor_frames=0; var errors=[]
		for frame in range(125):
			await get_tree().physics_frame
			if player.is_on_floor():
				floor_frames+=1
				for foot in range(2):
					if player.foot_phase[foot]<.5:
						var contact=player.position+player.feet[foot]
						errors.append(absf(contact.y-surface_y_at(contact.x,contact.y)))
		Input.action_release("right")
		var maximum=0.0
		for e in errors: maximum=maxf(maximum,e)
		assert_check("chapter_%d_native_slope_walk"%(index+1),player.position.x>start+270 and floor_frames>115,"distance=%0.2f grounded=%d"%[player.position.x-start,floor_frames])
		assert_check("chapter_%d_planted_slope_feet"%(index+1),not errors.is_empty() and maximum<4.0,"max vertical sole error=%0.3f"%maximum)
		checkpoint_x=float(profile.x)+400; respawn()
		assert_check("chapter_%d_slope_checkpoint_height"%(index+1),absf(player.position.y-(surface_y_at(checkpoint_x,700)-5))<.1)
	load_chapter(0,false); mode="playing"; level=level.duplicate(true); level.hazard_lanes=[]
	var relay={}; var brace={}; var clear={}
	for p in level.interact:
		if p.kind=="relay": relay=p
		if p.kind=="brace": brace=p
		if p.kind=="clear": clear=p
	player.position=Vector2(relay.x,relay.y-1); boy.position=Vector2(relay.x-220,relay.y-1); boy.following=false
	near_item=relay; player.action_time=0; interact()
	assert_check("shared_lift_refuses_distant_companion",pending_action.is_empty() and not flags.get(relay.id,false))
	boy.position=Vector2(relay.x-45,relay.y-1); boy.following=true; player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO
	await test_action(relay)
	assert_check("shared_lift_opens_physical_route",flags.get(relay.id,false) and gate_open(level.gates[-2]))
	player.position=Vector2(clear.x,clear.y-1); boy.position=Vector2(clear.x-45,clear.y-1); player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO
	await test_action(clear)
	assert_check("clearing_opens_its_gate",flags.get(clear.id,false) and gate_open(level.gates[-1]))
	player.position=Vector2(brace.x,brace.y-1); boy.position=Vector2(brace.x-45,brace.y-1); player.action_time=0; scrap=0; near_item=brace; interact()
	assert_check("brace_requires_real_salvage",pending_action.is_empty() and not flags.get(brace.id,false))
	scrap=1; await test_action(brace)
	assert_check("brace_consumes_one_salvage",flags.get(brace.id,false) and scrap==0)
	var roof_lane=levels[0].hazard_lanes[-1]
	assert_check("brace_permanently_stops_roof_hazard",not hazard_active(roof_lane) and not hazard_warning(roof_lane))
	# The actual authored lane timing can be observed before its active interval.
	load_chapter(2,false); mode="playing"; level=level.duplicate(true); level.erase("danger"); level.searchlight=false
	var h=level.hazard_lanes[-1]; level.hazard_lanes=[h]
	playtime=float(h.period)*10-float(h.offset)-.8
	assert_check("patrol_warning_precedes_active_sweep",hazard_warning(h) and not hazard_active(h))
	var center=float(h.x)+float(h.w)/2
	level.covers=[{"x":center-100,"w":120,"kind":"wall"}]; level.safe_zones=[]
	player.position=Vector2(center-100,surface_y_at(center-100,700)-1); boy.position=Vector2(center+100,surface_y_at(center+100,700)-1); boy.following=false
	Input.action_press("crouch"); boy.forced_crouch=true
	playtime=float(h.period)*10-float(h.offset)+.1; health=100; invulnerable=0
	for frame in range(83): await get_tree().physics_frame
	assert_check("patrol_can_find_exposed_boy",health<100,str(health))
	player.position=Vector2(center-120,surface_y_at(center-120,700)-1); boy.position=Vector2(center-80,surface_y_at(center-80,700)-1); player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO
	playtime=float(h.period)*10-float(h.offset)+.1; health=100; invulnerable=0; hazard_exposure.clear(); boy.forced_crouch=true
	for frame in range(83): await get_tree().physics_frame
	assert_check("patrol_cover_protects_both",health>99.9 and is_covered(player) and is_covered(boy),str(health))
	Input.action_release("crouch")
	load_chapter(2,false); mode="playing"; level=level.duplicate(true); level.hazard_lanes=[]; level.searchlight=false; level.covers=[]; level.safe_zones=[]
	player.position=Vector2(float(level.danger[1])+300,699); boy.position=Vector2(3000,699); boy.following=false
	health=100; invulnerable=0; shell_clock=10.79
	for frame in range(4): await get_tree().physics_frame
	assert_check("leaving_boy_in_shell_area_still_dangerous",health<100,str(health))
	level.erase("danger"); level.searchlight=true; player.position=Vector2(5000,699); health=100; invulnerable=0; exposure=0
	for frame in range(112):
		boy.position=Vector2(beam_x(),699); boy.velocity=Vector2.ZERO
		await get_tree().physics_frame
	assert_check("boy_still_detected_after_girl_leaves_searchlight_area",health<100,str(health))
	level.searchlight=false; level.hazard_lanes=[h]; hazard_exposure.clear()
	player.position=Vector2(center,surface_y_at(center,700)-1); boy.position=Vector2(h.x+h.w+350,699)
	playtime=float(h.period)*10-float(h.offset)+.1; health=100; invulnerable=0
	for frame in range(83): await get_tree().physics_frame
	assert_check("lane_stays_active_when_boy_is_ahead",health<100,str(health))
	load_chapter(0,false); mode="playing"; level=level.duplicate(true); level.covers=[]; level.safe_zones=[]
	var wind=level.hazard_lanes[0]; level.hazard_lanes=[wind]
	player.position=Vector2(wind.x+190,699); boy.position=Vector2(wind.x+140,699)
	player.velocity=Vector2.ZERO; boy.velocity=Vector2.ZERO; boy.following=true; stamina=100; wind_strain=false
	playtime=float(wind.period)*10-float(wind.offset)+.1
	for frame in range(80): await get_tree().physics_frame
	assert_check("exposed_wind_drains_stamina",stamina<92,str(stamina))
	assert_check("wind_reduces_uncrouched_speed",wind_speed_scale(player)<.7)
	Input.action_press("crouch"); stamina=70; wind_strain=false
	playtime=float(wind.period)*10-float(wind.offset)+.1
	for frame in range(80): await get_tree().physics_frame
	assert_check("crouching_steadies_both_in_wind",stamina>80 and not wind_strain and wind_speed_scale(player)==1.0,str(stamina))
	Input.action_release("crouch")
	load_chapter(3,false); mode="playing"; flags.erase("school_drain")
	assert_check("airborne_feet_do_not_count_as_wading",in_water(3100,699) and not in_water(3100,620))
	player.climbing=true; player.climb_clock=1; player.jump_buffer=.1; player.leap_axis=1; checkpoint_x=180; respawn(false)
	assert_check("recovery_clears_mantle_and_jump_state",not player.climbing and player.jump_buffer==0 and player.leap_axis==0)
	boy.following=false; player.position.x=600; boy.position.x=250
	for frame in range(3): await get_tree().physics_frame
	assert_check("waiting_companion_stays_low_after_separation",boy.crouching)
	var original_save=save_path; var original_settings=settings_path
	save_path="user://qa_v030_resources_"+str(Time.get_ticks_usec())+".json"; settings_path=save_path+".settings"
	smoke_test=false; journey_active=true; health=14; warmth=11; food=9; stamina=23; write_save()
	health=100; warmth=100; food=100; stamina=100; load_save(true)
	assert_check("continue_preserves_depleted_survival_resources",health==14 and warmth==11 and food==9 and stamina==23,"health=%s warmth=%s food=%s stamina=%s"%[health,warmth,food,stamina])
	DirAccess.remove_absolute(save_path); DirAccess.remove_absolute(settings_path); save_path=original_save; settings_path=original_settings; smoke_test=true
	var passed=true
	for result in test_log:
		if not result.passed: passed=false
	var report={"build":"0.5.0","all_passed":passed,"checks":test_log,"route_units":total,"method":"Native physics on authored slopes, measured planted sole heights, sloped checkpoint restoration, actual held shared lift and clearance, finite brace consumption, periodic warning and separate-child patrol exposure. Targeted setups are isolated from the continuous journey."}
	var f=FileAccess.open(report_path("journey_checks.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("JOURNEY_CHECKS_RESULT ",JSON.stringify(report)); call_deferred("quit_game",0 if passed else 1)

func capture_new_journey():
	var target=SubViewport.new(); target.size=Vector2i(3840,2160)
	target.size_2d_override=Vector2i(1600,900); target.size_2d_override_stretch=true
	target.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	get_tree().root.add_child(target); reparent(target); camera.make_current()
	var shots=[{"chapter":0,"x":5780,"name":"01_orchard_ridge"},{"chapter":1,"x":7550,"name":"02_rail_path"},{"chapter":2,"x":8760,"name":"03_carriage_lift"},{"chapter":3,"x":8420,"name":"04_courtyard_gully"},{"chapter":4,"x":9460,"name":"05_ash_garden"}]
	for shot in shots:
		load_chapter(shot.chapter,false); mode="playing"; chapter_card=0; message_time=0
		player.position=Vector2(shot.x,surface_y_at(shot.x,700)-2); boy.position=Vector2(shot.x-43,surface_y_at(shot.x-43,700)-2)
		camera.position.x=shot.x+170; player.reset_feet(); boy.reset_feet()
		for frame in range(45): await get_tree().process_frame
		if shot.chapter==2:
			update_prompt(); Input.action_press("interact"); interact()
			for frame in range(50): await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(report_path(shot.name+".png"))
		Input.action_release("interact")
	# Close view is explicitly a character study, separate from the gameplay zoom.
	load_chapter(0,false); mode="playing"; chapter_card=0; message_time=0
	for memory in level.memories: memories[memory.id]=memory.text
	player.position=Vector2(5780,surface_y_at(5780,700)-2); boy.position=Vector2(5738,surface_y_at(5738,700)-2)
	camera.zoom=Vector2(2.1,2.1)
	for frame in range(35): await get_tree().process_frame
	camera.position=Vector2(5760,550)
	await get_tree().process_frame; camera.position=Vector2(5760,550)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(report_path("06_character_close_study.png"))
	print("V030_NATIVE_4K_CAPTURE_COMPLETE"); call_deferred("quit_game")



func start_crossing():
	# A separate rehearsal save leaves the full journey intact.
	slice_active=false; section_preview=true; save_path=rehearsal_save_path
	journey_active=true; journey_completed=false; flags={}; memories={}; cache_remaining={}
	rations=0; scrap=0; medicine=1; health=82; warmth=38; food=39; stamina=100; wetness=.22
	load_chapter(2,false); mode="playing"; checkpoint_x=420; respawn(false)
	announce_message("THE FREIGHT CROSSING - Search the parcels, share warmth, keep low, and lift the loading bar together.",8)

func run_crossing_checks():
	await load("res://scripts/crossing_checks.gd").run(self)

func capture_crossing():
	await load("res://scripts/crossing_checks.gd").capture(self)
