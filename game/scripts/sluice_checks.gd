extends RefCounted

static var recording=false
static var movie_folder=""
static var recorded_frames=0

static func frames(g,count):
	for frame in range(count):
		await g.get_tree().physics_frame
		if recording:
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%recorded_frames),.88)
			recorded_frames+=1

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func route_event(g,event):
	# Four-kilopixel review reparents the game into a SubViewport. OS events
	# enter the root window, so deliver to the actual playing viewport there.
	# push_input keeps the native _unhandled_input path; key state is explicit
	# because injected local viewport events do not update the Input singleton.
	if g.get_viewport() is SubViewport:
		if event.pressed: Input.action_press(event.action)
		else: Input.action_release(event.action)
		g.get_viewport().push_input(event,true)
	else: Input.parse_input_event(event)

static func command(g,action):
	# Input.action_press updates key state but does not deliver _unhandled_input.
	# Parse a native action event so Q uses the same command path as the keyboard.
	var event=InputEventAction.new(); event.action=action; event.pressed=true
	route_event(g,event); await frames(g,2)
	event=InputEventAction.new(); event.action=action; event.pressed=false
	route_event(g,event); await frames(g,2)

static func hold_action(g,action,count):
	var event=InputEventAction.new(); event.action=action; event.pressed=true
	route_event(g,event); await frames(g,count)
	event=InputEventAction.new(); event.action=action; event.pressed=false
	route_event(g,event); await frames(g,2)

static func point(position): return {"x":position.x,"y":position.y}

static func add(checks,name,passed,detail=""):
	checks.append({"check":name,"passed":passed,"details":detail})

static func find_data(g):
	for item in g.levels[1].get("mechanisms",[]):
		if item.kind=="counterweight_crossing": return item
	return {}

static func find_node(g,data):
	for node in g.get("sluice_encounters") if g.get("sluice_encounters")!=null else []:
		if node.data.id==data.id: return node
	return null

static func prepare(g):
	release(); g.flags={}; g.cache_remaining={}; g.water_offsets={}
	var data=find_data(g)
	for gate in g.levels[1].gates: g.flags[gate.key]=true
	for bridge in g.levels[1].get("bridges",[]): g.flags[bridge.key]=true
	g.load_chapter(1,false); g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.hazard_lanes=[]; g.level.searchlight=false
	g.mode="playing"; g.health=100; g.warmth=100; g.food=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.scrap=0; g.rations=0; g.medicine=0; g.trail.clear(); g.pending_action={}; g.action_progress=0
	g.chapter_card=0; g.message_time=0
	var start=float(data.get("entry_x",14770))
	g.player.position=Vector2(start,g.surface_y_at(start,700)-2)
	g.boy.position=Vector2(start-49,g.surface_y_at(start-49,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.player.reset_feet(); g.boy.reset_feet()
	await frames(g,12)
	return find_node(g,data)

static func navigate(g,target_x,target_y,climb,require_boy,max_frames,node=null):
	var jump_hold=0; var reached=false; var bridge_frames=0; var ticks=0
	var contact_start=node.contact_ticks(g.player) if is_instance_valid(node) else 0
	for tick in range(max_frames):
		await frames(g,1); ticks=tick+1
		if g.mode!="playing": break
		Input.action_release("left"); Input.action_release("right"); Input.action_release("sprint"); Input.action_release("crouch")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		if is_instance_valid(node) and node.is_on_bridge(g.player): bridge_frames+=1
		var girl_ready=absf(g.player.position.x-target_x)<12 and g.player.is_on_floor() and absf(g.player.position.y-target_y)<23
		var boy_ready=absf(g.boy.position.x-target_x)<83 and g.boy.is_on_floor() and absf(g.boy.position.y-target_y)<23
		if girl_ready and (boy_ready or not require_boy): reached=true; break
		if not girl_ready:
			if g.player.position.x<target_x-8: Input.action_press("right")
			elif g.player.position.x>target_x+8: Input.action_press("left")
		if require_boy and absf(g.player.position.x-g.boy.position.x)>125 and absf(g.player.position.y-g.boy.position.y)<30: Input.action_release("right")
		if climb and g.player.is_on_floor() and jump_hold==0 and not girl_ready:
			for platform in g.level.platforms:
				var ahead=float(platform.x)-g.player.position.x; var rise=g.player.position.y-float(platform.y)
				if ahead>0 and ahead<57 and rise>12 and rise<145:
					Input.action_press("jump"); jump_hold=24; break
	release()
	var contact_ticks=node.contact_ticks(g.player)-contact_start if is_instance_valid(node) else 0
	return {"reached":reached,"frames":ticks,"bridge_floor_frames":contact_ticks,"bridge_floor_ticks":contact_ticks,"bridge_floor_seconds":float(contact_ticks)/Engine.physics_ticks_per_second,"bridge_render_samples":bridge_frames,"girl":point(g.player.position),"boy":point(g.boy.position)}

static func approach(g,node):
	var legs=[]; var reached=true
	for destination in [Vector2(14922,625),Vector2(15108,570)]:
		var leg=await navigate(g,destination.x,destination.y,true,true,900,node)
		legs.append(leg); reached=reached and leg.reached
		if not leg.reached: break
	return {"reached":reached,"legs":legs}

static func shot(g,name,node):
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(1.62,1.62)
	g.camera.position=Vector2(node.hinge.x+70,515)
	await g.get_tree().process_frame; g.camera.position=Vector2(node.hinge.x+70,515)
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func success(g,node,capture_images=false):
	var result={"approach":await approach(g,node)}
	if not result.approach.reached: return result
	await command(g,"companion")
	result["q_wait_used"]=not g.boy.following
	var held=false
	for tick in range(150):
		await frames(g,1)
		if node.lower_amount>=.999 and node.plate_child=="Boy": held=true; break
	result["boy_holds"]=held
	result["waiting_prompt"]=node.objective_text()
	result["wait_positions"]={"girl":point(g.player.position),"boy":point(g.boy.position),"holder":node.plate_child}
	if capture_images: await shot(g,"13_counterweight_wait",node)
	if not held: return result
	result["crossing"]=await navigate(g,node.hinge.x+node.span*.53,node.hinge.y,false,false,500,node)
	if capture_images: await shot(g,"14_counterweight_crossing",node)
	result["far_treadle"]=await navigate(g,float(node.data.latch_x),node.hinge.y,false,false,450,node)
	await frames(g,6)
	result["latched"]=node.latched and g.flags.get(node.data.key,false)
	result["holder_at_latch"]=node.plate_child
	result["far_child"]=node.far_child
	await command(g,"companion")
	result["q_call_used"]=g.boy.following
	result["called_prompt"]=node.objective_text()
	var boy_floor=0; var reunited=false
	var boy_contact_start=node.contact_ticks(g.boy)
	for tick in range(650):
		await frames(g,1)
		if node.is_on_bridge(g.boy): boy_floor+=1
		if g.boy.position.x>node.hinge.x+node.span+12 and absf(g.boy.position.y-node.hinge.y)<8 and g.boy.is_on_floor(): reunited=true; break
	result["boy_bridge_frames"]=node.contact_ticks(g.boy)-boy_contact_start
	result["boy_bridge_ticks"]=node.contact_ticks(g.boy)-boy_contact_start
	result["boy_bridge_seconds"]=float(result.boy_bridge_ticks)/Engine.physics_ticks_per_second
	result["boy_bridge_render_samples"]=boy_floor
	result["reunited"]=reunited
	if capture_images: await shot(g,"15_counterweight_reunion",node)
	var cache={}
	for item in g.level.interact:
		if item.get("id","")==node.data.cache_id: cache=item
	if not cache.is_empty() and reunited:
		result["cache_approach"]=await navigate(g,float(cache.x)-12,float(cache.y),false,true,300,node)
		g.update_prompt(); await hold_action(g,"interact",ceili(float(cache.hold_seconds)*60)+6); release()
	result["resources"]={"rations":g.rations,"medicine":g.medicine,"health":g.health}
	result["girl"]=point(g.player.position); result["boy"]=point(g.boy.position)
	return result

static func run(g):
	recording=false; recorded_frames=0
	if "--sluice-subviewport" in OS.get_cmdline_user_args():
		# Repeat the same input/physics assertions under the capture topology,
		# including in a headless renderer; this does not stand in for visual QA.
		var target=SubViewport.new(); target.size=Vector2i(1600,900)
		g.get_tree().root.add_child(target); g.reparent(target); g.camera.make_current()
		await frames(g,2)
	var checks=[]; var evidence={}
	var node=await prepare(g)
	if node==null: return {"all_passed":false,"checks":[{"check":"counterweight_native_component_exists","passed":false}]}
	add(checks,"raised_span_has_real_rotated_support",not node.latched and node.lower_amount==0 and absf(node.bridge_body.rotation)>1 and node.bridge_body.collision_layer==1)
	# Initial far-bank fixture proves both the latch and resource are guarded.
	g.player.position=Vector2(float(node.data.latch_x),node.hinge.y-2)
	g.boy.position=Vector2(14740,g.surface_y_at(14740,700)-2); g.boy.following=false
	await frames(g,25)
	add(checks,"far_treadle_cannot_latch_without_other_child",not node.latched and not g.flags.get(node.data.key,false))
	g.player.position=Vector2(15480,node.hinge.y-2); await frames(g,5); g.update_prompt()
	var before=[g.rations,g.medicine]
	await hold_action(g,"interact",100); release()
	add(checks,"keeper_cache_refuses_unsolved_right_approach",g.near_item.get("id","")!=node.data.cache_id and before==[g.rations,g.medicine])
	# A child on the cradle alone moves the real span, but never the latch.
	node=await prepare(g)
	g.player.position=Vector2(float(node.data.plate_x),node.hinge.y-2)
	g.boy.position=Vector2(14740,g.surface_y_at(14740,700)-2); g.boy.following=false
	await frames(g,120)
	add(checks,"real_weight_lowers_span_without_solving",node.lower_amount>.999 and absf(node.bridge_body.rotation)<.001 and not node.latched and node.plate_child=="Girl")
	for modal in ["pause","inventory"]:
		g.mode=modal; var amount=node.lower_amount; var angle=node.bridge_body.rotation
		await frames(g,35)
		add(checks,modal+"_freezes_counterweight",is_equal_approx(amount,node.lower_amount) and is_equal_approx(angle,node.bridge_body.rotation))
		g.mode="playing"
	Input.action_press("left"); await frames(g,65); release(); await frames(g,150)
	add(checks,"early_release_folds_span_without_softlock",node.lower_amount<.001 and not node.latched and g.health>99 and g.player.position.y<850)
	node.reset_from_progress()
	add(checks,"unsolved_reset_restores_raised_span",node.state=="folded" and node.lower_amount==0 and not node.latched)
	node=await prepare(g)
	if "--record-sluice" in OS.get_cmdline_user_args():
		movie_folder=g.report_path("sluice_motion_frames"); DirAccess.make_dir_recursive_absolute(movie_folder); recording=true
	evidence["continuous_success"]=await success(g,node)
	recording=false
	var route=evidence.continuous_success
	add(checks,"both_climb_authored_cradle_approach",route.approach.reached,JSON.stringify(route.approach))
	add(checks,"real_Q_wait_keeps_boy_on_pressure_cradle",route.get("q_wait_used",false) and route.get("boy_holds",false),JSON.stringify(route.get("wait_positions",{})))
	add(checks,"waiting_prompt_does_not_ask_for_second_Q",route.get("q_wait_used",false) and not "[Q]" in route.get("waiting_prompt","[Q]"),route.get("waiting_prompt",""))
	add(checks,"girl_crosses_real_lowered_support",route.get("crossing",{}).get("bridge_floor_ticks",0)>30,JSON.stringify(route.get("crossing",{})))
	add(checks,"different_children_hold_and_latch",route.get("latched",false) and route.get("holder_at_latch","")=="Boy" and route.get("far_child","")=="Girl")
	add(checks,"real_Q_call_brings_boy_across_actual_bridge",route.get("q_call_used",false) and route.get("reunited",false) and route.get("boy_bridge_ticks",0)>35,JSON.stringify(route))
	add(checks,"called_prompt_does_not_ask_for_second_Q",route.get("latched",false) and route.get("q_call_used",false) and not "[Q]" in route.get("called_prompt","[Q]"),route.get("called_prompt",""))
	add(checks,"finite_reward_enters_campaign_inventory",g.rations==1 and g.medicine==1 and g.flags.get(node.data.cache_id,false),str([g.rations,g.medicine]))
	add(checks,"collected_cache_objective_points_to_mill",g.flags.get(node.data.cache_id,false) and "packed" in node.objective_text() and not "Search" in node.objective_text(),node.objective_text())
	var resources=[g.rations,g.medicine]
	g.update_prompt(); await hold_action(g,"interact",90); release()
	add(checks,"reward_cannot_duplicate",resources==[g.rations,g.medicine])
	add(checks,"safe_solution_preserves_both_children",g.health>99 and g.mode=="playing")
	node.reset_from_progress()
	add(checks,"solved_reset_preserves_physical_latch",node.latched and node.lower_amount==1 and absf(node.bridge_body.rotation)<.001)
	g.load_chapter(1,false); g.mode="playing"; node=find_node(g,find_data(g)); await frames(g,4)
	add(checks,"chapter_reload_preserves_solved_bridge",node!=null and node.latched and node.lower_amount==1 and g.flags.get(node.data.cache_id,false))
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	return {"build":"0.4.2","all_passed":passed,"checks":checks,"evidence":evidence,"recorded_frames":recorded_frames,"method":"Bounded authored woods encounter. Refusal/release/reset fixtures use explicit initial placements. Success begins on ordinary signal-path ground, then uses held movement/jump and native parsed Q events, real child-floor contacts, rotating bridge support, far-bank ratchet and finite campaign cache; no actor repositioning or flag grants during success. Earlier hazards are disabled in this bounded fixture."}

static func capture(g):
	recording=false
	var node=await prepare(g)
	var route=await success(g,node,true) if node!=null else {}
	var report={"build":"0.4.2","actual_sequence":route,"all_states_reached":route.get("boy_holds",false) and route.get("latched",false) and route.get("reunited",false),"screenshots":["13_counterweight_wait.png","14_counterweight_crossing.png","15_counterweight_reunion.png"]}
	var file=FileAccess.open(g.report_path("sluice_capture.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("SLUICE_CAPTURE_RESULT ",JSON.stringify(report))
