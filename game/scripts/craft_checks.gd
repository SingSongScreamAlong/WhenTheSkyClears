extends RefCounted

# The native contact fixtures use real authored mechanisms and Input. Initial
# placement isolates the encounter; it is not a claim of campaign traversal.
const Canal=preload("res://scripts/refinement_checks.gd")
const Crossing=preload("res://scripts/sluice_checks.gd")
static var recording=false
static var recorded_frames=0
static var movie_folder=""
static var cues=[]
static var caption=""
static var camera_center=Vector2.ZERO
static var camera_zoom=2.15
static var camera_follow=false

static func tick(g,count=1):
	for frame in range(count):
		await g.get_tree().physics_frame
		if recording:
			await g.get_tree().process_frame
			g.chapter_card=0; g.message="CHARACTER ACTING STUDY · "+caption; g.message_time=1
			g.camera.zoom=Vector2(camera_zoom,camera_zoom)
			g.camera.position=g.player.position+Vector2(45,-112) if camera_follow else camera_center
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(movie_folder.path_join("%05d.jpg"%recorded_frames),.91)
			recorded_frames+=1

static func add(checks,name,passed,details=""):
	checks.append({"check":name,"passed":passed,"details":details})

static func contact_errors(child):
	var arms=child.arm_pose(child.body_pose())
	var scale_body=1.0 if child.is_girl else .84
	var contacts=child.game.character_work_contacts(child)
	var error=0.0; var count=0
	for grip in ["near","far"]:
		if contacts.has(grip):
			error=maxf(error,child.to_global(arms[grip]*scale_body).distance_to(contacts[grip])); count+=1
	return {"error":error,"grips":count}

static func run(g):
	recording=false; recorded_frames=0; cues=[]
	var checks=[]; var evidence={}
	var pump=await Canal.prepare(g)
	add(checks,"authored_pump_work_starts_with_held_input",Canal.start_work(g,pump))
	var grip_error=[0.0,0.0]; var grip_samples=[0,0]
	var shoulder_min=[INF,INF]; var shoulder_max=[-INF,-INF]
	var foot_origin=[]; var foot_drift=0.0
	for child in [g.player,g.boy]: foot_origin.append(child.position)
	for frame in range(90):
		await tick(g)
		for index in range(2):
			var child=[g.player,g.boy][index]
			if child.work_blend>.96 and child.work_contacts.has("near"):
				var contact=contact_errors(child)
				grip_error[index]=maxf(grip_error[index],contact.error); grip_samples[index]+=1
				var pose=child.body_pose()
				shoulder_min[index]=minf(shoulder_min[index],pose.shoulder.y)
				shoulder_max[index]=maxf(shoulder_max[index],pose.shoulder.y)
			foot_drift=maxf(foot_drift,child.position.distance_to(foot_origin[index]))
	for index in range(2):
		var label="girl" if index==0 else "boy"
		add(checks,label+"_hands_follow_actual_moving_lever",grip_samples[index]>25 and grip_error[index]<2.5,"samples=%d max_error=%.3f world_px"%[grip_samples[index],grip_error[index]])
	add(checks,"cooperative_effort_moves_shoulders_without_sliding_feet",shoulder_max[1]-shoulder_min[1]>4 and foot_drift<.15,"boy_shoulder_range=%.3f foot_drift=%.4f"%[shoulder_max[1]-shoulder_min[1],foot_drift])
	evidence["pump"]={"grip_error":grip_error,"samples":grip_samples,"shoulder_min":shoulder_min,"shoulder_max":shoulder_max,"foot_drift":foot_drift}
	var snapshot=[g.player.work_clock,g.boy.work_clock,g.player.arm_pose(g.player.body_pose()),g.boy.arm_pose(g.boy.body_pose())]
	g.mode="pause"; await tick(g,24)
	add(checks,"pause_holds_actual_contact_pose_and_effort_clock",snapshot==[g.player.work_clock,g.boy.work_clock,g.player.arm_pose(g.player.body_pose()),g.boy.arm_pose(g.boy.body_pose())])
	g.mode="playing"; Canal.release(); await tick(g,35)
	add(checks,"releasing_shared_work_eases_both_arms_out",g.pending_action.is_empty() and g.player.work_blend<.03 and g.boy.work_blend<.03 and g.player.action_time<=0 and g.boy.action_time<=0)

	var node=await Crossing.prepare(g)
	var approach=await Crossing.approach(g,node)
	add(checks,"pressure_pose_fixture_reaches_plate_through_native_movement",approach.reached,JSON.stringify(approach))
	await Crossing.command(g,"companion")
	for frame in range(150):
		await tick(g)
		if node.plate_child=="Boy" and g.boy.work_blend>.96: break
	var hold_error=contact_errors(g.boy)
	add(checks,"physical_plate_contact_activates_sustained_balance_pose",node.plate_child=="Boy" and g.boy.work_kind=="balance_hold" and g.boy.work_blend>.9 and hold_error.grips==2)
	add(checks,"balance_hands_meet_the_real_cradle_rail",hold_error.grips==2 and hold_error.error<2.5,str(hold_error))
	add(checks,"balance_acting_does_not_lock_the_child_in_an_action",g.boy.action_time<=0 and g.pending_action.is_empty())
	var held_at=g.boy.position
	await Crossing.command(g,"companion")
	Input.action_press("left"); await tick(g,55); Crossing.release(); await tick(g,45)
	add(checks,"calling_and_walking_off_plate_releases_balance_pose",g.boy.position.distance_to(held_at)>22 and g.boy.work_blend<.05 and g.boy.action_time<=0,"travel=%.3f blend=%.3f"%[g.boy.position.distance_to(held_at),g.boy.work_blend])
	evidence["pressure"]={"approach":approach,"contact":hold_error,"walk_off_distance":g.boy.position.distance_to(held_at)}
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	var report={"build":"0.4.2","all_passed":passed,"checks":checks,"evidence":evidence,"method":"Real authored pump and counterweight cradle, native children and Input. Isolated initial placements and disabled unrelated timed hazards. Measures rendered rig hand targets against actual mechanism grips, waist/shoulder effort, stationary work feet, pause, release and walking off a real pressure plate without action locking. Artistic review and campaign navigation are separate."}
	if "--record-craft" in OS.get_cmdline_user_args():
		report["recording"]=await record_study(g)
		report["recorded_frames"]=recorded_frames; report["fps"]=30
	return report

static func beat(g,label,count,actions=[]):
	Crossing.release()
	for action in actions: Input.action_press(action)
	caption=label; cues.append({"frame":recorded_frames,"label":label})
	await tick(g,count)

static func setup_stage(g,cold=false):
	recording=false; Crossing.release(); g.flags={}; g.cache_remaining={}
	var stage=g.levels[0].duplicate(true)
	stage.ground=[{"x":0,"y":700,"w":8000,"h":600,"kind":"earth"}]
	stage.width=8000; stage.cold=0
	for key in ["platforms","gates","interact","pushables","checkpoints","memories","tutorials","hazard_lanes","zones","mechanisms","water_zones","bridges"]: stage[key]=[]
	stage.covers=[{"x":840,"y":700,"w":230,"h":125,"kind":"tent"}]
	stage.erase("danger"); stage.searchlight=false
	var original=g.levels[0]; g.levels[0]=stage; g.load_chapter(0,false); g.levels[0]=original
	g.level=stage; g.mode="playing"; g.chapter_card=0; g.pending_action={}; g.trail.clear()
	g.health=48 if cold else 100; g.warmth=15 if cold else 100; g.food=100; g.stamina=100; g.wetness=.6 if cold else 0
	g.player.position=Vector2(750,698); g.boy.position=Vector2(714 if cold else 704,698)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO
	g.player.reset_feet(); g.boy.reset_feet(); g.boy.following=not cold
	if cold: g.player.anim_time=7.3
	await tick(g,12)
	camera_follow=true; camera_zoom=2.15

static func stage_item(g,entry,kind):
	recording=false; Crossing.release(); g.pending_action={}; g.player.action_time=0; g.boy.action_time=0
	var y=float(entry.get("y",700))
	g.player.position=Vector2(float(entry.x)-18,y-2); g.boy.position=Vector2(float(entry.x)-54,y-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.player.facing=1; g.boy.facing=1
	g.player.reset_feet(); g.boy.reset_feet(); g.boy.following=true
	g.health=70; g.warmth=25 if kind=="fire" else 100; g.food=65; g.rations=1 if kind=="fire" else 0; g.medicine=0; g.scrap=1
	await tick(g,12); g.update_prompt()
	Input.action_press("interact"); g.interact()
	camera_follow=false; camera_zoom=2.15; camera_center=Vector2(entry.x+36,y-102)

static func record_study(g):
	movie_folder=g.report_path("craft_motion_frames"); DirAccess.make_dir_recursive_absolute(movie_folder)
	recorded_frames=0; cues=[]
	await setup_stage(g)
	recording=true
	await beat(g,"WALK · PLANTED FEET",75,["right"])
	await beat(g,"BRAKE · TURN · HEAD LEADS",30,["left"])
	await beat(g,"STOP · WEIGHT SETTLES",15)
	await beat(g,"CROUCH · RISE",35,["right","crouch"])
	await beat(g,"RUN · CLOTH FOLLOW THROUGH",45,["right","sprint"])
	await beat(g,"TAKEOFF · AIR",12,["right","jump"])
	await beat(g,"PREPARE · LAND · RECOVER",24,["right"])
	await beat(g,"LANDING SETTLE",15)
	await setup_stage(g,true)
	recording=true
	await beat(g,"COLD HANDS · QUIET CARE",90)
	recording=false
	var pump=await Canal.prepare(g); Canal.start_work(g,pump)
	camera_follow=false; camera_zoom=2.15; camera_center=Vector2(pump.x+32,pump.y-105)
	caption="TWO CHILDREN · MOVING PUMP GRIPS"; cues.append({"frame":recorded_frames,"label":caption})
	recording=true; await tick(g,90); recording=false; Crossing.release()
	var node=await Crossing.prepare(g)
	await Crossing.approach(g,node); await Crossing.command(g,"companion"); await tick(g,40)
	camera_follow=false; camera_zoom=1.95; camera_center=Vector2(g.boy.position.x+95,g.boy.position.y-105)
	recording=true
	await beat(g,"WAIT · WEIGHT ON THE CRADLE",60)
	await Crossing.command(g,"companion")
	await beat(g,"CALL · RELEASE THE HOLD",45,["left"])
	recording=false
	g.load_chapter(0,false); g.level=g.level.duplicate(true); g.level.erase("danger"); g.level.hazard_lanes=[]; g.level.searchlight=false
	var fire={}; var cache={}
	for entry in g.level.interact:
		if entry.kind=="fire" and fire.is_empty(): fire=entry
		if entry.kind=="cache" and cache.is_empty(): cache=entry
	if not fire.is_empty():
		await stage_item(g,fire,"fire"); caption="SHELTER · WARMING HANDS"; cues.append({"frame":recorded_frames,"label":caption})
		recording=true; await tick(g,90); recording=false; Crossing.release()
	if not cache.is_empty():
		await stage_item(g,cache,"cache"); caption="SEARCH · ONE HAND BRACES"; cues.append({"frame":recorded_frames,"label":caption})
		recording=true; await tick(g,60); recording=false; Crossing.release()
	return {"enabled":true,"frames":recorded_frames,"fps":30,"duration_seconds":recorded_frames/30.0,"frame_directory":movie_folder,"cues":cues,"scope":"Normal-speed native character acting study using both actual children, Input and runtime renderer. Flat locomotion and cold/care sections use an explicitly staged isolated route; pump and pressure sections use authored mechanisms, held input and physical contact. Fire and search begin from explicit isolated placements. Scene changes and fixture preparation are excluded. Not continuous campaign traversal or artistic acceptance."}
