extends RefCounted

static func frames(g, count):
	for frame in range(count): await g.get_tree().physics_frame

static func place(g, x, y=700):
	g.player.position=Vector2(x,g.surface_y_at(x,y)-2)
	g.boy.position=Vector2(x-42,g.surface_y_at(x-42,y)-2)
	for child in [g.player,g.boy]:
		child.velocity=Vector2.ZERO; child.action_time=0; child.reset_feet()
	g.boy.following=true; g.message_time=0; g.chapter_card=0
	await frames(g,12)

static func capture(g, name):
	await g.get_tree().process_frame
	await g.get_tree().process_frame
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))

static func run(g, render=false):
	g.test_log=[]; g.flags={}; g.memories={}; g.journey_active=true
	if render:
		var target=SubViewport.new(); target.size=Vector2i(3840,2160)
		target.size_2d_override=Vector2i(1600,900); target.size_2d_override_stretch=true
		target.render_target_update_mode=SubViewport.UPDATE_ALWAYS
		g.get_tree().root.add_child(target); g.reparent(target); g.camera.make_current()
		g.mode="menu"; await capture(g,"01_title")
	for moment in g.story.data.moments:
		g.load_chapter(int(moment.chapter),false); g.mode="playing"
		for key in moment.get("requires",[]): g.flags[key]=true
		await place(g,float(moment.x),float(moment.y))
		g.update_prompt()
		g.assert_check(str(moment.id)+"_reachable_prompt",g.near_item.get("kind","")=="story",g.prompt)
		g.assert_check(str(moment.id)+"_both_in_real_shelter",g.story.can_begin())
		g.boy.position.x-=240
		g.assert_check(str(moment.id)+"_refuses_separation",not g.story.can_begin())
		g.boy.position.x+=240
		var task=moment.duplicate(true); task.kind="story"
		await g.test_action(task)
		g.assert_check(str(moment.id)+"_native_held_entry",g.mode=="stillness" and g.story.active)
		var snapshot=[g.health,g.warmth,g.food,g.rations,g.medicine,g.scrap,g.playtime]
		await frames(g,120)
		g.assert_check(str(moment.id)+"_no_cost_for_staying",snapshot==[g.health,g.warmth,g.food,g.rations,g.medicine,g.scrap,g.playtime])
		g.assert_check(str(moment.id)+"_shared_hand_contact",g.player.hand_active and g.boy.hand_active and g.player.hand_blend>.9)
		var elapsed=g.story.elapsed; g.mode="pause"; await frames(g,30)
		g.assert_check(str(moment.id)+"_pause_holds_story_time",g.story.elapsed==elapsed)
		g.resume_journey()
		g.assert_check(str(moment.id)+"_resume_returns_to_moment",g.mode=="stillness")
		await frames(g,210)
		if render: await capture(g,"02_moment_"+str(moment.chapter+1))
		g.story.finish()
		g.assert_check(str(moment.id)+"_returns_control_and_keeps_page",g.mode=="playing" and g.flags.get(moment.id,false))
	# Quiet HUD must react before survival reaches the damaging thresholds.
	g.health=100; g.warmth=100; g.food=100; g.wetness=0; g.lane_warning=""; g.exposure=0; g.shell_warning=0; g.chapter_card=0
	g.mode="playing"; await frames(g,120)
	g.assert_check("healthy_hud_recedes",g.story.hud_presence<.05)
	if render: await capture(g,"03_quiet_hud")
	g.warmth=40; await frames(g,120)
	g.assert_check("low_warmth_restores_meters",g.story.hud_presence>.95)
	g.always_show_hud=true; g.warmth=100; await frames(g,30)
	g.assert_check("always_visible_setting",g.story.hud_presence>.95)
	g.always_show_hud=false
	# All remembered pages remain browsable; there is no collection completion score.
	for i in range(21): g.memories["qa_"+str(i)]="A page kept dry. "+str(i)
	g.assert_check("journal_keeps_all_entries",g.story.kept_pages().size()==g.memories.size()+5 and g.story.kept_pages().has("A page kept dry. 20"))
	if render:
		g.mode="inventory"; g.hud.memory_page=6; await capture(g,"04_last_journal_page")
	# Actual final ground and native child controller. No position tween/teleport.
	g.load_chapter(4,false); g.mode="playing"
	await place(g,13900)
	var end_task={}
	for task in g.level.interact:
		if task.kind=="end": end_task=task
	g.player.action_time=0; g.complete_interaction(end_task)
	var girl_x=g.player.position.x; var boy_x=g.boy.position.x; var world_time=g.playtime
	g.assert_check("final_preserves_ending_contract",g.mode=="ending" and g.journey_completed)
	g.assert_check("final_echoes_played_opening",str(g.story.current.lines[0])=="He holds out his hand.")
	await frames(g,570)
	g.assert_check("boy_takes_real_step_ahead",g.boy.position.x>girl_x+30 and g.boy.position.x>boy_x+60,str(g.boy.position))
	g.assert_check("girl_waits_without_teleport",absf(g.player.position.x-girl_x)<.01)
	g.assert_check("ending_holds_survival_clock",g.playtime==world_time)
	g.assert_check("final_hand_contact_restored",g.player.hand_active and g.boy.hand_active)
	if render: await capture(g,"05_final_reversal")
	g.story.finish()
	if render: await capture(g,"06_ending")
	# Old saves default cleanly, while care decisions and the HUD preference persist.
	var original_save=g.save_path; var original_settings=g.settings_path
	g.save_path="user://qa_story_"+str(Time.get_ticks_usec())+".json"
	g.settings_path=g.save_path+".settings"
	g.always_show_hud=true; g.smoke_test=false; g.write_save()
	g.flags={}; g.always_show_hud=false; g.load_save(true)
	g.assert_check("care_flags_and_hud_preference_roundtrip",g.flags.get("care_village",false) and g.always_show_hud)
	DirAccess.remove_absolute(g.save_path); DirAccess.remove_absolute(g.settings_path)
	g.save_path=original_save; g.settings_path=original_settings; g.smoke_test=true
	var passed=true
	for check in g.test_log:
		if not check.passed: passed=false
	var report={"all_passed":passed,"checks":g.test_log,"scope":"Targeted native story/HUD tests. Authored refuge and ending positions are staged. Does not establish human emotional response or a continuous campaign playthrough.","engine":Engine.get_version_info()}
	var file=FileAccess.open(g.report_path("story_checks.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")); file.close()
	print("STORY_CHECKS_RESULT ",JSON.stringify(report))
	g.call_deferred("quit_game",0 if passed else 1)
