extends RefCounted

const NativeInput=preload("res://scripts/sluice_checks.gd")
static var recording=false
static var recorded_frames=0
static var movie_folder=""
static var cues=[]

static func frames(g,count):
	for tick in range(count):
		await g.get_tree().physics_frame
		if recording:
			g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(1.7,1.7)
			g.camera.position=Vector2(clampf(g.player.position.x+45,12465,13010),590)
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%recorded_frames),.88)
			recorded_frames+=1

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func hold(g,action,ticks):
	var event=InputEventAction.new(); event.action=action; event.pressed=true; NativeInput.route_event(g,event)
	await frames(g,ticks)
	event=InputEventAction.new(); event.action=action; event.pressed=false; NativeInput.route_event(g,event)
	await frames(g,2)

static func add(checks,label,passed,details=""):
	checks.append({"check":label,"passed":passed,"details":details})

static func point(at): return {"x":at.x,"y":at.y}

static func find_node(g):
	for node in g.puzzle_encounters:
		if str(node.data.get("kind",""))=="garden_rope_ferry": return node
	return null

static func prepare(g,aboard=false):
	release(); g.flags={}; g.cache_remaining={}; g.water_offsets={}
	for gate in g.levels[4].gates: g.flags[gate.key]=true
	for bridge in g.levels[4].get("bridges",[]): g.flags[bridge.key]=true
	g.load_chapter(4,false); g.level=g.level.duplicate(true)
	g.level.hazard_lanes=[]; g.level.erase("danger"); g.level.searchlight=false
	g.mode="playing"; g.chapter_card=0; g.message_time=0
	g.health=100; g.warmth=100; g.food=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.rations=0; g.scrap=0; g.medicine=0; g.pending_action={}; g.action_progress=0; g.trail.clear()
	var node=find_node(g)
	if node==null: return null
	var x=node.body.position.x
	g.player.position=Vector2(x+44,node.deck_y()-2) if aboard else Vector2(12195,698)
	g.boy.position=Vector2(x+2,node.deck_y()-2) if aboard else Vector2(12152,698)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=not aboard
	g.player.reset_feet(); g.boy.reset_feet()
	if aboard: Input.action_press("crouch")
	await frames(g,20)
	return node

static func navigate(g,node,target_x,target_y,max_ticks=900,low=false):
	Input.action_release("interact"); Input.action_release("sprint")
	if low: Input.action_press("crouch")
	else: Input.action_release("crouch")
	var reached=false; var jump_hold=0
	for tick in range(max_ticks):
		await frames(g,1)
		if g.mode!="playing": break
		Input.action_release("left"); Input.action_release("right")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var girl_ready=absf(g.player.position.x-target_x)<9 and g.player.is_on_floor() and absf(g.player.position.y-target_y)<25
		var boy_ready=absf(g.boy.position.x-target_x)<84 and g.boy.is_on_floor() and absf(g.player.position.y-g.boy.position.y)<40
		if girl_ready and boy_ready: reached=true; break
		if not girl_ready:
			Input.action_press("right" if g.player.position.x<target_x else "left")
		if g.player.is_on_floor() and jump_hold==0 and not girl_ready and not low:
			for platform in g.level.platforms:
				var ahead=float(platform.x)-g.player.position.x
				var rise=g.player.position.y-float(platform.y)
				if ahead>0 and ahead<54 and rise>12 and rise<100:
					Input.action_press("jump"); jump_hold=27; break
		if absf(g.player.position.x-g.boy.position.x)>130 and g.boy.position.y>g.player.position.y+30: Input.action_release("right")
	Input.action_release("left"); Input.action_release("right"); Input.action_release("jump")
	return {"reached":reached,"girl":point(g.player.position),"boy":point(g.boy.position)}

static func shot(g,node,name):
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(1.7,1.7)
	var center=Vector2(node.body.position.x+15,590)
	g.camera.position=center; await g.get_tree().process_frame; g.camera.position=center
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func success(g,node,captures=false):
	var result={}; var initial=node.body.position.x; var mid_shot=false
	result["boarding"]=await navigate(g,node,initial+44,node.deck_y(),900,false)
	Input.action_press("crouch"); await frames(g,20)
	result["both_on_real_deck"]=node.both_boarded() and node.both_low()
	if captures: await shot(g,node,"24_garden_ferry_board")
	Input.action_press("interact")
	for tick in range(1600):
		await frames(g,1)
		if g.mode!="playing": break
		if captures and not mid_shot and node.travel>170:
			await shot(g,node,"25_garden_ferry_crossing"); mid_shot=true
		if node.moored: break
	Input.action_release("interact")
	result["native_travel"]=node.body.position.x-initial
	result["moored"]=node.moored and g.flags.get(node.data.key,false)
	result["actual_dock_contact"]=node.body.get_colliding_bodies().has(node.dock_body)
	result["crank_ticks"]=node.crank_ticks; result["both_riding_ticks"]=node.riding_ticks.both
	result["both_protected_ticks"]=node.protected_ticks.both; result["ride_wetness"]=g.wetness
	result["girl"]=point(g.player.position); result["boy"]=point(g.boy.position)
	if captures: await shot(g,node,"26_garden_ferry_moored")
	if not node.moored: return result
	result["exit"]=await navigate(g,node,float(node.cache_item.x),float(node.cache_item.y),1100,false)
	g.update_prompt(); await hold(g,"interact",90)
	result["reward_taken"]=g.flags.get(node.data.cache_id,false) and g.medicine==1
	result["health"]=g.health; result["medicine"]=g.medicine
	return result

static func run(g):
	recording=false; recorded_frames=0; movie_folder=""; cues=[]
	var checks=[]; var evidence={}
	var node=await prepare(g,true)
	if node==null: return {"all_passed":false,"checks":[{"check":"garden_ferry_instantiates","passed":false}]}
	add(checks,"ferry_is_actual_native_rigid_body",node.body is RigidBody2D and not node.body.freeze and node.body.get_meta("mechanism_drive_only",false))
	add(checks,"both_children_have_native_deck_floor_contacts",node.foot_contact(g.player) and node.foot_contact(g.boy))
	add(checks,"each_crouched_child_has_its_own_canvas_cover",node.is_covered(g.player) and node.is_covered(g.boy))
	var start=node.body.position.x
	await frames(g,80)
	add(checks,"unworked_ferry_does_not_auto_travel",absf(node.body.position.x-start)<.5)
	Input.action_release("crouch"); await frames(g,15); Input.action_press("interact"); await frames(g,60); release()
	add(checks,"standing_operator_cannot_drive_ferry",absf(node.body.position.x-start)<.5 and not node.is_covered(g.player))
	node=await prepare(g,true); g.boy.position=Vector2(12280,668); g.boy.velocity=Vector2.ZERO; await frames(g,16)
	start=node.body.position.x; Input.action_press("interact"); await frames(g,60); release()
	add(checks,"girl_aboard_cannot_leave_boy_on_bank",absf(node.body.position.x-start)<.5 and node.foot_contact(g.player) and not node.foot_contact(g.boy))
	add(checks,"boy_on_bank_does_not_borrow_girls_cover",not node.is_covered(g.boy))
	node=await prepare(g,true); g.player.position=Vector2(12280,668); g.player.velocity=Vector2.ZERO; await frames(g,16)
	start=node.body.position.x; Input.action_press("crouch"); Input.action_press("interact"); await frames(g,60); release()
	add(checks,"boy_aboard_cannot_depart_without_girl",absf(node.body.position.x-start)<.5 and node.foot_contact(g.boy) and not node.foot_contact(g.player))
	node=await prepare(g,true)
	start=node.body.position.x; Input.action_press("interact"); await frames(g,90); Input.action_release("interact")
	add(checks,"held_reel_moves_actual_body_and_both_riders",node.body.position.x-start>50 and node.foot_contact(g.player) and node.foot_contact(g.boy),str([node.body.position.x-start,point(g.player.position),point(g.boy.position)]))
	await frames(g,4); var stopped=node.body.position.x; await frames(g,60)
	add(checks,"released_reel_brakes_without_teleport",absf(node.body.position.x-stopped)<.5)
	for modal in ["pause","inventory"]:
		g.mode=modal; await frames(g,2); var at=node.body.position; var girl=g.player.position; var boy=g.boy.position
		await frames(g,35)
		add(checks,modal+"_holds_ferry_and_both_children",node.body.freeze and node.body.position.distance_to(at)<.01 and g.player.position.distance_to(girl)<.01 and g.boy.position.distance_to(boy)<.01)
		g.mode="playing"; await frames(g,4)
	g.checkpoint_x=12000; g.respawn(false); await frames(g,15)
	add(checks,"unsolved_recovery_restores_ferry_before_canal",not node.moored and node.body.position.distance_to(node.origin)<.5 and not g.flags.get(node.data.key,false))
	node=await prepare(g,true)
	g.player.position=Vector2(13170,706); g.boy.position=Vector2(13135,735); g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO
	await frames(g,20); g.update_prompt(); await hold(g,"interact",90)
	add(checks,"unmoored_ferry_cannot_grant_far_bank_medicine",g.medicine==0 and not g.flags.get(node.data.cache_id,false))
	node=await prepare(g)
	if "--record-garden-v044" in OS.get_cmdline_user_args():
		movie_folder=g.report_path("garden_v044_motion_frames"); DirAccess.make_dir_recursive_absolute(movie_folder); recording=true
		cues.append({"frame":0,"cue":"Native near-bank approach, boarding, crouching and held reel operate the real ferry; no actor/body repositioning follows this fixture."})
	evidence["continuous_success"]=await success(g,node)
	recording=false; var route=evidence.continuous_success
	add(checks,"native_bank_approach_boards_both_children",route.get("boarding",{}).get("reached",false) and route.get("both_on_real_deck",false),JSON.stringify(route.get("boarding",{})))
	add(checks,"continuous_native_crank_reaches_far_dock",route.get("moored",false) and route.get("native_travel",0)>440 and route.get("crank_ticks",0)>300,JSON.stringify(route))
	add(checks,"mooring_requires_real_dock_collision",route.get("actual_dock_contact",false))
	add(checks,"both_children_physically_ride_and_stay_dry",route.get("both_riding_ticks",0)>300 and route.get("both_protected_ticks",0)>300 and route.get("ride_wetness",1)<.01,JSON.stringify(route))
	add(checks,"both_children_exit_via_real_far_shore",route.get("exit",{}).get("reached",false),JSON.stringify(route.get("exit",{})))
	add(checks,"moored_pair_searches_finite_existing_medicine",route.get("reward_taken",false) and route.get("health",0)>99,JSON.stringify(route))
	g.update_prompt(); await hold(g,"interact",90)
	add(checks,"depleted_far_bank_reward_cannot_duplicate",g.medicine==1 and node.cache_contents().is_empty())
	node.reset_from_progress(); await frames(g,8)
	add(checks,"solved_recovery_preserves_mooring_and_spent_cache",node.moored and node.body.freeze and g.flags.get(node.data.cache_id,false) and absf(node.body.position.x-12880)<.5)
	var old_save=g.save_path; var old_settings=g.settings_path; var old_smoke=g.smoke_test
	g.save_path="user://qa_garden_ferry_"+str(Time.get_ticks_usec())+".json"; g.settings_path=g.save_path+".settings"
	g.smoke_test=false; g.journey_active=true; g.checkpoint_x=13200; g.write_save()
	g.flags={}; g.load_save(true); g.mode="playing"; node=find_node(g); await frames(g,8)
	add(checks,"native_save_resume_keeps_mooring_and_finite_reward",node!=null and node.moored and g.flags.get(node.data.cache_id,false))
	DirAccess.remove_absolute(g.save_path); DirAccess.remove_absolute(g.settings_path)
	g.save_path=old_save; g.settings_path=old_settings; g.smoke_test=old_smoke
	node=await prepare(g)
	var water_start=g.wetness; var low_route=await navigate(g,node,13185,700,1400,false)
	evidence["lower_wading_route"]=low_route
	add(checks,"lower_route_remains_native_walkable_for_both",low_route.reached and g.health>99,JSON.stringify(low_route))
	add(checks,"lower_route_has_real_cold_water_cost",g.wetness>water_start+.3 and not node.moored,str([water_start,g.wetness,g.warmth]))
	var near_checkpoint=false; var far_checkpoint=false; var hull_checkpoint=false
	for checkpoint in g.level.checkpoints:
		if absf(float(checkpoint)-12000)<.1: near_checkpoint=true
		if absf(float(checkpoint)-13200)<.1: far_checkpoint=true
		if float(checkpoint)>12330 and float(checkpoint)<13060: hull_checkpoint=true
	add(checks,"no_checkpoint_is_authored_inside_ferry_corridor",near_checkpoint and far_checkpoint and not hull_checkpoint)
	release(); var passed=true
	for check in checks:
		if not check.passed: passed=false
	return {"build":"0.4.4","all_passed":passed,"checks":checks,"evidence":evidence,"recorded_frames":recorded_frames,"fps":30,"recording":{"enabled":not movie_folder.is_empty(),"frames":recorded_frames,"fps":30,"duration_seconds":recorded_frames/30.0,"frame_directory":movie_folder,"cues":cues,"scope":"One near-bank fixture precedes native approach/jump, both-child boarding/crouch, held reel, native moving-platform ride, actual far-dock collision, shoreline exit and finite search. Refusal, release, modal pause, recovery, persistence and lower wading fixtures are separate."}}

static func capture(g):
	recording=false
	var node=await prepare(g); var route=await success(g,node,true) if node!=null else {}
	var report={"build":"0.4.4","all_states_reached":route.get("both_on_real_deck",false) and route.get("moored",false) and route.get("actual_dock_contact",false) and route.get("native_travel",0)>440 and route.get("reward_taken",false) and route.get("exit",{}).get("reached",false),"actual_sequence":route,"screenshots":["24_garden_ferry_board.png","25_garden_ferry_crossing.png","26_garden_ferry_moored.png"]}
	var file=FileAccess.open(g.report_path("garden_v044_capture.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("GARDEN_CAPTURE_RESULT ",JSON.stringify(report))
