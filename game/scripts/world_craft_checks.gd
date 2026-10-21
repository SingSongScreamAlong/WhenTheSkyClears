extends RefCounted

static func frames(g,count):
	for frame in range(count): await g.get_tree().physics_frame

static func add(checks,label,passed,detail=""):
	checks.append({"check":label,"passed":passed,"details":detail})

static func run(g):
	var checks=[]
	for action in ["left","right","jump","crouch","interact"]: Input.action_release(action)
	g.flags={}; g.load_chapter(1,false); g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.hazard_lanes=[]; g.mode="playing"
	g.health=100; g.warmth=100; g.food=100; g.stamina=100
	g.player.position=Vector2(2480,698); g.player.velocity=Vector2.ZERO
	g.boy.position=Vector2(2000,698); g.boy.velocity=Vector2.ZERO; g.boy.following=false
	g.player.reset_feet(); g.boy.reset_feet()
	await frames(g,12)
	var entry=g.gate_bodies[0]; var gate=entry.data
	add(checks,"logging_gate_starts_physically_closed",g.gate_lift(gate)<.1 and entry.body.collision_layer==1)
	Input.action_press("right"); await frames(g,70); Input.action_release("right")
	add(checks,"closed_timber_blocks_native_movement",g.player.position.x<float(gate.x)-20,str(g.player.position))
	g.boy.position=Vector2(float(gate.plate),698); g.boy.velocity=Vector2.ZERO; g.boy.reset_feet()
	await frames(g,20)
	add(checks,"weight_pays_out_gate_gradually",g.gate_lift(gate)>15 and g.gate_lift(gate)<90,str(g.gate_lift(gate)))
	add(checks,"collision_and_painted_edge_share_displacement",is_equal_approx(entry.body.position.y,-g.gate_lift(gate)))
	for modal in ["pause","inventory"]:
		g.mode=modal; var previous=g.gate_lift(gate)
		await frames(g,24)
		add(checks,modal+"_holds_logging_gate",is_equal_approx(previous,g.gate_lift(gate)))
		g.mode="playing"
	await frames(g,110)
	add(checks,"held_plate_clears_both_child_heights",g.gate_lift(gate)>float(gate.h),str(g.gate_lift(gate)))
	Input.action_press("right"); await frames(g,52); Input.action_release("right")
	add(checks,"raised_timber_allows_native_crossing",g.player.position.x>float(gate.x)+55,str(g.player.position))
	# Explicit safety fixture: release the weight while a child is directly
	# under the fully raised timber. The normal campaign route is tested apart.
	g.player.position=Vector2(float(gate.x),698); g.player.velocity=Vector2.ZERO
	g.boy.position=Vector2(2000,698); g.boy.velocity=Vector2.ZERO; g.boy.following=false
	await frames(g,180)
	var head=g.player.position.y-g.player.col.shape.size.y
	add(checks,"release_arrests_above_child_head",float(gate.y)-g.gate_lift(gate)<head-5,str([head,float(gate.y)-g.gate_lift(gate)]))
	add(checks,"arrested_gate_keeps_child_alive_and_free",g.health>99 and absf(g.player.position.y-700)<5)
	Input.action_press("right"); await frames(g,65); Input.action_release("right"); await frames(g,180)
	add(checks,"gate_returns_after_child_clears_it",g.gate_lift(gate)<.1 and g.player.position.x>float(gate.x)+80)
	g.flags[gate.key]=true; await frames(g,125)
	add(checks,"far_latch_permanently_releases_weight_requirement",g.gate_lift(gate)>float(gate.h) and absf(g.boy.position.x-float(gate.plate))>150)
	add(checks,"new_grass_response_uses_physical_contact",absf(g.world.foliage_displacement(g.player.position.x+12,g.player.position.y))>0 and g.world.foliage_displacement(g.player.position.x,g.player.position.y+100)==0)
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	return {"build":"0.4.2","all_passed":passed,"checks":checks,"method":"Native held-input crossing of the authored logging gate. Explicit initial placements isolate weight, modal pause and anti-crush safety. Real collision displacement is compared to rendered displacement; full-journey navigation is separate."}

static func capture(g):
	g.flags={"forest_bridge":true}; g.load_chapter(1,false); g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.hazard_lanes=[]; g.mode="playing"
	g.player.position=Vector2(2508,698); g.player.velocity=Vector2.ZERO
	g.boy.position=Vector2(2230,698); g.boy.velocity=Vector2.ZERO; g.boy.following=false
	g.player.reset_feet(); g.boy.reset_feet(); g.chapter_card=0; g.message_time=0
	g.health=100; g.warmth=90; g.food=90
	await frames(g,64)
	g.camera.zoom=Vector2(1.48,1.48); var center=Vector2(2400,515)
	g.camera.position=center; await g.get_tree().process_frame; g.camera.position=center
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path("16_logging_counterweight.png"))
