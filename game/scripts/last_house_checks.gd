extends RefCounted
static func frames(g,n):
	for i in range(n): await g.get_tree().physics_frame
static func release():
	for action in ["left","right","jump","sprint","crouch","interact"]:Input.action_release(action)
static func use(g):
	Input.action_press("interact");g.update_prompt();g.interact()
static func run(g):
	g.smoke_test=true
	var results=[]
	for upper in [false,true]:
		g.last_house.start(false);g.chapter_card=0;await frames(g,30)
		var result=await route(g,upper,false);results.append(result)
		g.assert_check("shop_route_completes" if upper else "arcade_route_completes",result.complete,str(result))
		g.assert_check("shop_supplies_collected" if upper else "arcade_preserves_shop_choice",bool(g.flags.get("shop_supplies",false))==upper,str(g.flags))
		g.assert_check("shop_pair_survives" if upper else "arcade_pair_survives",g.death_count==0 and g.health>0 and g.mode=="playing",str(result))
		g.assert_check("shop_reciprocal_help" if upper else "arcade_reciprocal_help",g.flags.get("passage_complete",false) and g.flags.get("damaged_passage",false))
		g.assert_check("shop_relief" if upper else "arcade_relief",g.flags.get("shared_meal",false) and g.warmth>94 and g.wetness<.1,str([g.warmth,g.wetness]))
	# Repeated/refused shelter actions cannot spend more supplies or finish early.
	g.last_house.start(false);g.player.position=Vector2(8560,699);g.boy.position=Vector2(8506,699);await frames(g,10)
	var share=g.level.interact.filter(func(p):return p.kind=="share")[0]
	var quiet=g.level.interact.filter(func(p):return p.kind=="quiet")[0]
	var support=g.level.interact.filter(func(p):return p.kind=="reciprocal")[0]
	g.update_prompt();g.assert_check("share_prerequisite_prompt_has_no_false_action",not g.prompt.begins_with("E ") and "bag" in g.prompt)
	g.last_house.try_interact(share);g.assert_check("share_requires_bag",not g.flags.get("shared_meal",false) and g.rations==1)
	g.flags["bag_down"]=true;g.boy.position.x=8250;g.last_house.try_interact(share)
	g.assert_check("share_waits_for_companion",not g.flags.get("shared_meal",false) and g.rations==1)
	g.boy.position.x=8506;g.wetness=.85;g.warmth=30;g.last_house.try_interact(share)
	g.assert_check("share_consumes_one_ration_and_warms",g.rations==0 and g.food>90 and g.warmth==95 and g.wetness<.16)
	var meal_food=g.food;g.last_house.try_interact(share)
	g.assert_check("repeat_share_never_duplicates_supplies",g.rations==0 and g.food==meal_food and not g.flags.get("emergency_bowl",false))
	g.last_house.try_interact(quiet);g.assert_check("quiet_requires_relief_time",not g.flags.get("last_house_complete",false))
	await frames(g,330);g.assert_check("dry_room_drains_wetness_and_preserves_warmth",g.wetness==0 and g.warmth>95,str([g.warmth,g.wetness]))
	g.last_house.try_interact(quiet);g.assert_check("relief_completion_remains_playable",g.flags.get("last_house_complete",false) and g.mode=="playing")
	g.assert_check("support_prompt_requires_held_input",g.last_house.prompt_for(support).begins_with("HOLD E"))
	g.last_house.stage="boy_holds";g.assert_check("support_transfer_prompt_releases_input",g.last_house.prompt_for(support).begins_with("WALK RIGHT"))
	g.last_house.stage="idle"
	# Boundary setup deliberately reproduces the former follower cover miss.
	g.last_house.start(false);g.player.position=Vector2(5362,699);g.boy.position=Vector2(5300,699)
	Input.action_press("crouch");await frames(g,150)
	g.assert_check("pair_fits_at_cover_edge",g.is_covered(g.player) and g.is_covered(g.boy),str([g.player.position,g.boy.position]))
	g.assert_check("pair_feedback_reports_covered",g.child_status(g.player)=="COVERED" and g.child_status(g.boy)=="COVERED")
	release();g.player.position=Vector2(6050,699);g.boy.position=Vector2(5910,699);g.boy.following=false
	Input.action_press("crouch");g.clock=-1.36;g.last_house.exposure={"Girl":0.0,"Boy":0.0};g.invulnerable=0
	# The light centre is pinned only in this isolated exposure fixture.
	for i in range(110):g.clock=-1.36;await frames(g,1)
	g.assert_check("uncovered_boy_gets_individual_seen_feedback",float(g.child_detection.Boy)>.08 or float(g.child_injury.Boy)>0,str(g.child_detection))
	g.assert_check("covered_girl_avoids_individual_injury",float(g.child_injury.Girl)==0 and float(g.child_injury.Boy)>0,str(g.child_injury))
	release()
	# Abort, return and retry the reciprocal passage using held input.
	g.last_house.start(false);g.player.position=Vector2(3900,699);g.boy.position=Vector2(3846,699);await frames(g,10)
	use(g);await frames(g,25);release();await frames(g,160)
	g.assert_check("early_release_returns_companion_safely",g.last_house.stage=="idle" and g.boy.position.x<3890 and not g.flags.get("passage_braced",false),str([g.last_house.stage,g.boy.position]))
	use(g);await frames(g,190);release()
	g.assert_check("reciprocal_retry_transfers_support",g.last_house.stage=="boy_holds" and g.flags.get("passage_braced",false),g.last_house.stage)
	g.assert_check("boy_holds_catch_standing",not g.boy.crouching and g.boy.col.shape.size.y==99)
	var call=InputEventAction.new();call.action="companion";call.pressed=true;g._unhandled_input(call)
	g.assert_check("companion_call_cannot_interrupt_support",g.last_house.stage=="boy_holds" and not g.boy.following)
	Input.action_press("right");await frames(g,180);release();await frames(g,100)
	g.assert_check("both_clear_retried_passage",g.flags.get("passage_complete",false) and g.boy.position.x>4270,str([g.player.position,g.boy.position]))
	# Save/load uses private disposable paths and actual disk IO.
	var unique="user://qa_slice_"+str(Time.get_ticks_usec())
	g.last_house_save_path=unique+".slice";g.journey_save_path=unique+".main";g.settings_path=unique+".settings"
	g.save_path=g.last_house_save_path;g.checkpoint_x=4500;g.smoke_test=false;g.write_save()
	var saved=FileAccess.get_file_as_string(g.save_path);g.return_to_title();g.last_house.start(true)
	g.assert_check("slice_save_resumes_own_layout",g.slice_active and g.level.id=="last_house" and g.checkpoint_x==4500 and g.flags.get("passage_complete",false))
	g.assert_check("slice_save_leaves_main_absent",not FileAccess.file_exists(g.journey_save_path))
	g.new_journey();g.flags["qa_main"]=true;g.write_save();var main=FileAccess.get_file_as_string(g.journey_save_path)
	g.last_house.start(true);g.return_to_title()
	g.assert_check("slice_preserves_existing_main_bytes",FileAccess.get_file_as_string(g.journey_save_path)==main)
	g.continue_journey();g.assert_check("main_continue_after_slice_restores_journey",not g.slice_active and not g.section_preview and g.chapter==0 and g.flags.get("qa_main",false))
	g.last_house.start(true)
	g.player.position.y=1100;await frames(g,3);g.assert_check("slice_fall_enters_recovery",g.mode=="recovering")
	await frames(g,100);g.assert_check("slice_retry_keeps_completed_passage",g.mode=="playing" and g.player.position.x==4500 and g.boy.following and g.flags.get("passage_complete",false),str(g.player.position))
	g.mode="pause";g.hud.activate("last_house_new");await frames(g,3)
	g.assert_check("pause_menu_can_restart_slice_cleanly",g.mode=="playing" and g.slice_active and g.player.position.x==180 and g.flags.is_empty() and g.rations==1)
	g.assert_check("slice_restart_preserves_main_bytes",FileAccess.get_file_as_string(g.journey_save_path)==main)
	for path in [g.last_house_save_path,g.journey_save_path,g.settings_path]:
		for suffix in ["",".bak",".tmp"]:
			if FileAccess.file_exists(path+suffix):DirAccess.remove_absolute(path+suffix)
	g.smoke_test=true
	var passed=true
	for check in g.test_log:
		if not check.passed:passed=false
	var f=FileAccess.open(g.report_path("last_house_checks.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"all_passed":passed,"checks":g.test_log,"routes":results,"scope":"Both routes use native held Input continuously from fresh start without repositioning, immunity, resource grants or geometry changes. Separate boundary, abort and save/retry fixtures deliberately set initial actor positions. Scripted verification; no human controller, Mac or audio review claimed."},"\t"));f.close()
	print("SLICE_RESULT ",passed," ",JSON.stringify(results));g.quit_game(0 if passed else 1)

static func route(g,upper,capture):
	var phase="photo";var hold=0;var max_gap=0.0;var last_phase="";var events=[];var n=0;var details={}
	var folder=g.report_path("slice_frames")
	if capture:DirAccess.make_dir_recursive_absolute(folder)
	var last_x=g.player.position.x;var stuck=0;var jumps={};var covers=[5480,6120,6880];var cover_index=0
	for tick in range(16000):
		for action in ["left","right","sprint","crouch","interact"]:Input.action_release(action)
		if hold<=0:Input.action_release("jump")
		if g.mode!="playing":break
		var x=g.player.position.x;var y=g.player.position.y
		max_gap=maxf(max_gap,absf(x-g.boy.position.x))
		if absf(x-last_x)<.1:stuck+=1
		else:stuck=0
		last_x=x
		if phase=="photo":
			if x<910:Input.action_press("right")
			else:use(g)
			if g.flags.get("house_photo",false):phase="bread"
		elif phase=="bread":
			if x<1270:Input.action_press("right")
			else:use(g)
			if g.flags.get("house_bread",false):phase="approach"
		elif phase=="approach":
			Input.action_press("right")
			if x>1740 and g.player.is_on_floor() and not jumps.has("entry"):Input.action_press("jump");hold=26;jumps["entry"]=true
			if x>1850 and y<650:phase="shop" if upper else "arcade"
		elif phase=="arcade":
			Input.action_press("right");Input.action_press("crouch")
			if x>3250:phase="passage"
		elif phase=="shop":
			Input.action_press("right")
			if g.player.is_on_floor() and x>1900 and not jumps.has("shelf"):Input.action_press("jump");hold=28;jumps["shelf"]=true
			if g.player.is_on_floor() and x>2125 and x<2220 and not jumps.has("shelf_gap"):Input.action_press("jump");hold=26;jumps["shelf_gap"]=true
			if x>2670 and not g.flags.get("shop_supplies",false):Input.action_release("right");use(g)
			if x>3280:phase="passage"
		elif phase=="passage":
			if x<3895:Input.action_press("right")
			elif g.last_house.stage!="boy_holds" and not g.flags.get("passage_complete",false):use(g)
			else:Input.action_press("right")
			if x>4400:phase="rail_approach"
		elif phase=="rail_approach":
			Input.action_press("right")
			if x>5470:phase="cover_wait"
		elif phase=="cover_wait":
			Input.action_press("crouch")
			var beam=g.last_house.beam_x();var safe=false
			# Leave after the beam is moving away from the next island.
			if cover_index==0:safe=beam>6400 and cos(g.clock*.34)>0
			elif cover_index==1:safe=beam<5920 and cos(g.clock*.34)<0
			else:safe=beam<6350
			if safe and g.is_covered(g.boy) and absf(x-g.boy.position.x)<80:phase="rail_run"
		elif phase=="rail_run":
			Input.action_press("right");Input.action_press("sprint")
			var edge=5640 if cover_index==0 else 6460
			if cover_index<2 and x>edge-25 and g.player.is_on_floor() and not jumps.has(str(edge)):
				Input.action_press("jump");hold=30;jumps[str(edge)]=true
			var goal=6120 if cover_index==0 else (6880 if cover_index==1 else 7420)
			if x>=goal:
				cover_index+=1;phase="cover_wait" if cover_index<3 else "room"
		elif phase=="room":
			if x<8290:Input.action_press("right")
			elif absf(x-g.boy.position.x)<100:use(g)
			if g.flags.get("bag_down",false):phase="share"
		elif phase=="share":
			if x<8550:Input.action_press("right")
			else:use(g)
			if g.flags.get("shared_meal",false):phase="quiet"
		elif phase=="quiet":
			if x<8760:Input.action_press("right")
			else:use(g)
			if g.flags.get("last_house_complete",false):phase="complete"
		if hold>0:Input.action_press("jump");hold-=1
		await g.get_tree().physics_frame
		if capture and tick%4==0:
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(folder.path_join("%05d.jpg"%n),.87);n+=1
		if capture:
			var detail=""
			if g.last_house.stage=="girl_holds" and g.boy.position.x>4020:detail="girl_holds_support"
			elif g.last_house.stage=="boy_holds":detail="boy_holds_support"
			elif phase=="cover_wait" and g.is_covered(g.player) and g.is_covered(g.boy) and absf(x-g.boy.position.x)<65 and absf(g.boy.velocity.x)<12:detail="pair_covered_%d"%cover_index
			elif upper and g.flags.get("shop_supplies",false) and x<2850:detail="exposed_shop_supplies"
			if detail!="" and not details.has(detail):
				await RenderingServer.frame_post_draw;g.get_viewport().get_texture().get_image().save_png(g.report_path("detail_"+detail+".png"));details[detail]={"frame":n,"time":g.playtime,"girl":str(g.player.position),"boy":str(g.boy.position),"girl_state":g.child_status(g.player),"boy_state":g.child_status(g.boy)}
		if phase!=last_phase:
			events.append({"phase":phase,"frame":n,"time":g.playtime,"girl":str(g.player.position),"boy":str(g.boy.position),"health":g.health});last_phase=phase
			if capture:
				await RenderingServer.frame_post_draw;g.get_viewport().get_texture().get_image().save_png(g.report_path("%02d_%s.png"%[events.size(),phase]))
		if phase=="complete":break
	release()
	return {"upper_shop":upper,"complete":g.flags.get("last_house_complete",false),"phase":phase,"girl":str(g.player.position),"boy":str(g.boy.position),"health":g.health,"warmth":g.warmth,"wetness":g.wetness,"deaths":g.death_count,"maximum_separation":max_gap,"playtime":g.playtime,"frames":n,"events":events,"details":details,"stuck_frames":stuck}

static func capture(g):
	g.last_house_save_path="user://qa_capture_"+str(Time.get_ticks_usec())+".slice"
	g.mode="menu";await frames(g,30);await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path("startup_title.png"))
	var title_has_slice=g.hud.buttons.any(func(b):return b.action=="last_house")
	g.hud.activate("last_house");g.chapter_card=0;await frames(g,30)
	var result=await route(g,"--shop-route" in g.qa_args,true)
	result["title_has_slice"]=title_has_slice
	g.mode="pause";await frames(g,3);await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path("pause_slice.png"))
	result["pause_has_restart"]=g.hud.buttons.any(func(b):return b.action=="last_house_new")
	var f=FileAccess.open(g.report_path("slice_capture.json"),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	g.quit_game(0 if result.complete and title_has_slice and result.pause_has_restart else 1)
