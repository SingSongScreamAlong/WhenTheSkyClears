extends RefCounted

static func release_inputs():
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)

static func run(g):
	g.test_log=[]
	var original=g.levels[0]
	var fixture=original.duplicate(true)
	fixture.width=8000; fixture.ground=[{"x":0,"y":700,"w":8000,"h":600,"kind":"earth"}]
	fixture.platforms=[]; fixture.gates=[]; fixture.covers=[]; fixture.interact=[]; fixture.pushables=[]; fixture.checkpoints=[]; fixture.memories=[]; fixture.tutorials=[]; fixture.safe_zones=[]; fixture.water_zones=[]; fixture.zones=[]; fixture.searchlight=false; fixture.erase("danger")
	fixture.hazard_lanes=[{"x":300,"w":1800,"kind":"listener","period":60,"active":45,"offset":2,"feet_min_y":650}]
	g.levels[0]=fixture; g.load_chapter(0,false); g.mode="playing"
	g.player.position=Vector2(500,699); g.boy.position=Vector2(100,699); g.boy.following=false
	for frame in range(12): await g.get_tree().physics_frame
	g.player.velocity.x=166
	g.assert_check("dry_walking_is_quiet",g.movement_noise(g.player)<.55)
	g.player.velocity.x=265
	g.assert_check("sprinting_carries_to_listener",g.movement_noise(g.player)>.55)
	g.player.crouching=true
	g.assert_check("crouching_remains_quiet",g.movement_noise(g.player)<.55)
	g.player.crouching=false; g.level.water_zones=[{"x":300,"w":1800,"top":686,"key":"qa_drain"}]
	g.player.velocity.x=166
	g.assert_check("walking_in_water_splashes",g.movement_noise(g.player)>.55)
	g.player.crouching=true
	g.assert_check("low_wading_is_quiet",g.movement_noise(g.player)<.55)
	g.player.crouching=false; g.player.position.y=540
	g.assert_check("raised_route_outside_lower_listener",not g.child_in_lane(g.player,fixture.hazard_lanes[0]))
	g.player.position.y=699; g.level.water_zones=[]; g.player.velocity=Vector2.ZERO; g.player.land_time=0
	g.health=100; g.invulnerable=0; g.hazard_exposure.clear(); g.playtime=0
	Input.action_press("right")
	for frame in range(100): await g.get_tree().physics_frame
	g.assert_check("native_dry_walk_passes_listener_without_damage",g.health>99.9 and g.player.position.x>720)
	release_inputs()
	g.player.position=Vector2(500,699); g.player.velocity=Vector2.ZERO; g.health=100; g.invulnerable=0; g.hazard_exposure.clear(); g.playtime=0
	Input.action_press("right"); Input.action_press("sprint")
	for frame in range(115): await g.get_tree().physics_frame
	g.assert_check("native_running_alerts_listener",g.health<100 and g.player.position.x>800,str(g.health))
	release_inputs()
	# Deliberately isolate the boy's sound from the girl's; actual lane detection
	# must inspect each child, even when the controlled child has left the area.
	g.player.position=Vector2(2400,699); g.player.velocity=Vector2.ZERO; g.boy.position=Vector2(700,699); g.boy.crouching=false; g.boy.velocity.x=260
	g.health=100; g.invulnerable=0; g.hazard_exposure.clear()
	g.tick_hazard_lanes(1.3)
	g.assert_check("listener_hears_boy_after_girl_leaves",g.health<100,str(g.health))
	var task={"kind":"pump","id":"qa_paid_drain","x":700,"y":700,"hold_seconds":1.0,"scrap_cost":1,"companion_required":true,"label":"Repair the sluice"}
	g.player.position=Vector2(700,699); g.boy.position=Vector2(650,699); g.boy.following=true; g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.player.action_time=0; g.boy.action_time=0; g.pending_action={}; g.scrap=0; g.near_item=task
	g.level.hazard_lanes=[]; g.interact()
	g.assert_check("drain_refuses_missing_real_salvage",g.pending_action.is_empty() and not g.flags.get(task.id,false))
	g.scrap=1; g.boy.position.x=450; g.player.action_time=0; g.near_item=task; g.interact()
	g.assert_check("drain_requires_both_children",g.pending_action.is_empty() and g.scrap==1)
	g.boy.position.x=650; g.player.action_time=0; g.near_item=task
	await g.test_action(task)
	g.assert_check("held_drain_consumes_one_salvage",g.flags.get(task.id,false) and g.scrap==0)
	g.level.water_zones=[{"x":500,"w":700,"top":686,"key":task.id}]
	g.assert_check("repaired_sluice_makes_lower_route_dry",not g.in_water(700,699))
	g.levels[0]=original
	var branches=await check_forks(g)
	var passed=true
	for check in g.test_log:
		if not check.passed: passed=false
	var report={"build":"0.4.0","all_passed":passed,"scope":"upper routes only" if "--development-upper-only" in g.qa_args else "all six fork choices and baseline mechanics","checks":g.test_log,"branches":branches,"method":"Targeted native runtime fixtures for noise, either-child detection, paid shared drainage, and authored route forks. Each physical fork scenario places both children once outside the entrance, unlocks only earlier gates and sets initial inventory explicitly. Native Input and existing companion AI drive all later navigation; held pump/brace/search actions use actual prompts. Climb setup disables timed hazards, then the raised bypass is tested with its real listener deliberately kept active. Lower fixtures retain that active height-gated listener. No mid-route repositioning, damage immunity, collision edits or resource grants. These fixtures complement continuous campaign navigation."}
	var file=FileAccess.open(g.report_path("development_checks.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("DEVELOPMENT_CHECKS_RESULT ",JSON.stringify(report)); g.call_deferred("quit_game",0 if passed else 1)

static func check_forks(g):
	var records=[]
	for index in range(g.levels.size()):
		for branch in g.levels[index].get("branch_routes",[]):
			g.assert_check(str(branch.id)+"_authored_entry_and_exit",float(branch.exit_x)>float(branch.entry_x)+300)
			var choices=["upper"] if "--development-upper-only" in g.qa_args else ["quiet_lower","paid_lower","upper"]
			for choice in choices:
				var record=await physical_fork(g,index,branch,choice)
				records.append(record)
	return records

static func task_by_id(g,id):
	for task in g.level.interact:
		if task.get("id","")==id: return task
	return {}

static func active_listener(g,branch):
	var listeners=[]
	for h in g.levels[g.chapter].get("hazard_lanes",[]):
		if h.kind=="listener" and h.x>=branch.entry_x and h.x<branch.exit_x:
			var lane=h.duplicate(true); lane.period=3600.0; lane.active=3599.0; lane.offset=0.0; listeners.append(lane)
	return listeners

static func fixture_branch(g,index,branch,choice):
	release_inputs(); g.flags={}; g.cache_remaining={}
	for gate in g.levels[index].gates:
		if float(gate.x)<float(branch.entry_x): g.flags[gate.key]=true
	for bridge in g.levels[index].get("bridges",[]):
		if float(bridge.x)<float(branch.entry_x): g.flags[bridge.key]=true
	g.load_chapter(index,false); g.level=g.level.duplicate(true)
	g.level.erase("danger"); g.level.searchlight=false
	g.level.hazard_lanes=[] if choice=="upper" else active_listener(g,branch)
	g.mode="playing"; g.health=100; g.food=100; g.warmth=100; g.stamina=100; g.wetness=0; g.invulnerable=0; g.playtime=1
	g.rations=0; g.medicine=0; g.scrap=0 if choice=="quiet_lower" else int(branch.cost)
	g.pending_action={}; g.action_progress=0; g.trail.clear()
	var start=float(branch.entry_x)-100.0
	if choice=="paid_lower": start=minf(start,float(task_by_id(g,branch.pump_id).x)-40)
	g.player.position=Vector2(start,g.surface_y_at(start,700)-2); g.boy.position=Vector2(start-52,g.surface_y_at(start-52,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.player.reset_feet(); g.boy.reset_feet(); g.boy.following=true
	for frame in range(12): await g.get_tree().physics_frame
	return {"girl":{"x":g.player.position.x,"y":g.player.position.y},"boy":{"x":g.boy.position.x,"y":g.boy.position.y}}

static func held_prompt(g,task):
	release_inputs()
	# Prompt eligibility is checked in the real world; supplying near_item from
	# the fixture would hide an inaccessible interaction or wrong route height.
	g.update_prompt()
	if g.near_item.is_empty() or g.near_item.get("id","")!=task.get("id",""): return false
	Input.action_press("interact"); g.interact()
	for frame in range(ceili(float(task.get("hold_seconds",1.2))*60)+12):
		await g.get_tree().physics_frame
		if g.mode!="playing": break
	Input.action_release("interact")
	return bool(g.flags.get(task.get("id",""),false))

static func navigate(g,target_x,target_y,climb,crouch,max_frames):
	var jump_hold=0; var jumps=0; var max_gap=0.0; var min_girl=INF; var min_boy=INF
	var landed=false; var companion=false; var complete=false; var frames=0
	for frame in range(max_frames):
		await g.get_tree().physics_frame; frames=frame+1
		if g.mode!="playing": break
		min_girl=minf(min_girl,g.player.position.y); min_boy=minf(min_boy,g.boy.position.y); max_gap=maxf(max_gap,absf(g.player.position.x-g.boy.position.x))
		Input.action_release("right"); Input.action_release("left"); Input.action_release("sprint"); Input.action_release("interact")
		if crouch: Input.action_press("crouch")
		else: Input.action_release("crouch")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var at_target=absf(g.player.position.x-target_x)<16 and g.player.is_on_floor() and (target_y==INF or absf(g.player.position.y-target_y)<22)
		var boy_target=absf(g.boy.position.x-target_x)<100 and g.boy.is_on_floor() and (target_y==INF or absf(g.boy.position.y-target_y)<24)
		landed=landed or at_target; companion=companion or boy_target
		if at_target and boy_target: complete=true; break
		if not at_target:
			if g.player.position.x<target_x-10: Input.action_press("right")
			elif g.player.position.x>target_x+16: Input.action_press("left")
		# Leave enough room to let the follower land on the tread before moving
		# to the next ascent. No companion reposition or forced jump is used.
		if absf(g.player.position.x-g.boy.position.x)>125 and absf(g.player.position.y-g.boy.position.y)<30: Input.action_release("right")
		if climb and g.player.is_on_floor() and jump_hold==0 and not at_target:
			for platform in g.level.platforms:
				var ahead=float(platform.x)-g.player.position.x; var rise=g.player.position.y-float(platform.y)
				if ahead>0 and ahead<55 and rise>12 and rise<145:
					Input.action_press("jump"); jump_hold=24; jumps+=1; break
	release_inputs()
	return {"reached":complete,"girl_reached":landed,"boy_reached":companion,"frames":frames,"jumps":jumps,"maximum_gap":max_gap,"minimum_girl_y":min_girl,"minimum_boy_y":min_boy,"final_girl":{"x":g.player.position.x,"y":g.player.position.y},"final_boy":{"x":g.boy.position.x,"y":g.boy.position.y},"mode":g.mode}

static func physical_fork(g,index,branch,choice):
	var initial=await fixture_branch(g,index,branch,choice)
	var prefix=str(branch.id)+"_"+choice
	var record={"chapter":index+1,"branch":branch.id,"choice":choice,"initial":initial,"legs":[]}
	if choice=="paid_lower":
		var pump=task_by_id(g,branch.pump_id)
		var approach=await navigate(g,float(pump.x),INF,false,false,180)
		record.legs.append(approach)
		var pumped=await held_prompt(g,pump)
		g.assert_check(prefix+"_shared_held_pump_spends_one",approach.reached and pumped and g.scrap==0,JSON.stringify(approach))
		g.assert_check(prefix+"_drains_authored_lower_water",not g.in_water(float(branch.entry_x)+700,float(branch.lower_y)),str(g.flags.get(branch.pump_id,false)))
	if choice=="upper":
		var climbed=true
		# The first two treads are bounded waypoints; reaching both with both
		# children must happen before the next jump across the forty-pixel gap.
		for position in range(2):
			var platform=g.level.platforms[int(branch.platform_indices[position])]
			var leg=await navigate(g,float(platform.x)+float(platform.w)-30,float(platform.y),true,false,900)
			record.legs.append(leg); climbed=climbed and leg.reached
			if not leg.reached: break
		var brace=task_by_id(g,branch.safe_key)
		if climbed:
			var approach=await navigate(g,float(brace.x),float(branch.upper_y),true,false,900)
			record.legs.append(approach); climbed=climbed and approach.reached
		g.assert_check(prefix+"_both_children_climb_authored_steps",climbed,JSON.stringify(record.legs))
		# A brace is noisy work for longer than the listener's detection window.
		# Turn the real lane on before that held action so quiet walking cannot
		# accidentally make a broken upper/lower height test appear to pass.
		if climbed:
			g.level.hazard_lanes=active_listener(g,branch); g.playtime=1; g.invulnerable=0; g.hazard_exposure.clear()
		var braced=await held_prompt(g,brace) if climbed else false
		g.assert_check(prefix+"_held_brace_spends_one",braced and g.scrap==0,str(g.scrap))
		g.assert_check(prefix+"_noisy_upper_work_stays_above_listener",braced and g.health>99.9,str(g.health))
		var cache=task_by_id(g,branch.cache_id)
		var reached={"reached":false}
		if braced: reached=await navigate(g,float(cache.x),float(branch.upper_y),false,false,900); record.legs.append(reached)
		var searched=await held_prompt(g,cache) if reached.reached else false
		g.assert_check(prefix+"_both_reach_and_search_finite_cache",reached.reached and searched and g.rations==int(cache.rations) and g.medicine==int(cache.medicine),JSON.stringify(reached))
		# Keep the real listener active during the raised exit. Its height gate,
		# rather than an inactive timing phase or grace immunity, must protect them.
		var exit_leg=await navigate(g,float(branch.exit_x)+30,INF,false,false,1500) if searched else {"reached":false}
		record.legs.append(exit_leg)
		g.assert_check(prefix+"_both_physically_exit_upper_route",exit_leg.reached,JSON.stringify(exit_leg))
		g.assert_check(prefix+"_elevated_bypass_avoids_listener",searched and exit_leg.reached and g.health>99.9,str(g.health))
		g.assert_check(prefix+"_does_not_drain_lower_route",not g.flags.get(branch.pump_id,false) and g.in_water(float(branch.entry_x)+700,float(branch.lower_y)))
	else:
		var lower=await navigate(g,float(branch.exit_x)+30,INF,false,choice=="quiet_lower",3600)
		record.legs.append(lower)
		g.assert_check(prefix+"_both_walk_below_closed_upper_gate",lower.reached and not g.flags.get(branch.safe_key,false) and lower.jumps==0,JSON.stringify(lower))
		g.assert_check(prefix+"_quiet_lower_listener_survival",lower.reached and g.health>99.9,str(g.health))
		if choice=="quiet_lower": g.assert_check(prefix+"_wet_route_costs_warmth_without_salvage",g.wetness>.2 and g.warmth<95 and g.scrap==0 and not g.flags.get(branch.pump_id,false),"wetness=%0.3f warmth=%0.3f"%[g.wetness,g.warmth])
		else: g.assert_check(prefix+"_drained_route_stays_dry",g.wetness<.01,str(g.wetness))
	record["final_health"]=g.health; record["final_warmth"]=g.warmth; record["final_wetness"]=g.wetness; record["salvage_remaining"]=g.scrap
	print("FORK_PHYSICAL_RESULT ",JSON.stringify(record))
	return record
