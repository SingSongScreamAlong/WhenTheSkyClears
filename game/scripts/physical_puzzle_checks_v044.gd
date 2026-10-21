extends RefCounted

# Bounded native fixtures. Only prepare() positions the children on the road;
# every measured success thereafter uses the actual keyboard action paths.
const NativeInput=preload("res://scripts/sluice_checks.gd")
static var recording=false
static var recorded_frames=0
static var movie_folder=""
static var cues=[]

static func frames(g,count):
	for tick in range(count):
		await g.get_tree().physics_frame
		if recording:
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%recorded_frames),.88)
			recorded_frames+=1

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func command(g,action,count=2):
	var event=InputEventAction.new(); event.action=action; event.pressed=true; NativeInput.route_event(g,event)
	await frames(g,count)
	event=InputEventAction.new(); event.action=action; event.pressed=false; NativeInput.route_event(g,event)
	await frames(g,2)

static func point(p): return {"x":p.x,"y":p.y}
static func add(checks,name,passed,detail=""): checks.append({"check":name,"passed":passed,"details":detail})

static func find_node(g,id):
	for node in g.puzzle_encounters:
		if node.data.id==id: return node
	return null

static func prepare(g,chapter):
	release(); g.flags={}; g.cache_remaining={}; g.water_offsets={}
	for gate in g.levels[chapter].gates: g.flags[gate.key]=true
	for bridge in g.levels[chapter].get("bridges",[]): g.flags[bridge.key]=true
	g.load_chapter(chapter,false); g.level=g.level.duplicate(true)
	g.level.hazard_lanes=[]; g.level.erase("danger"); g.level.searchlight=false
	g.mode="playing"; g.chapter_card=0; g.message_time=0
	g.health=100; g.food=100; g.warmth=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.rations=0; g.scrap=0; g.medicine=0; g.trail.clear(); g.pending_action={}; g.action_progress=0
	var node=find_node(g,"orchard_counterweight" if chapter==0 else "freight_child_lift")
	if node==null: return null
	var start=7280.0 if chapter==0 else 13840.0
	g.player.position=Vector2(start,g.surface_y_at(start,700)-2)
	g.boy.position=Vector2(start-50,g.surface_y_at(start-50,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.player.reset_feet(); g.boy.reset_feet(); await frames(g,18)
	return node

static func navigate(g,node,x,y,require_boy=true,max_ticks=1100):
	var jump_hold=0; var reached=false; var ticks=0
	Input.action_release("interact"); Input.action_release("crouch")
	for tick in range(max_ticks):
		await frames(g,1); ticks=tick+1
		if g.mode!="playing": break
		Input.action_release("left"); Input.action_release("right")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var girl_ready=absf(g.player.position.x-x)<12 and absf(g.player.position.y-y)<20 and g.player.is_on_floor()
		var boy_ready=absf(g.boy.position.x-x)<88 and absf(g.boy.position.y-y)<25 and g.boy.is_on_floor()
		if girl_ready and (boy_ready or not require_boy): reached=true; break
		if not girl_ready:
			if g.player.position.x<x-8: Input.action_press("right")
			elif g.player.position.x>x+8: Input.action_press("left")
		if require_boy and g.player.position.x-g.boy.position.x>125 and absf(g.player.position.y-g.boy.position.y)<30: Input.action_release("right")
		if g.player.is_on_floor() and jump_hold==0 and not girl_ready:
			var obstacles=node.obstacle_rects().duplicate()
			if node.kind=="weighted_orchard" and node.solved: obstacles.remove_at(1)
			for platform in g.level.platforms: obstacles.append(Rect2(platform.x,platform.y,platform.w,platform.h))
			for obstacle in obstacles:
				var direction=1.0 if x>=g.player.position.x else -1.0
				var edge=obstacle.position.x if direction>0 else obstacle.end.x
				var ahead=(edge-g.player.position.x)*direction
				var rise=g.player.position.y-obstacle.position.y
				var overhead=g.player.position.x>=obstacle.position.x-4 and g.player.position.x<=obstacle.end.x+4 and y<=obstacle.position.y+5
				if rise>12 and rise<140 and ((ahead>0 and ahead<59) or overhead):
					Input.action_press("jump"); jump_hold=24; break
	release()
	return {"reached":reached,"physics_samples":ticks,"girl":point(g.player.position),"boy":point(g.boy.position)}

static func shot(g,name,center):
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(1.52,1.52)
	g.camera.position=center; await g.get_tree().process_frame; g.camera.position=center
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func orchard_success(g,node,capture_images=false):
	var result={}; var start=node.crate.position.x
	Input.action_press("interact"); Input.action_press("right")
	for tick in range(700):
		await frames(g,1)
		if node.solved or g.mode!="playing": break
	release()
	result["latched"]=node.solved; result["actual_crate_travel"]=node.crate.position.x-start
	result["push_ticks"]=node.push_ticks; result["plate_contact"]=node.crate_on_plate(); result["ramp_angle"]=node.ramp_body.rotation
	result["crate"]=point(node.crate.position); result["crate_velocity"]=point(node.crate.linear_velocity)
	result["native_contacts"]=[]
	for body in node.crate.get_colliding_bodies(): result.native_contacts.append(str(body.name))
	if capture_images: await shot(g,"20_orchard_weighted_mechanism",Vector2(7530,570))
	if not node.solved: return result
	result["ascent"]=await navigate(g,node,7770,580,true,1200)
	await frames(g,45)
	result["girl_ramp_ticks"]=node.ramp_ticks.get("Girl",0); result["boy_ramp_ticks"]=node.ramp_ticks.get("Boy",0)
	if capture_images: await shot(g,"21_orchard_open_route",Vector2(7600,525))
	g.update_prompt(); await command(g,"interact",100)
	result["reward_taken"]=g.flags.get(node.data.cache_id,false) and g.rations==1 and g.scrap==1
	result["girl"]=point(g.player.position); result["boy"]=point(g.boy.position); result["health"]=g.health
	return result

static func freight_success(g,node,capture_images=false):
	var result={"boarding":await navigate(g,node,14020,696,true,1000)}
	if not result.boarding.reached: return result
	g.update_prompt()
	var signal_offered=str(g.near_item.get("id",""))=="camp_yard_signal"
	await command(g,"interact",8)
	result["signal_not_offered_from_deck"]=not signal_offered and str(g.pending_action.get("id",""))!="camp_yard_signal" and not g.flags.get("camp_yard_signal",false) and node.foot_contact(g.player,node.lift_body)
	await command(g,"companion")
	result["q_wait_used"]=not g.boy.following
	result["waiting_contact"]=node.foot_contact(g.boy,node.lift_body)
	result["return_to_winch"]=await navigate(g,node,float(node.data.winch_x),float(node.data.floor_y),false,800)
	if capture_images: await shot(g,"22_freight_lift_wait",Vector2(13900,590))
	if not result.return_to_winch.reached: return result
	Input.action_press("interact")
	for tick in range(650):
		await frames(g,1)
		if node.solved or g.mode!="playing": break
	release(); result["latched"]=node.solved; result["actual_lift_travel"]=node.actual_travel
	result["winch_ticks"]=node.winch_ticks; result["rider_ticks"]=node.rider_ticks
	result["boy_catches_upper_floor"]=node.foot_contact(g.boy,node.lift_body) and absf(g.boy.position.y-float(node.data.upper_y))<5
	if not node.solved: return result
	var legs=[]; var all_reached=true
	for target in [Vector2(14150,696),Vector2(14320,636),Vector2(14480,576),Vector2(14460,526)]:
		var leg=await navigate(g,node,target.x,target.y,false,1000); legs.append(leg)
		if not leg.reached: all_reached=false; break
	result["girl_climbs_loading_steps"]={"reached":all_reached,"legs":legs}
	await command(g,"companion"); result["q_call_used"]=g.boy.following
	result["reunion"]=await navigate(g,node,14460,526,true,1200); await frames(g,45)
	if capture_images: await shot(g,"23_freight_lift_reunion",Vector2(14190,465))
	g.update_prompt(); await command(g,"interact",110)
	result["reward_taken"]=g.flags.get(node.data.cache_id,false) and g.rations==1 and g.medicine==1
	result["girl"]=point(g.player.position); result["boy"]=point(g.boy.position); result["health"]=g.health
	return result

static func run(g):
	recording=false; recorded_frames=0; movie_folder=""; cues=[]
	var checks=[]; var evidence={}; var node=await prepare(g,0)
	if node==null: return {"all_passed":false,"checks":[{"check":"authored_machines_instantiate","passed":false}]}
	add(checks,"orchard_crate_and_ramp_have_native_bodies",node.crate is RigidBody2D and node.ramp_body is AnimatableBody2D)
	var origin=node.crate.position
	Input.action_press("right"); await frames(g,42); release(); await frames(g,8)
	add(checks,"walking_without_E_cannot_drive_weight",absf(node.crate.position.x-origin.x)<3,str(node.crate.position.x-origin.x))
	for modal in ["pause","inventory"]:
		g.mode=modal; await frames(g,2); var before=node.crate.position; await frames(g,35)
		add(checks,"orchard_"+modal+"_freezes_weight",node.crate.freeze and node.crate.position.distance_to(before)<.01)
		g.mode="playing"; await frames(g,3)
	node.reset_from_progress(); await frames(g,8)
	add(checks,"orchard_unsolved_reset_restores_native_transform",node.crate.position.distance_to(origin)<2 and absf(node.ramp_body.rotation-.4)<.001)
	# Isolated far-bank refusal uses the real cache prerequisites, before success.
	g.player.position=Vector2(7770,578); g.boy.position=Vector2(7728,578); g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO
	await frames(g,15); g.update_prompt(); await command(g,"interact",100)
	add(checks,"unsolved_orchard_supplies_refuse_far_approach",g.rations==0 and g.scrap==0 and not g.flags.get(node.data.cache_id,false))
	# A child's standing contact is deliberately insufficient for this heavy
	# iron tread: the native crate is the distinct weighted tool.
	g.player.position=Vector2(node.data.plate_x,node.data.floor_y-2); g.boy.position=Vector2(node.data.plate_x-60,node.data.floor_y-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO
	await frames(g,60)
	add(checks,"standing_child_cannot_substitute_for_heavy_weight",not node.solved and node.amount==0)
	node=await prepare(g,0)
	if "--record-physical-v044" in OS.get_cmdline_user_args():
		movie_folder=g.report_path("physical_v044_motion_frames"); DirAccess.make_dir_recursive_absolute(movie_folder); recording=true
		cues.append({"frame":recorded_frames,"cue":"Held E moves an actual weighted crate onto the iron chock, paying out a hinged timber ramp."})
	evidence["orchard_success"]=await orchard_success(g,node)
	recording=false; var route=evidence.orchard_success
	add(checks,"real_crate_contact_latches_hinged_ramp",route.get("latched",false) and route.get("actual_crate_travel",0)>115 and route.get("push_ticks",0)>45 and route.get("plate_contact",false),JSON.stringify(route))
	add(checks,"both_children_physically_ascend_hinged_ramp",route.get("ascent",{}).get("reached",false) and route.get("girl_ramp_ticks",0)>8 and route.get("boy_ramp_ticks",0)>8,JSON.stringify(route))
	add(checks,"native_search_earns_finite_orchard_supplies",route.get("reward_taken",false),JSON.stringify(route))
	if node.solved:
		g.update_prompt(); await command(g,"interact",100)
		add(checks,"orchard_spent_cache_cannot_duplicate",g.rations==1 and g.scrap==1)
		node.reset_from_progress(); await frames(g,3)
		add(checks,"orchard_latched_reset_keeps_ramp_and_weight",node.solved and node.crate.freeze and absf(node.crate.position.x-float(node.data.plate_x))<.1 and absf(node.ramp_body.rotation+atan2(120.0,160.0))<.001)
	node=await prepare(g,2)
	if node==null: return {"all_passed":false,"checks":checks}
	g.player.position=Vector2(node.data.winch_x,node.data.floor_y-2); g.boy.position=Vector2(node.data.winch_x-70,node.data.floor_y-2)
	await frames(g,12); Input.action_press("interact"); await frames(g,90); release()
	add(checks,"empty_cargo_lift_refuses_to_raise",node.actual_travel<.01 and not node.solved)
	# Same-x overhead refusal isolates the vertical rule after the old signal
	# was moved clear of the lift. Both bodies then fall onto the actual slope
	# and operate it normally; the solved lift is never a prerequisite.
	var signal_item={}
	for item in g.level.interact:
		if item.get("id","")=="camp_yard_signal": signal_item=item
	g.player.position=Vector2(signal_item.x,float(signal_item.y)-60)
	g.boy.position=Vector2(float(signal_item.x)-42,g.surface_y_at(float(signal_item.x)-42,float(signal_item.y))-60)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.update_prompt(); var overhead_offered=str(g.near_item.get("id",""))=="camp_yard_signal"
	g.near_item=signal_item # Also reject an otherwise stale prior ground prompt.
	await command(g,"interact",8)
	add(checks,"same_x_overhead_signal_refuses_native_E",not overhead_offered and str(g.pending_action.get("id",""))!="camp_yard_signal" and not g.flags.get("camp_yard_signal",false))
	await frames(g,30); g.update_prompt()
	var native_road_floor=false
	for index in range(g.player.get_slide_collision_count()):
		var collision=g.player.get_slide_collision(index)
		if collision.get_normal().y<-.65 and collision.get_collider().get_parent()==g.solids: native_road_floor=true
	var ground_offered=str(g.near_item.get("id",""))=="camp_yard_signal" and g.player.is_on_floor() and native_road_floor
	await command(g,"interact",230)
	add(checks,"ordinary_sloped_ground_signal_works_before_lift",ground_offered and g.flags.get("camp_yard_signal",false) and not node.solved and node.actual_travel==0,str([point(g.player.position),point(g.boy.position),signal_item.y]))
	node=await prepare(g,2)
	g.player.position=Vector2(node.data.winch_x,node.data.floor_y-2); g.boy.position=Vector2(node.data.winch_x-70,node.data.floor_y-2)
	await frames(g,12)
	# Isolated occupied fixture measures real interruption and recovery; the
	# continuous success below boards and commands Boy using normal input.
	g.boy.position=Vector2(float(node.data.lift_x)+70,float(node.data.low_y)-2); g.boy.velocity=Vector2.ZERO; g.boy.following=false
	await frames(g,18); Input.action_press("interact"); await frames(g,70); release()
	await frames(g,2); var partial=node.actual_travel; await frames(g,60)
	add(checks,"released_winch_holds_actual_partial_load",partial>35 and partial<100 and absf(node.actual_travel-partial)<.01,str([partial,node.actual_travel]))
	for modal in ["pause","inventory"]:
		g.mode=modal; await frames(g,2); var deck_y=node.lift_body.position.y
		await frames(g,40)
		add(checks,"freight_"+modal+"_freezes_physical_deck",absf(node.lift_body.position.y-deck_y)<.01)
		g.mode="playing"; await frames(g,3)
	Input.action_press("crouch"); Input.action_press("interact"); await frames(g,130); release()
	add(checks,"crouch_E_physically_recovers_unlatched_load",node.actual_travel<.01 and not node.solved and node.foot_contact(g.boy,node.lift_body),str([node.actual_travel,point(g.boy.position)]))
	g.checkpoint_x=13850; g.respawn(false); await frames(g,14)
	add(checks,"unsolved_respawn_restores_low_deck_without_softlock",not node.solved and node.actual_travel<.01 and absf(node.lift_body.position.y-float(node.data.low_y))<.01)
	# One initial obstruction setup; from here Q is the only way the fixture
	# moves Boy out from under the real descending platform.
	node=await prepare(g,2)
	node.lift_body.sync_to_physics=false; node.lift_body.position.y=620
	PhysicsServer2D.body_set_state(node.lift_body.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM,node.lift_body.global_transform)
	node.lift_body.sync_to_physics=true
	g.player.position=Vector2(node.data.winch_x,node.data.floor_y-2); g.player.velocity=Vector2.ZERO
	g.boy.position=Vector2(float(node.data.lift_x)+80,node.data.floor_y-2); g.boy.velocity=Vector2.ZERO; g.boy.following=false
	await frames(g,15); Input.action_press("crouch"); Input.action_press("interact"); await frames(g,150)
	var blocked=node.lowering_blocked; var held_y=node.lift_body.position.y
	var clearance=node.child_bounds(g.boy).position.y-(held_y+18)
	await frames(g,40)
	add(checks,"descending_platform_arrests_above_real_child_collider",blocked and node.lowering_blocked and absf(node.lift_body.position.y-held_y)<.01 and clearance>=0 and clearance<2 and g.health>99,str([held_y,clearance,point(g.boy.position)]))
	await command(g,"companion"); await frames(g,180); release()
	add(checks,"native_Q_clearance_resumes_safe_lowering",g.boy.following and g.boy.position.x<float(node.data.lift_x)-12 and node.actual_travel<.01 and not node.solved and g.health>99,str([node.actual_travel,point(g.player.position),point(g.boy.position)]))
	node=await prepare(g,2)
	if not movie_folder.is_empty():
		recording=true; cues.append({"frame":recorded_frames,"cue":"Escort Boy onto the native cargo platform; Q wait; Girl returns to the lower winch, raises his actual standing weight to the latch, climbs and calls him across."})
	evidence["freight_success"]=await freight_success(g,node)
	recording=false; route=evidence.freight_success
	add(checks,"boy_boards_real_platform_then_native_Q_waits",route.get("boarding",{}).get("reached",false) and route.get("q_wait_used",false) and route.get("waiting_contact",false),JSON.stringify(route))
	add(checks,"cargo_deck_cannot_offer_or_start_lower_road_signal",route.get("signal_not_offered_from_deck",false))
	add(checks,"actual_winch_and_rider_contact_catch_upper_latch",route.get("latched",false) and route.get("actual_lift_travel",0)>169 and route.get("winch_ticks",0)>200 and route.get("rider_ticks",0)>200 and route.get("boy_catches_upper_floor",false),JSON.stringify(route))
	add(checks,"girl_uses_loading_steps_and_Q_reunites_both",route.get("girl_climbs_loading_steps",{}).get("reached",false) and route.get("q_call_used",false) and route.get("reunion",{}).get("reached",false),JSON.stringify(route))
	add(checks,"native_shared_search_earns_freight_medicine",route.get("reward_taken",false),JSON.stringify(route))
	if node.solved:
		g.update_prompt(); await command(g,"interact",110)
		add(checks,"freight_spent_cache_cannot_duplicate",g.medicine==1 and g.rations==1)
		node.reset_from_progress(); await frames(g,4)
		add(checks,"freight_latched_reset_retains_physical_upper_deck",node.solved and absf(node.lift_body.position.y-float(node.data.upper_y))<.01)
		var original_save=g.save_path; var original_settings=g.settings_path; var prior_smoke=g.smoke_test
		g.save_path="user://qa_physical_v044_"+str(Time.get_ticks_usec())+".json"; g.settings_path=g.save_path+".settings"
		g.smoke_test=false; g.journey_active=true; g.checkpoint_x=13850; g.write_save()
		g.flags={}; g.load_save(true); g.mode="playing"; node=find_node(g,"freight_child_lift"); await frames(g,5)
		add(checks,"save_resume_restores_solved_lift_and_spent_supplies",node!=null and node.solved and node.actual_travel>169 and g.flags.get(node.data.cache_id,false) and g.medicine==1 and g.rations==1,str([node!=null,node.solved,node.actual_travel,g.flags.get(node.data.cache_id,false),g.medicine,g.rations,g.chapter]))
		DirAccess.remove_absolute(g.save_path); DirAccess.remove_absolute(g.settings_path)
		g.save_path=original_save; g.settings_path=original_settings; g.smoke_test=prior_smoke
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	return {"build":"0.4.4","all_passed":passed,"checks":checks,"evidence":evidence,"recorded_frames":recorded_frames,"recording":{"enabled":not movie_folder.is_empty(),"frames":recorded_frames,"fps":30,"frame_directory":movie_folder,"cues":cues,"scope":"Two uninterrupted native Input sequences after explicit safe-road setups; unrelated campaign hazards disabled only at initial setup. All crate push, rider lift, Q wait/call, climbs and finite searches are real physics."},"method":"Native rigid and animatable bodies with actual floor contacts; component evidence counts physics ticks, independent of render FPS. Refusal, modal pause and resets use separate isolated fixtures."}

static func capture(g):
	recording=false
	var node=await prepare(g,0); var orchard=await orchard_success(g,node,true) if node!=null else {}
	node=await prepare(g,2); var freight=await freight_success(g,node,true) if node!=null else {}
	var report={"build":"0.4.4","all_states_reached":orchard.get("latched",false) and orchard.get("ascent",{}).get("reached",false) and orchard.get("reward_taken",false) and freight.get("latched",false) and freight.get("reunion",{}).get("reached",false) and freight.get("reward_taken",false),"screenshots":["20_orchard_weighted_mechanism.png","21_orchard_open_route.png","22_freight_lift_wait.png","23_freight_lift_reunion.png"],"actual_sequences":{"orchard":orchard,"freight":freight}}
	var file=FileAccess.open(g.report_path("physical_v044_capture.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("PHYSICAL_V044_CAPTURE_RESULT ",JSON.stringify(report))
