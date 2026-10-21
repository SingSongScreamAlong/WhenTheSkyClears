extends RefCounted

const NativeInput=preload("res://scripts/sluice_checks.gd")
static var recording=false
static var recorded_frames=0
static var movie_folder=""
static var recording_cues=[]

static func frames(g,count):
	for tick in range(count):
		await g.get_tree().physics_frame
		if recording:
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%recorded_frames),.88)
			recorded_frames+=1

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func hold_action(g,action,count):
	var event=InputEventAction.new(); event.action=action; event.pressed=true; NativeInput.route_event(g,event)
	await frames(g,count)
	event=InputEventAction.new(); event.action=action; event.pressed=false; NativeInput.route_event(g,event)
	await frames(g,2)

static func add(checks,name,passed,details=""):
	checks.append({"check":name,"passed":passed,"details":details})

static func point(position): return {"x":position.x,"y":position.y}

static func find_node(g):
	for node in g.get("trolley_encounters") if g.get("trolley_encounters")!=null else []:
		if node.data.id=="school_trolley": return node
	return null

static func prepare(g,cart_x=0.0,boy_offset=-112.0,boy_follows=true):
	release(); g.flags={}; g.cache_remaining={}; g.water_offsets={}
	for gate in g.levels[3].gates: g.flags[gate.key]=true
	for bridge in g.levels[3].get("bridges",[]): g.flags[bridge.key]=true
	g.load_chapter(3,false); g.level=g.level.duplicate(true)
	var target_lanes=[]
	for lane in g.level.hazard_lanes:
		if lane.kind=="sweep" and int(lane.x)==10420: target_lanes.append(lane)
	g.level.hazard_lanes=target_lanes; g.level.erase("danger"); g.level.searchlight=false
	g.mode="playing"; g.chapter_card=0; g.message_time=0
	g.health=100; g.food=100; g.warmth=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.rations=0; g.scrap=0; g.medicine=0; g.trail.clear(); g.pending_action={}; g.action_progress=0
	g.playtime=0.0; g.hazard_exposure.clear()
	var node=find_node(g)
	if node==null: return null
	if cart_x>0:
		node.body.position=Vector2(cart_x,g.surface_y_at(cart_x,700)-24)
		node.body.linear_velocity=Vector2.ZERO; node.previous_x=cart_x
	var x=node.body.position.x
	g.player.position=Vector2(x-62,g.surface_y_at(x-62,700)-2)
	g.boy.position=Vector2(x+boy_offset,g.surface_y_at(x+boy_offset,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=boy_follows
	g.player.reset_feet(); g.boy.reset_feet()
	Input.action_press("crouch"); await frames(g,18)
	return node

static func active_sweep(g):
	# This is the existing real lane's normal active phase, selected only at
	# fixture setup. No hazard is overridden during either measured crossing.
	g.playtime=5.05; g.invulnerable=0; g.hazard_exposure.clear()

static func navigate(g,node,target_x,max_ticks=600):
	var reached=false; var jump_hold=0
	Input.action_release("crouch"); Input.action_release("interact")
	for tick in range(max_ticks):
		await frames(g,1)
		if g.mode!="playing": break
		Input.action_release("left"); Input.action_release("right")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var girl_ready=absf(g.player.position.x-target_x)<12 and g.player.is_on_floor()
		var boy_ready=absf(g.boy.position.x-target_x)<88 and g.boy.is_on_floor() and absf(g.boy.position.y-g.player.position.y)<40
		if girl_ready and boy_ready: reached=true; break
		if not girl_ready:
			if g.player.position.x<target_x-8: Input.action_press("right")
			elif g.player.position.x>target_x+12: Input.action_press("left")
		if absf(g.player.position.x-g.boy.position.x)>125 and g.boy.position.y>=g.player.position.y-20: Input.action_release("right")
		if g.player.is_on_floor() and jump_hold==0 and not girl_ready:
			for obstacle in node.obstacle_rects():
				var ahead=obstacle.position.x-g.player.position.x
				var rise=g.player.position.y-obstacle.position.y
				if ahead>0 and ahead<58 and rise>12 and rise<110:
					Input.action_press("jump"); jump_hold=24; break
	release()
	return {"reached":reached,"girl":point(g.player.position),"boy":point(g.boy.position)}

static func shot(g,name,node):
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(1.7,1.7)
	var center=Vector2(node.body.position.x-32,node.cart_floor()-100)
	if name!="17_trolley_cover": center=Vector2(10990,587)
	g.camera.position=center; await g.get_tree().process_frame; g.camera.position=center
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func success(g,node,captures=false):
	var result={}; var shot_done=false
	var start=node.body.position.x; var initial_health=g.health
	Input.action_press("crouch"); Input.action_press("interact"); Input.action_press("right")
	for tick in range(2100):
		await frames(g,1)
		if g.mode!="playing": break
		if captures and not shot_done and node.body.position.x>10625:
			await shot(g,"17_trolley_cover",node); shot_done=true
		if node.docked: break
	release()
	result["held_push"]=node.push_ticks>60
	result["actual_travel"]=node.body.position.x-start
	result["docked"]=node.docked and g.flags.get(node.data.key,false)
	result["push_contact_ticks"]=node.push_ticks
	result["both_cover_ticks"]=node.protected_ticks.both
	result["both_protected"]=node.protected_ticks.both>180 and g.health>=initial_health-.1
	result["health"]=g.health
	result["body"]=point(node.body.position); result["hatch_amount"]=node.hatch_amount
	if captures: await shot(g,"18_trolley_dock",node)
	if not node.docked: return result
	result["reunion"]=await navigate(g,node,float(node.data.cache_x)-52,900)
	await frames(g,45)
	result["settled_spacing"]=absf(g.player.position.x-g.boy.position.x)
	result.reunion["settled_girl"]=point(g.player.position); result.reunion["settled_boy"]=point(g.boy.position)
	if captures: await shot(g,"19_trolley_reunion",node)
	g.update_prompt(); await hold_action(g,"interact",90)
	result["reward_taken"]=g.flags.get(node.data.cache_id,false) and g.medicine==1 and g.scrap==1
	result["medicine"]=g.medicine; result["scrap"]=g.scrap
	result["girl"]=point(g.player.position); result["boy"]=point(g.boy.position)
	result["exit"]=await navigate(g,node,float(node.data.cache_x)+170,1000)
	return result

static func run(g):
	recording=false; recorded_frames=0; movie_folder=""; recording_cues=[]
	if "--trolley-subviewport" in OS.get_cmdline_user_args():
		var target=SubViewport.new(); target.size=Vector2i(1600,900)
		g.get_tree().root.add_child(target); g.reparent(target); g.camera.make_current(); await frames(g,2)
	var checks=[]; var evidence={}
	var node=await prepare(g,10650,-112,false)
	if node==null: return {"all_passed":false,"checks":[{"check":"authored_trolley_instantiates","passed":false}]}
	add(checks,"native_chassis_uses_real_rigid_body",node.body is RigidBody2D and node.body.collision_layer==1 and not node.body.freeze)
	var wheel_error=0.0
	for center in node.wheel_centers():
		var query=PhysicsRayQueryParameters2D.create(center-Vector2(0,6),center+Vector2(0,36),1,[node.body.get_rid()])
		var hit=g.get_world_2d().direct_space_state.intersect_ray(query)
		wheel_error=maxf(wheel_error,absf(float(hit.position.y)-center.y-18) if not hit.is_empty() else INF)
	add(checks,"drawn_wheels_contact_actual_sloped_ground",wheel_error<.4,str(wheel_error))
	add(checks,"both_crouched_children_fit_actual_canvas",node.is_covered(g.player) and node.is_covered(g.boy),str([point(g.player.position),point(g.boy.position),node.cart_floor()]))
	active_sweep(g); await frames(g,100)
	add(checks,"moving_canvas_protects_both_from_actual_sweep",g.health>99 and g.is_covered(g.player) and g.is_covered(g.boy),str(g.health))
	node=await prepare(g,10650,-200,false); active_sweep(g); await frames(g,100)
	add(checks,"exposed_boy_is_not_protected_by_girls_canvas",node.is_covered(g.player) and not g.is_covered(g.boy) and g.health<99,str(g.health))
	node=await prepare(g,10650,-112,false)
	g.player.position=Vector2(node.body.position.x-200,g.surface_y_at(node.body.position.x-200,700)-2)
	await frames(g,8); active_sweep(g); await frames(g,100)
	add(checks,"exposed_girl_is_not_protected_by_boys_canvas",not g.is_covered(g.player) and node.is_covered(g.boy) and g.health<99,str(g.health))
	node=await prepare(g,10650,-112,false)
	Input.action_release("crouch"); await frames(g,12); active_sweep(g); await frames(g,100)
	add(checks,"standing_under_canvas_is_still_exposed",not node.is_covered(g.player) and g.health<99,str(g.health))
	# Start on ordinary near-bank ground. From this point success never moves
	# actors, bodies, resources or flags by script; only held native Input acts.
	node=await prepare(g)
	var original=node.body.position.x
	Input.action_press("right"); await frames(g,50); release(); await frames(g,15)
	add(checks,"walking_into_cart_without_E_does_not_drive_it",absf(node.body.position.x-original)<3,str(node.body.position.x-original))
	Input.action_press("crouch"); Input.action_press("interact"); Input.action_press("right"); await frames(g,90); release()
	add(checks,"held_E_contact_physically_pushes_cart",node.body.position.x-original>30 and node.push_ticks>20,str([node.body.position.x-original,node.push_ticks]))
	await frames(g,40); var stopped=node.body.position.x; await frames(g,70)
	add(checks,"released_parking_brake_stops_cart_on_slope",absf(node.body.position.x-stopped)<2.5,str(node.body.position.x-stopped))
	for modal in ["pause","inventory"]:
		g.mode=modal; await frames(g,2); var position=node.body.position
		await frames(g,40)
		add(checks,modal+"_freezes_real_cart",node.body.freeze and node.body.position.distance_to(position)<.01)
		g.mode="playing"; await frames(g,4)
	g.checkpoint_x=10230; g.respawn(false); await frames(g,12)
	add(checks,"unsolved_respawn_restores_cart_and_closed_hatch",not node.docked and node.body.position.distance_to(node.origin)<2 and node.hatch_amount==0 and not g.flags.get(node.data.key,false),str([point(node.body.position),point(node.origin),node.hatch_amount,node.docked]))
	# A right-side supply attempt cannot claim a cabinet which has not opened.
	g.player.position=Vector2(node.cabinet.x-52,698); g.boy.position=Vector2(node.cabinet.x-94,698)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; await frames(g,15)
	g.update_prompt(); await hold_action(g,"interact",100)
	add(checks,"closed_hatch_refuses_reward_from_far_approach",g.medicine==0 and g.scrap==0 and not g.flags.get(node.data.cache_id,false))
	node=await prepare(g)
	if "--record-trolley" in OS.get_cmdline_user_args():
		movie_folder=g.report_path("trolley_motion_frames"); DirAccess.make_dir_recursive_absolute(movie_folder); recording=true
		recording_cues.append({"frame":0,"cue":"Both children crouch beneath canvas; held E pushes the native cart through the sweep."})
	evidence["continuous_success"]=await success(g,node)
	recording=false
	var route=evidence.continuous_success
	add(checks,"continuous_push_reaches_real_far_dock",route.get("docked",false) and route.get("held_push",false) and route.get("actual_travel",0)>550,JSON.stringify(route))
	add(checks,"both_children_survive_under_moving_canvas",route.get("both_protected",false) and route.get("health",0)>99,JSON.stringify(route))
	add(checks,"dock_opens_real_rotating_hatch",node.docked and node.hatch_amount>=1 and absf(node.hatch_body.rotation)>1)
	add(checks,"boy_navigates_cart_to_reunite_at_cabinet",route.get("reunion",{}).get("reached",false),JSON.stringify(route.get("reunion",{})))
	add(checks,"natural_reunion_keeps_child_silhouettes_apart",route.get("settled_spacing",0)>20,str(route.get("settled_spacing",0)))
	add(checks,"both_can_clear_the_opened_supply_cabinet",route.get("exit",{}).get("reached",false),JSON.stringify(route.get("exit",{})))
	add(checks,"native_search_grants_finite_medicine_and_iron",route.get("reward_taken",false),str([g.medicine,g.scrap]))
	add(checks,"exhausted_cart_objective_moves_on",route.get("reward_taken",false) and "packed" in node.objective_text(),node.objective_text())
	g.update_prompt(); await hold_action(g,"interact",100)
	add(checks,"depleted_cabinet_cannot_duplicate_resources",g.medicine==1 and g.scrap==1 and node.cache_contents().is_empty())
	# Real resource transfer with a full medicine slot leaves its source sprite.
	g.flags.erase(node.data.cache_id); g.cache_remaining[node.data.cache_id]={"rations":0,"medicine":1,"scrap":1}
	g.medicine=2; g.scrap=0; g.player.action_time=0
	g.complete_interaction(node.cache_item)
	add(checks,"partial_search_keeps_only_uncollected_painted_medicine",g.medicine==2 and g.scrap==1 and node.cache_contents()==["medicine"] and not g.flags.get(node.data.cache_id,false),str(node.cache_contents()))
	g.medicine=0; g.player.action_time=0; g.complete_interaction(node.cache_item)
	add(checks,"remaining_medicine_is_finite_after_partial_search",g.medicine==1 and node.cache_contents().is_empty() and g.flags.get(node.data.cache_id,false))
	node.reset_from_progress(); await frames(g,4)
	add(checks,"solved_reset_preserves_docked_cart_and_open_hatch",node.docked and node.body.freeze and absf(node.body.position.x-float(node.data.dock_x))<.01 and node.hatch_amount==1)
	add(checks,"open_cabinet_reports_its_actual_physical_top",absf(node.obstacle_rects()[1].position.y-(node.cabinet.y-38))<.01)
	var lid_center=node.hatch_body.position+Vector2(-36,-5).rotated(node.hatch_body.rotation)
	var lid_query=PhysicsRayQueryParameters2D.create(Vector2(lid_center.x,500),Vector2(lid_center.x,720),1)
	var lid_hit=g.get_world_2d().direct_space_state.intersect_ray(lid_query)
	var lid_error=absf(node.support_at(lid_center.x,float(lid_hit.position.y))-float(lid_hit.position.y)) if not lid_hit.is_empty() else INF
	add(checks,"rotated_lid_support_matches_native_collision",lid_error<.4,str(lid_error))
	var original_save=g.save_path; var original_settings=g.settings_path; var prior_smoke=g.smoke_test
	g.save_path="user://qa_trolley_"+str(Time.get_ticks_usec())+".json"; g.settings_path=g.save_path+".settings"
	g.smoke_test=false; g.journey_active=true; g.checkpoint_x=11000; g.write_save()
	g.flags={}; g.load_save(true); g.mode="playing"; node=find_node(g); await frames(g,4)
	add(checks,"save_resume_restores_solved_cart_and_spent_reward",node!=null and node.docked and node.hatch_amount==1 and g.flags.get(node.data.cache_id,false))
	DirAccess.remove_absolute(g.save_path); DirAccess.remove_absolute(g.settings_path)
	g.save_path=original_save; g.settings_path=original_settings; g.smoke_test=prior_smoke
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	return {"build":"0.4.3","all_passed":passed,"checks":checks,"evidence":evidence,"recorded_frames":recorded_frames,"recording":{"enabled":not movie_folder.is_empty(),"frames":recorded_frames,"fps":30,"frame_directory":movie_folder,"cues":recording_cues,"scope":"Continuous native crouch, held E push, actual slope travel, dock ratchet, reunion and finite search after one explicit near-bank setup. Refusal/exposure/pause/save fixtures are excluded."},"method":"Actual school sweep lane and native rigid body. Isolated setups test each child's exposure, release, modal pause, recovery and persistence. Success uses native held movement/E/crouch/jump and actual floor/contact ticks without repositioning, flags or resource grants."}

static func capture(g):
	recording=false
	var node=await prepare(g)
	var route=await success(g,node,true) if node!=null else {}
	var report={"build":"0.4.3","all_states_reached":route.get("held_push",false) and route.get("docked",false) and route.get("both_protected",false) and route.get("reward_taken",false) and route.get("reunion",{}).get("reached",false) and route.get("exit",{}).get("reached",false),"actual_sequence":route,"screenshots":["17_trolley_cover.png","18_trolley_dock.png","19_trolley_reunion.png"]}
	var file=FileAccess.open(g.report_path("trolley_capture.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("TROLLEY_CAPTURE_RESULT ",JSON.stringify(report))
