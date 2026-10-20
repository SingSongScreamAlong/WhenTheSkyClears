extends RefCounted
static func frames(g,n):
	for i in range(n):await g.get_tree().physics_frame
static func release():
	for action in ["left","right","jump","sprint","crouch","interact"]:Input.action_release(action)
static func run(g):
	g.smoke_test=true;var cases=[]
	for sprint in [false,true]:
		g.last_house.start(false);g.player.position=Vector2(1100,699);g.boy.position=Vector2(1048,699);await frames(g,20)
		var minimum=1000.0;var maximum=0.0;var largest_step=0.0
		for turn in range(8):
			release();Input.action_press("right" if turn%2==0 else "left")
			if sprint:Input.action_press("sprint")
			for frame in range(32):
				var previous=g.boy.position;await frames(g,1)
				minimum=minf(minimum,absf(g.player.position.x-g.boy.position.x));maximum=maxf(maximum,absf(g.player.position.x-g.boy.position.x));largest_step=maxf(largest_step,g.boy.position.distance_to(previous))
		cases.append({"sprint":sprint,"minimum_gap":minimum,"maximum_gap":maximum,"largest_native_step":largest_step})
		g.assert_check("sprint_reversals_keep_separate_bodies" if sprint else "walk_reversals_keep_separate_bodies",minimum>34,str(cases[-1]))
		g.assert_check("sprint_yield_uses_native_motion" if sprint else "walk_yield_uses_native_motion",largest_step<4.9 and maximum<150,str(cases[-1]))
	release();g.last_house.start(false);g.player.position=Vector2(1100,699);g.boy.position=Vector2(1048,699);await frames(g,10)
	Input.action_press("left");await frames(g,12)
	g.assert_check("player_reversal_is_not_delayed_by_yield",g.player.velocity.x< -150 and g.companion_yield_dir<0)
	release();g.player.position=Vector2(130,699);g.boy.position=Vector2(65,699);await frames(g,12)
	g.assert_check("yield_refuses_left_boundary",not g.safe_yield_space(-1))
	g.player.position=Vector2(5900,699);g.boy.position=Vector2(5840,699);await frames(g,12)
	g.assert_check("yield_refuses_missing_ground",not g.safe_yield_space(-1))
	g.player.position=Vector2(5362,699);g.boy.position=Vector2(5300,699);Input.action_press("crouch");await frames(g,130)
	g.assert_check("cover_stop_keeps_both_children_safe",g.is_covered(g.player) and g.is_covered(g.boy) and g.companion_yield_dir==0)
	release();g.last_house.start(false);g.player.position=Vector2(8560,699);g.boy.position=Vector2(8506,699);g.flags["bag_down"]=true;await frames(g,12)
	var share=g.level.interact.filter(func(p):return p.kind=="share")[0];var quiet=g.level.interact.filter(func(p):return p.kind=="quiet")[0]
	g.last_house.try_interact(share);g.last_house.try_interact(quiet)
	g.assert_check("relief_waits_for_meal_performance",not g.flags.get("last_house_complete",false))
	await frames(g,80);g.last_house.try_interact(quiet)
	g.assert_check("relief_has_no_extra_five_second_gate",g.flags.get("last_house_complete",false) and g.last_house.relief_clock<2)
	g.assert_check("relief_has_contextual_attention",g.last_house.pose_for(g.player).get("mode")=="quiet" and g.last_house.pose_for(g.player).facing<0 and g.last_house.pose_for(g.boy).facing>0)
	g.assert_check("equal_collision_heights_preserved",g.player.col.shape.size.y==g.boy.col.shape.size.y and g.player.scale==Vector2.ONE and g.boy.scale==Vector2.ONE)
	release();g.last_house.start(false);g.player.position=Vector2(1280,699);g.boy.position=Vector2(1226,699);await frames(g,20)
	Input.action_press("left");Input.action_press("jump");var airborne_yield=false
	for i in range(38):
		await frames(g,1)
		if not g.player.is_on_floor() and g.boy.is_on_floor() and g.companion_yield_dir<0:airborne_yield=true
	g.assert_check("grounded_companion_yields_during_safe_air_crossing",airborne_yield)
	release();g.last_house.start(false);g.player.position=Vector2(1220,699);g.boy.position=Vector2(1270,699);g.boy.following=false;await frames(g,25)
	var waiting_x=g.boy.position.x;Input.action_press("right");await frames(g,65)
	g.assert_check("wait_command_preserves_companion_position_during_crossing",absf(g.boy.position.x-waiting_x)<.05 and not g.boy.following)
	release();var passed=g.test_log.all(func(c):return c.passed)
	var f=FileAccess.open(g.report_path("quality_checks.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"build":"0.5.4","all_passed":passed,"checks":g.test_log,"reversal_cases":cases,"scope":"Targeted native safety/response regression. Does not grade animation/composition quality. Deliberate starts are separate from route traversal; no physical controller or human pacing test."},"\t"));f.close();g.quit_game(0 if passed else 1)
