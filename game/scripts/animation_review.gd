extends "res://scripts/game.gd"

# Reuses the real game, its paintings, follower, controller, and renderer.
# Only this review scene substitutes an isolated route. QA mode prevents saves.
func _ready():
	super._ready()
	if not "--motion" in OS.get_cmdline_user_args():
		smoke_test=true
		call_deferred("prepare_stage")

func prepare_stage():
	var fixture=levels[0].duplicate(true)
	fixture.ground=[{"x":0,"y":700,"w":8000,"h":600,"kind":"earth"}]
	fixture.width=8000; fixture.cold=0
	for key in ["platforms","gates","covers","interact","pushables","checkpoints","memories","tutorials","hazard_lanes","zones","mechanisms","water_zones","bridges"]: fixture[key]=[]
	fixture.erase("danger"); fixture.searchlight=false
	levels[0]=fixture; flags={}; load_chapter(0,false); mode="playing"; chapter_card=0
	player.position=Vector2(750,698); boy.position=Vector2(704,698)
	player.reset_feet(); boy.reset_feet(); camera.zoom=Vector2(2.2,2.2)
	camera.position=Vector2(900,610)
	message="MOVEMENT PRACTICE · A/D MOVE · SHIFT RUN · SPACE JUMP · S CROUCH"
	message_time=10000; muted=true; apply_volume()

func run_motion_review():
	prepare_stage()
	var folder=report_path("motion_frames"); DirAccess.make_dir_recursive_absolute(folder)
	var samples=[]
	for frame in range(660):
		for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)
		var label="WALK"
		if frame<90: Input.action_press("right")
		elif frame<150: Input.action_press("left"); label="BRAKE & TURN"
		elif frame<180: label="STOP & SETTLE"
		elif frame<240: Input.action_press("right"); Input.action_press("crouch"); label="CROUCH & RISE"
		elif frame<330: Input.action_press("right"); Input.action_press("sprint"); label="RUN"
		elif frame<375:
			Input.action_press("right"); label="JUMP & LAND"
			if frame<342: Input.action_press("jump")
		elif frame<405: label="LANDING RECOVERY"
		elif frame<465:
			label="SHARED WORK · PUMP"; Input.action_press("interact")
			pending_action={"kind":"pump","x":player.position.x,"companion_required":true}; action_duration=100; action_progress=0
			player.action_time=.12; boy.action_time=.12
		elif frame<495: pending_action={}; label="RELEASE & RECOVER"
		elif frame<555:
			label="SLOW, TIRED STEPS"; Input.action_press("right"); warmth=13; stamina=12
		elif frame<615:
			label="LOW SHELTER · ALERT"; Input.action_press("crouch"); exposure=1.2; lane_warning="ALERT"
		else: label="REUNION & REST"; warmth=100; stamina=100; exposure=0; lane_warning=""
		message="CHARACTER MOTION REVIEW · "+label; message_time=1
		await get_tree().process_frame
		# The close review follows the body without hiding the feet behind HUD.
		camera.position=Vector2(player.position.x+110,600)
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_jpg(folder.path_join("%04d.jpg"%frame),.92)
		if frame%15==0: samples.append({"frame":frame,"girl_state":player.animation_state,"boy_state":boy.animation_state,"girl":var_to_str(player.position),"boy":var_to_str(boy.position)})
	var report={"frames":660,"fps":30,"duration_seconds":22,"scope":"Close character motion study using the actual game renderer and both runtime controllers. Staged isolated flat route; work, fatigue and alert conditions are injected for review. Not campaign traversal or artistic acceptance.","samples":samples}
	var file=FileAccess.open(report_path("motion_review.json"),FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("CHARACTER_MOTION_REVIEW_COMPLETE"); call_deferred("quit_game")
