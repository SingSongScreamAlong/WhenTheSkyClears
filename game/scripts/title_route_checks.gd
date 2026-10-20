extends SceneTree

# Isolated reachability/diagnostic fixture for the authored Ash title steps and
# the following gap. This script is intentionally separate from release code.
func _initialize(): call_deferred("local_run")

func local_run():
	var scene=load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)
	scene.smoke_test=true; scene.journey_active=false
	if is_instance_valid(scene.ambience): scene.ambience.stop()
	var report=await run(scene)
	var folder=scene.report_path("title_route_checks.json")
	var file=FileAccess.open(folder,FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("TITLE_ROUTE_CHECKS_RESULT ",JSON.stringify(report))
	quit(0 if report.all_passed else 1)

static func release_inputs():
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)

static func vector(v): return {"x":v.x,"y":v.y}

static func actor(child):
	var contacts=[]
	for index in range(child.get_slide_collision_count()):
		var contact=child.get_slide_collision(index); var body=contact.get_collider()
		contacts.append({"normal":vector(contact.get_normal()),"position":vector(contact.get_position()),"collider":str(body.get_path()) if body is Node else str(body)})
	return {"position":vector(child.position),"velocity":vector(child.velocity),"floor":child.is_on_floor(),"wall":child.is_on_wall(),"climbing":child.climbing,"climb_clock":child.climb_clock,"climb_target":vector(child.climb_target),"climb_direction":child.climb_direction,"mantle_count":child.mantle_count,"mantle_phase":child.get("mantle_phase"),"mantle_blend":child.get("mantle_blend"),"animation_state":child.get("animation_state"),"input_axis":child.input_axis,"ai_axis":child.ai_axis,"ai_jump":child.ai_jump,"leap_axis":child.leap_axis,"following":child.following,"forced_crouch":child.forced_crouch,"crouching":child.crouching,"collider_height":child.col.shape.size.y,"coyote":child.coyote,"jump_buffer":child.jump_buffer,"jump_released":child.get("jump_released"),"action_time":child.action_time,"contacts":contacts}

static func fixture(g):
	release_inputs(); g.flags={}; g.cache_remaining={}; g.load_chapter(4,false)
	g.level=g.level.duplicate(true); g.level.hazard_lanes=[]; g.level.searchlight=false; g.level.erase("danger")
	g.mode="playing"; g.health=100; g.food=100; g.warmth=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.rations=0; g.scrap=0; g.medicine=0; g.pending_action={}; g.trail.clear()
	g.player.position=Vector2(3500,698); g.boy.position=Vector2(3448,698)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.player.reset_feet(); g.boy.reset_feet(); g.boy.following=true
	for frame in range(12): await g.get_tree().physics_frame

static func scenario(g,deliberate):
	await fixture(g)
	var samples=[]; var launches=[]; var prior_boy_vy=0.0; var reached=false; var failure=""; var jump_hold=0; var jump_sprinting=false; var jump_inputs=0
	var first_girl=false; var first_boy=false; var second_girl=false; var second_boy=false
	var farthest=g.player.position.x; var stalled=0; var frames=0; var stage=0
	for frame in range(1800):
		await g.get_tree().physics_frame; frames=frame+1
		if g.boy.velocity.y< -200 and prior_boy_vy>=0:
			var candidates=[]
			for old in g.trail:
				if absf(old.x-g.boy.position.x)<30 and old.y<g.boy.position.y-38: candidates.append({"x":old.x,"y":old.y,"relative_x":old.x-g.boy.position.x})
			launches.append({"frame":frame,"boy":actor(g.boy),"girl":actor(g.player),"nearby_raised_trail":candidates})
		prior_boy_vy=g.boy.velocity.y
		if frame%20==0 or (stalled>120 and frame%5==0): samples.append({"frame":frame,"mode":g.mode,"girl":actor(g.player),"boy":actor(g.boy),"jump_held":Input.is_action_pressed("jump"),"sprint_held":Input.is_action_pressed("sprint")})
		if g.mode!="playing": failure="Native route entered mode "+str(g.mode); break
		if g.player.position.x>farthest+3: farthest=g.player.position.x; stalled=0
		else: stalled+=1
		if stalled>240: failure="No forward progress for four simulated seconds"; break
		for child in [g.player,g.boy]:
			if child.is_on_floor() and child.position.x>3570 and child.position.x<3750 and absf(child.position.y-640)<3:
				if child==g.player: first_girl=true
				else: first_boy=true
			if child.is_on_floor() and child.position.x>3810 and child.position.x<4010 and absf(child.position.y-580)<3:
				if child==g.player: second_girl=true
				else: second_boy=true
		if g.player.position.x>=4450 and g.boy.position.x>=4370 and g.player.is_on_floor() and g.boy.is_on_floor(): reached=true; break
		Input.action_release("left"); Input.action_press("right"); Input.action_release("sprint"); Input.action_release("crouch")
		if g.player.position.x>=4450: Input.action_release("right")
		if absf(g.player.position.x-g.boy.position.x)>155: Input.action_release("right")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		if deliberate and stage<2:
			var target_x=3715.0 if stage==0 else 3975.0
			var target_y=640.0 if stage==0 else 580.0
			if absf(g.player.position.x-target_x)<15 and g.player.is_on_floor() and absf(g.player.position.y-target_y)<3:
				Input.action_release("right")
				if absf(g.boy.position.x-target_x)<100 and g.boy.is_on_floor() and absf(g.boy.position.y-target_y)<3: stage+=1; stalled=0
		var need_jump=false; var gap_leap=false
		if g.player.is_on_floor():
			if not g.ground_at(g.player.position.x+30): need_jump=true; gap_leap=true; Input.action_press("sprint")
			for p in g.level.platforms:
				if not p.get("optional_route",false) and p.x-g.player.position.x>0 and p.x-g.player.position.x<45 and p.y<g.player.position.y-12 and p.y>g.player.position.y-145: need_jump=true
		if need_jump and jump_hold==0:
			Input.action_press("jump"); jump_hold=24; jump_sprinting=gap_leap; jump_inputs+=1
		if not g.player.is_on_floor() and jump_sprinting: Input.action_press("sprint")
	release_inputs()
	return {"policy":"deliberate waiting on both title treads" if deliberate else "same platform/gap Input decisions as uninterrupted traversal","reached_4450_with_boy":reached,"girl_first_tread":first_girl,"boy_first_tread":first_boy,"girl_second_tread":second_girl,"boy_second_tread":second_boy,"frames":frames,"jump_inputs":jump_inputs,"failure":failure,"final_mode":g.mode,"final_girl":actor(g.player),"final_boy":actor(g.boy),"launches":launches,"samples":samples}

static func run(g):
	var routes=[]
	routes.append(await scenario(g,false))
	routes.append(await scenario(g,true))
	var passed=true
	for result in routes:
		if not result.reached_4450_with_boy: passed=false
	return {"all_passed":passed,"scenarios":routes,"scope":"Targeted native Ash title-step and gap reachability. Each fixture starts both children once on authored ground at3500/3448, disables timed dangers and sets initial survival stats. Thereafter real Input, collision and existing companion AI drive movement; there are no actor repositions, collision edits or resource grants. Detailed physics/mantle/AI/contact snapshots are diagnostics, not a full journey test."}
