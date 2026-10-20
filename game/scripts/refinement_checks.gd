extends RefCounted

static func frames(g,count):
	for frame in range(count): await g.get_tree().physics_frame

static func release():
	for action in ["interact","left","right","jump","sprint","crouch"]: Input.action_release(action)

static func item(g,id):
	for entry in g.level.interact:
		if entry.get("id","")==id: return entry
	return {}

static func prepare(g):
	release(); g.flags={}; g.cache_remaining={}; g.water_offsets={}
	g.load_chapter(1,false); g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.hazard_lanes=[]; g.level.searchlight=false
	g.mode="playing"; g.health=100; g.warmth=100; g.food=100; g.stamina=100
	g.scrap=1; g.rations=0; g.medicine=0; g.trail.clear()
	var pump=item(g,"woods_canal_drain")
	g.player.position=Vector2(pump.x-12,pump.y-2)
	g.boy.position=Vector2(pump.x-58,pump.y-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.player.reset_feet(); g.boy.reset_feet(); g.camera.zoom=Vector2(1.12,1.12)
	g.camera.position=Vector2(pump.x+180,480)
	await frames(g,12)
	return pump

static func start_work(g,pump):
	g.player.action_time=0; g.boy.action_time=0; g.update_prompt()
	if g.near_item.get("id","")!=pump.id: return false
	Input.action_press("interact"); g.interact()
	return not g.pending_action.is_empty()

static func run(g):
	g.test_log=[]
	var pump=await prepare(g)
	var art=g.world.interaction_art
	g.assert_check("authored_pump_is_reachable_at_its_visible_position",start_work(g,pump))
	await frames(g,48)
	var angle=art.pump_angle(g,pump)
	g.assert_check("held_work_moves_the_separate_pump_lever",absf(angle-art.PUMP_REST_ANGLE)>.05,str(angle))
	g.assert_check("pump_cannot_drain_before_work_finishes",not g.flags.get(pump.id,false) and g.in_water(12500,780))
	g.mode="pause"
	var progress=g.action_progress
	await frames(g,30)
	g.assert_check("pause_freezes_work_and_lever",is_equal_approx(progress,g.action_progress) and is_equal_approx(angle,art.pump_angle(g,pump)))
	g.mode="playing"; Input.action_release("interact")
	await frames(g,3)
	g.assert_check("releasing_work_keeps_salvage_and_water",g.pending_action.is_empty() and g.scrap==1 and not g.flags.get(pump.id,false))
	g.assert_check("released_shared_work_frees_both_children",g.player.action_time<=0 and g.boy.action_time<=0)
	g.player.action_time=0; g.update_prompt(); start_work(g,pump)
	await frames(g,20)
	g.player.position.y-=150
	await frames(g,1)
	g.assert_check("leaving_work_height_interrupts_mechanism",g.pending_action.is_empty() and g.scrap==1 and not g.flags.get(pump.id,false))
	pump=await prepare(g)
	g.assert_check("shared_work_can_restart_after_interruption",start_work(g,pump))
	await frames(g,ceili(float(pump.hold_seconds)*60)+4)
	g.assert_check("completed_pump_consumes_exactly_one_salvage",g.flags.get(pump.id,false) and g.scrap==0)
	var offset=float(g.water_offsets.get(pump.id,0))
	g.assert_check("sluice_moves_with_the_receding_water",offset>0 and offset<62,str(offset))
	g.mode="inventory"
	await frames(g,30)
	g.assert_check("inventory_freezes_the_drainage_transition",is_equal_approx(offset,float(g.water_offsets.get(pump.id,0))))
	g.mode="playing"; release()
	await frames(g,180)
	g.assert_check("water_finishes_receding_after_resume",is_equal_approx(62,float(g.water_offsets.get(pump.id,0))) and not g.in_water(12500,780))
	# Native inventory transfers use an authored mixed cache. These targeted
	# setup placements do not pretend to be navigation across the upper route.
	var cache=item(g,"woods_canal_ledger")
	g.rations=4; g.medicine=0; g.player.action_time=0
	g.complete_interaction(cache)
	var remaining=art.cache_contents(g,cache)
	g.assert_check("partial_search_removes_only_taken_resource_art",remaining==["rations"] and g.medicine==1 and not g.flags.get(cache.id,false),JSON.stringify(remaining))
	g.rations=0; g.player.action_time=0; g.complete_interaction(cache)
	g.assert_check("depleted_cache_has_no_remaining_contents",art.cache_contents(g,cache).is_empty() and g.flags.get(cache.id,false) and g.rations==2)
	g.mode="pause"
	var snapshot=JSON.stringify(g.cache_remaining)
	await frames(g,30)
	g.assert_check("rendering_does_not_grant_or_duplicate_supplies",snapshot==JSON.stringify(g.cache_remaining) and g.rations==2 and g.medicine==1)
	var passed=true
	for check in g.test_log:
		if not check.passed: passed=false
	var report={"build":"0.4.1","all_passed":passed,"checks":g.test_log,
		"method":"Targeted native fixtures at the authored canal pump and mixed upper cache. Real held Input, physics frames, pause/inventory states, water offsets, resource consumption and interruption. Earlier hazards are disabled only in this fixture; continuous campaign and branch suites remain separate."}
	var output=FileAccess.open(g.report_path("refinement_checks.json"),FileAccess.WRITE)
	output.store_string(JSON.stringify(report,"\t")); output.close()
	print("REFINEMENT_CHECKS_RESULT ",JSON.stringify(report))
	g.call_deferred("quit_game",0 if passed else 1)

static func shot(g,name,center,zoom):
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(zoom,zoom)
	g.camera.position=center
	await g.get_tree().process_frame
	g.camera.position=center
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func capture(g):
	var pump=await prepare(g)
	start_work(g,pump)
	await frames(g,95)
	await shot(g,"10_canal_pump_work",Vector2(pump.x+110,600),1.65)
	# Capture completion, not an arbitrary point in the receding-water blend.
	for frame in range(420):
		await frames(g,1)
		if float(g.water_offsets.get(pump.id,0))>=62: break
	release()
	if float(g.water_offsets.get(pump.id,0))<62:
		push_error("Canal capture did not reach fully drained state")
	await shot(g,"11_canal_sluice_drained",Vector2(pump.x+330,560),1.35)
	# Three existing search positions in the village are shown in their normal
	# geometry; this close study stages the camera, not the asset arrangement.
	g.load_chapter(0,false); g.mode="playing"; g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.hazard_lanes=[]
	var food_item={}
	for entry in g.level.interact:
		if entry.kind=="cache" and int(entry.get("rations",0))>0 and int(entry.get("scrap",0))>0:
			food_item=entry; break
	g.player.position=Vector2(food_item.x-46,food_item.y-2)
	g.boy.position=Vector2(food_item.x-90,food_item.y-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO
	g.player.reset_feet(); g.boy.reset_feet()
	await frames(g,12)
	await shot(g,"12_supplies_close_study",Vector2(food_item.x,food_item.y-115),2.1)
