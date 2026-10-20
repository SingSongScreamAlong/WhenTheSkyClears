extends RefCounted

static func frames(g,n):
	for i in range(n): await g.get_tree().physics_frame

static func release():
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)

static func run(g):
	g.start_crossing(); g.smoke_test=true
	await frames(g,30)
	g.assert_check("authored_children_standing_colliders",g.player.col.shape.size.y==99 and g.boy.col.shape.size.y==84)
	# Actual head clearance in the authored low beam, then standing on exit.
	g.player.position=Vector2(940,699); g.boy.position=Vector2(885,699)
	Input.action_press("crouch"); await frames(g,6)
	Input.action_release("crouch"); await frames(g,8)
	g.assert_check("release_crouch_under_beam_keeps_head_clear",g.player.crouching and g.player.col.shape.size.y==74)
	Input.action_press("right"); Input.action_press("crouch"); await frames(g,145)
	release(); await frames(g,40)
	g.assert_check("both_leave_low_passage_and_stand",g.player.position.x>1060 and g.boy.position.x>1047 and not g.player.crouching and not g.boy.crouching,str([g.player.position,g.boy.position]))
	# Wait is stable; call catches up without repositioning the follower.
	g.load_chapter(0,false); g.mode="playing"; await frames(g,20)
	g.boy.following=false; var bx=g.boy.position.x
	Input.action_press("right"); await frames(g,110); release(); await frames(g,10)
	g.assert_check("wait_command_holds_position",absf(g.boy.position.x-bx)<2)
	g.boy.following=true; await frames(g,200)
	g.assert_check("call_rejoins_and_settles",absf(g.player.position.x-g.boy.position.x)<60 and absf(g.boy.velocity.x)<8,str(g.boy.velocity))
	var settled=g.boy.position.x; await frames(g,90)
	g.assert_check("idle_follower_does_not_oscillate",absf(g.boy.position.x-settled)<2)
	Input.action_press("left"); await frames(g,85); release(); await frames(g,140)
	g.assert_check("reverse_direction_rejoins",absf(g.player.position.x-g.boy.position.x)<65)
	# An unlowered bridge is a real 330-unit gap: follower must wait at edge.
	g.load_chapter(1,false); g.mode="playing"; g.flags.erase("forest_bridge")
	g.boy.position=Vector2(1180,699); g.player.position=Vector2(1600,699); await frames(g,100)
	g.assert_check("unreachable_crossing_waits_without_suicide",g.boy.position.x<1210 and g.boy.position.y<730 and g.mode=="playing",str(g.boy.position))
	# High points left by an earlier descent cannot trigger a phantom jump.
	g.trail=[Vector3(g.boy.position.x,g.boy.position.y-100,0)]
	g.boy.ai_jump=false
	g.update_companion(1.0/60)
	g.assert_check("old_airborne_trail_cannot_trigger_jump",not g.boy.ai_jump)
	# Complete the authored freight crossing continuously after initial setup.
	g.start_crossing(); g.chapter_card=0
	var report=await cross(g,false)
	g.assert_check("freight_sequence_reached_shared_gate",report.reached_gate,str(report))
	g.assert_check("freight_sequence_supply_rest_and_shared_work",report.searched and report.rested and g.flags.get("freight_loading_bar",false),str(report))
	g.assert_check("freight_sequence_both_children_survive",g.mode=="playing" and g.death_count==0 and g.health>0,str(report))
	var passed=true
	for check in g.test_log:
		if not check.passed: passed=false
	var f=FileAccess.open(g.report_path("crossing_checks.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"all_passed":passed,"checks":g.test_log,"crossing":report,"scope":"Native controller checks use deliberate initial setups. Freight sequence then uses held Input actions with no actor repositioning, immunity or resource grants."},"\t")); f.close()
	print("CROSSING_RESULT ",passed," ",JSON.stringify(report)); g.quit_game(0 if passed else 1)

static func cross(g,capture):
	var searched=false; var rested=false; var reached=false; var jumped=false
	var phase="search"; var hold=0; var captures=0; var max_gap=0.0; var last_phase=""; var phase_events=[]
	var movie_folder=g.report_path("crossing_frames")
	if capture: DirAccess.make_dir_recursive_absolute(movie_folder)
	for tick in range(4600):
		for action in ["left","right","sprint","crouch","interact"]: Input.action_release(action)
		if hold<=0: Input.action_release("jump")
		if g.mode!="playing": break
		max_gap=maxf(max_gap,absf(g.player.position.x-g.boy.position.x))
		var x=g.player.position.x
		g.update_prompt()
		if phase=="search":
			Input.action_press("right")
			if x>690:
				Input.action_release("right"); Input.action_press("interact"); g.interact()
			if g.flags.get("camp_tools",false): searched=true; phase="return"
		elif phase=="return":
			Input.action_press("left")
			if x<570: phase="rest"
		elif phase=="rest":
			if absf(x-g.boy.position.x)<100:
				Input.action_press("interact"); g.interact()
			if g.rations==0 and g.warmth>60: rested=true; phase="beam"
		elif phase=="beam":
			Input.action_press("right")
			if x>850: Input.action_press("crouch")
			if x>1065: phase="wall"
		elif phase=="wall":
			Input.action_press("right")
			if g.player.is_on_floor() and x>1085 and x<1150: Input.action_press("jump"); hold=24
			if hold>0: Input.action_press("jump"); hold-=1
			if x>1380: phase="wait"
		elif phase=="wait":
			Input.action_press("crouch")
			# A visible cover beat, then leave after the beam has passed to the right.
			if absf(g.boy.position.x-x)<85 and g.beam_x()>2050 and g.shell_warning<.05: phase="gap"
		elif phase=="gap":
			Input.action_press("right"); Input.action_press("sprint")
			if g.player.is_on_floor() and x>1540 and not jumped: Input.action_press("jump"); hold=25; jumped=true
			if hold>0: Input.action_press("jump"); hold-=1
			if x>1840: phase="rejoin"
		elif phase=="rejoin":
			Input.action_press("crouch")
			if absf(x-g.boy.position.x)<80: phase="gate"
		elif phase=="gate":
			if x<2040: Input.action_press("right")
			elif absf(x-g.boy.position.x)<85: Input.action_press("interact"); g.interact()
			if g.flags.get("freight_loading_bar",false): reached=true; phase="done"
		elif phase=="done":
			if x<2250: Input.action_press("right")
			else: break
		if g.shell_warning>.03 and g.player.is_on_floor():
			for cover in g.level.covers:
				if absf(x-cover.x)<float(cover.w)*.45 and absf(g.boy.position.x-cover.x)<float(cover.w)*.45 and absf(g.player.position.y-700)<20:
					Input.action_release("right"); Input.action_release("left"); Input.action_press("crouch"); break
		await g.get_tree().physics_frame
		if capture and tick%2==0:
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%captures),.88); captures+=1
			if phase!=last_phase:
				g.get_viewport().get_texture().get_image().save_png(g.report_path("%02d_%s.png"%[phase_events.size(),phase]))
				phase_events.append({"phase":phase,"frame":captures-1,"time":g.playtime}); last_phase=phase
	release()
	return {"searched":searched,"rested":rested,"reached_gate":reached,"phase":phase,"girl":str(g.player.position),"boy":str(g.boy.position),"health":g.health,"warmth":g.warmth,"maximum_separation":max_gap,"frames":captures,"phase_events":phase_events,"deaths":g.death_count}

static func capture(g):
	g.start_crossing(); g.chapter_card=0
	var report=await cross(g,true)
	g.get_viewport().get_texture().get_image().save_png(g.report_path("crossing_arrival.png"))
	var f=FileAccess.open(g.report_path("capture_report.json"),FileAccess.WRITE); f.store_string(JSON.stringify(report,"\t")); f.close()
	print("CROSSING_CAPTURE ",JSON.stringify(report)); g.quit_game(0 if report.reached_gate else 1)
