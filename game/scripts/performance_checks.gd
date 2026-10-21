extends RefCounted

# Native, bounded acting fixtures. The initial placements isolate existing
# cover and cart encounters; physics, warning clocks and Input remain live.
static var recording=false
static var recorded_frames=0
static var folder=""
static var caption=""
static var cues=[]
static var center=Vector2.ZERO
static var follow=false
static var render_measurements={}
static var previous_render_shoulder=Vector2.ZERO

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func tick(g,count=1):
	for frame in range(count):
		await g.get_tree().physics_frame
		if recording:
			await g.get_tree().process_frame
			g.chapter_card=0; g.message="CHARACTER PERFORMANCE STUDY / "+caption; g.message_time=1
			g.camera.zoom=Vector2(2.0,2.0)
			g.camera.position=g.player.position+Vector2(48,-110) if follow else center
			await RenderingServer.frame_post_draw
			if caption.begins_with("MOVING SHELTER") or caption.begins_with("RELEASE"):
				var sample=push_pose_sample(g.player)
				if caption.begins_with("MOVING SHELTER"):
					previous_render_shoulder=sample.shoulder
					render_measurements.push_frames+=1
					render_measurements.minimum_face_clearance=minf(render_measurements.minimum_face_clearance,sample.clearance)
					if sample.contact and g.player.work_blend>.96:
						render_measurements.live_grip_frames+=1
						render_measurements.maximum_grip_error=maxf(render_measurements.maximum_grip_error,sample.error)
				else:
					render_measurements.maximum_release_shoulder_step=maxf(render_measurements.maximum_release_shoulder_step,sample.shoulder.distance_to(previous_render_shoulder))
					previous_render_shoulder=sample.shoulder
					render_measurements.release_frames+=1
					render_measurements.minimum_release_face_clearance=minf(render_measurements.minimum_release_face_clearance,sample.clearance)
			g.get_viewport().get_texture().get_image().save_jpg(folder.path_join("%05d.jpg"%recorded_frames),.91)
			recorded_frames+=1

static func add(checks,name,passed,detail=""):
	checks.append({"check":name,"passed":passed,"details":detail})

static func prepare_cover(g):
	recording=false; release(); g.flags={}; g.cache_remaining={}
	g.load_chapter(2,false); g.mode="playing"; g.pending_action={}; g.trail.clear()
	g.health=100; g.warmth=100; g.food=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.shell_clock=0; g.shell_warning=0; g.exposure=0; g.playtime=0
	g.player.position=Vector2(1038,g.surface_y_at(1038,700)-2)
	g.boy.position=Vector2(1000,g.surface_y_at(1000,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.player.facing=1; g.boy.facing=1; g.player.reset_feet(); g.boy.reset_feet()
	await tick(g,16)
	center=Vector2(1060,590); follow=false

static func prepare_cart(g):
	recording=false; release(); g.flags={}; g.cache_remaining={}
	var data={}
	for entry in g.levels[3].get("mechanisms",[]):
		if entry.kind=="shelter_trolley": data=entry; break
	if data.is_empty(): return null
	for gate in g.levels[3].gates:
		if float(gate.x)<float(data.x): g.flags[gate.key]=true
	for bridge in g.levels[3].get("bridges",[]):
		if float(bridge.x)<float(data.x): g.flags[bridge.key]=true
	g.load_chapter(3,false); g.mode="playing"; g.pending_action={}; g.trail.clear()
	g.health=100; g.warmth=100; g.food=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.shell_clock=0; g.shell_warning=0; g.exposure=0; g.playtime=0
	var node=null
	for cart in g.trolley_encounters:
		if cart.data.id==data.id: node=cart; break
	if node==null: return null
	for pair in [[g.player,62],[g.boy,112]]:
		var child=pair[0]; var x=node.body.position.x-pair[1]
		child.position=Vector2(x,g.surface_y_at(x,node.cart_floor())-2)
		child.velocity=Vector2.ZERO; child.facing=1; child.reset_feet()
	g.boy.following=true; Input.action_press("crouch")
	await tick(g,18)
	follow=true
	return node

static func geometry_valid(child):
	var pose=child.body_pose()
	var points=child.coat_contour(pose,child.cloth_drag)
	if Geometry2D.triangulate_polygon(points).size()!=(points.size()-2)*3: return false
	for point in points:
		if not is_finite(point.x) or not is_finite(point.y): return false
	return true

static func push_pose_sample(child):
	var pose=child.body_pose(); var arms=child.arm_pose(pose)
	var elbow=child.near_elbow(arms.near_shoulder,arms.near,pose.head)
	var face=pose.head+Vector2(pose.head_facing*7,-2)
	var clearance=Geometry2D.get_closest_point_to_segment(face,elbow,arms.near).distance_to(face)
	var contacts=child.game.character_work_contacts(child)
	var active=contacts.get("kind","")=="cart_push"
	var error=0.0
	if active:
		for grip in ["near","far"]: error=maxf(error,child.to_global(arms[grip]).distance_to(contacts[grip]))
	return {"clearance":clearance,"contact":active,"error":error,"shoulder":pose.shoulder}

static func run(g):
	recording=false; recorded_frames=0; cues=[]
	var checks=[]; var evidence={}
	await prepare_cover(g)
	var anchors=[g.player.position,g.boy.position]
	var previous=g.player.body_pose().shoulder; var max_pose_step=0.0; var valid=true
	Input.action_press("crouch")
	for frame in range(26):
		await tick(g)
		var shoulder=g.player.body_pose().shoulder
		max_pose_step=maxf(max_pose_step,shoulder.distance_to(previous)); previous=shoulder
		for child in [g.player,g.boy]: valid=valid and geometry_valid(child)
	add(checks,"both_children_lower_into_existing_cover",g.is_covered(g.player) and g.is_covered(g.boy) and g.player.crouching and g.boy.crouching)
	Input.action_release("crouch")
	for frame in range(35):
		await tick(g)
		var shoulder=g.player.body_pose().shoulder
		max_pose_step=maxf(max_pose_step,shoulder.distance_to(previous)); previous=shoulder
		for child in [g.player,g.boy]: valid=valid and geometry_valid(child)
	var drift=maxf(g.player.position.distance_to(anchors[0]),g.boy.position.distance_to(anchors[1]))
	add(checks,"crouch_and_stand_preserve_the_grounded_feet",drift<.15 and not g.player.crouching and g.player.crouch_blend<.01,"body_drift=%.4f"%drift)
	add(checks,"weighted_stance_has_no_large_pose_step",max_pose_step<9.0,"maximum_shoulder_step=%.4f"%max_pose_step)
	add(checks,"curved_coat_contours_remain_valid_through_stance",valid)
	await tick(g,70)
	add(checks,"safe_close_idle_does_not_repeat_guarding_gestures",g.player.protect_blend<.03 and g.player.glance_blend<.03 and g.player.care_blend<.03)
	await prepare_cover(g); Input.action_press("crouch"); await tick(g,18)
	# Start at an explicit phase of the existing warning timer. The game owns
	# the warning growth and the protected impact; no threat blend is injected.
	g.shell_clock=8.4
	var max_warning=0.0; var max_guard=0.0; var close_contact=INF; var guard_near=Vector2.ZERO
	for frame in range(164):
		await tick(g)
		max_warning=maxf(max_warning,g.shell_warning); max_guard=maxf(max_guard,g.player.protect_blend)
		if g.player.protect_blend>.7:
			var pose=g.player.body_pose(); var arms=g.player.arm_pose(pose)
			close_contact=minf(close_contact,g.player.to_global(arms.far).distance_to(g.player.steady_target))
			guard_near=arms.near-arms.near_shoulder
	add(checks,"native_warning_drives_low_cover_protection",max_warning>.9 and max_guard>.7 and g.health==100,"warning=%.3f guard=%.3f health=%.1f"%[max_warning,max_guard,g.health])
	add(checks,"protective_hand_reaches_the_crouched_companion",close_contact<8,"closest_wrist_to_upper_arm=%.3f"%close_contact)
	evidence["cover"]={"maximum_warning":max_warning,"maximum_guard":max_guard,"contact_distance":close_contact,"stance_pose_step":max_pose_step,"body_drift":drift}
	await prepare_cover(g); Input.action_press("crouch"); g.warmth=10; g.wetness=.6; await tick(g,100)
	var cold_arms=g.player.arm_pose(g.player.body_pose())
	var cold_near=cold_arms.near-cold_arms.near_shoulder
	add(checks,"cold_and_danger_have_different_hand_silhouettes",g.player.cold_blend>.5 and g.player.danger_blend<.05 and cold_near.distance_to(guard_near)>7,"hand_pose_difference=%.3f"%cold_near.distance_to(guard_near))
	await prepare_cover(g)
	Input.action_press("right"); await tick(g,25); Input.action_release("right"); Input.action_press("left")
	var turned=false; var turn_valid=true
	for frame in range(25):
		await tick(g)
		turned=turned or (g.player.facing<0 and g.player.body_pose().head_facing<0)
		turn_valid=turn_valid and geometry_valid(g.player)
	release()
	add(checks,"native_reversal_turns_head_and_keeps_valid_cloth",turned and turn_valid)

	# Reproduce a follower landing into a stationary silhouette. Placement is
	# explicit; gravity and the native following clearance own all later motion.
	await prepare_cover(g)
	g.boy.position=g.player.position+Vector2(0,-90)
	g.boy.velocity=Vector2.ZERO; g.boy.reset_feet()
	var landing_start=g.boy.position; var previous_x=g.boy.position.x
	var max_separation_step=0.0; var landed=false
	for frame in range(140):
		await tick(g)
		landed=landed or g.boy.is_on_floor()
		max_separation_step=maxf(max_separation_step,absf(g.boy.position.x-previous_x)); previous_x=g.boy.position.x
	var separation=absf(g.player.position.x-g.boy.position.x)
	add(checks,"overlapping_landing_recovers_through_physical_steps",landed and g.boy.is_on_floor() and separation>=27.5 and separation<43 and absf(g.boy.position.x-landing_start.x)>24 and max_separation_step<3.5,"separation=%.3f maximum_step=%.3f"%[separation,max_separation_step])
	# The same overlap at an actual authored gap must not backstep into it.
	await prepare_cover(g)
	for child in [g.player,g.boy]:
		child.position=Vector2(1747,g.surface_y_at(1747,700)-2)
		child.velocity=Vector2.ZERO; child.facing=1; child.reset_feet()
	await tick(g,8)
	var ledge_at=g.boy.position; var unsafe_axis=false
	for frame in range(45):
		await tick(g)
		unsafe_axis=unsafe_axis or g.boy.ai_axis<-.01
	add(checks,"overlap_recovery_never_backsteps_off_an_actual_ledge",g.boy.is_on_floor() and g.boy.position.distance_to(ledge_at)<.15 and not unsafe_axis,"boy_drift=%.4f"%g.boy.position.distance_to(ledge_at))
	evidence["overlap_recovery"]={"landing_separation":separation,"maximum_horizontal_step":max_separation_step,"ledge_drift":g.boy.position.distance_to(ledge_at)}

	var cart=await prepare_cart(g)
	add(checks,"performance_uses_the_real_rigid_body_cart",cart!=null and cart.body is RigidBody2D)
	if cart!=null:
		var start=cart.body.position.x; var samples=0; var max_error=0.0; var action_free=true; var mesh_ok=true
		var push_trace=[]; var face_clearance=INF; var contact_ticks=0
		Input.action_press("right"); Input.action_press("interact")
		for frame in range(360):
			await tick(g)
			action_free=action_free and g.player.action_time<=0
			mesh_ok=mesh_ok and geometry_valid(g.player)
			var contacts=g.character_work_contacts(g.player)
			var pose=g.player.body_pose(); var all_arms=g.player.arm_pose(pose)
			var elbow=g.player.near_elbow(all_arms.near_shoulder,all_arms.near,pose.head)
			var face=pose.head+Vector2(pose.head_facing*7,-2)
			var clearance=Geometry2D.get_closest_point_to_segment(face,elbow,all_arms.near).distance_to(face)
			face_clearance=minf(face_clearance,clearance)
			if contacts.get("kind","")=="cart_push": contact_ticks+=1
			if frame%24==0 or clearance<8.5:
				push_trace.append({"frame":frame,"contact":contacts.get("kind",""),"work":g.player.work_blend,"push":g.player.push_blend,"threat":g.player.danger_blend,"clearance":clearance,"head":str(pose.head),"near":str(all_arms.near),"elbow":str(elbow),"shoulder":str(all_arms.near_shoulder)})
			if contacts.get("kind","")=="cart_push" and g.player.work_blend>.96:
				var arms=g.player.arm_pose(g.player.body_pose())
				for grip in ["near","far"]: max_error=maxf(max_error,g.player.to_global(arms[grip]).distance_to(contacts[grip]))
				samples+=1
			# Sample the whole bounded push, including the slopes and any contact gaps.
		var dx=cart.body.position.x-start
		add(checks,"native_contact_push_moves_the_cart_without_action_lock",dx>80 and action_free and cart.push_ticks>20,"travel=%.3f push_ticks=%d"%[dx,cart.push_ticks])
		add(checks,"both_hands_follow_the_actual_moving_handle",samples>=30 and max_error<2.5,"samples=%d max_grip_error=%.3f"%[samples,max_error])
		add(checks,"whole_push_keeps_the_near_forearm_clear_of_the_face",face_clearance>=8.5,"minimum_cheek_to_forearm_centerline=%.3f contact_ticks=%d"%[face_clearance,contact_ticks])
		add(checks,"loaded_cart_pose_keeps_bent_knees_and_valid_cloth",g.player.crouching and g.player.work_kind=="cart_push" and mesh_ok and g.player.body_pose().hip.y> -35)
		var pose_before=g.player.arm_pose(g.player.body_pose()); var clock=g.player.anim_time; var at=cart.body.position
		g.mode="pause"; await tick(g,24)
		add(checks,"pause_holds_handle_pose_and_physical_cart",pose_before==g.player.arm_pose(g.player.body_pose()) and clock==g.player.anim_time and cart.body.position.distance_to(at)<.1)
		g.mode="playing"; release()
		var release_clearance=INF; var release_step=0.0; var last_shoulder=g.player.body_pose().shoulder
		for frame in range(42):
			await tick(g)
			var sample=push_pose_sample(g.player)
			release_clearance=minf(release_clearance,sample.clearance)
			release_step=maxf(release_step,sample.shoulder.distance_to(last_shoulder)); last_shoulder=sample.shoulder
		add(checks,"release_settles_without_torso_pop_or_forearm_face_overlap",release_clearance>=8.5 and release_step<8,"minimum_clearance=%.3f maximum_shoulder_step=%.3f"%[release_clearance,release_step])
		add(checks,"letting_go_releases_the_push_pose",g.player.work_blend<.04 and g.player.action_time<=0)
		evidence["cart"]={"travel":dx,"samples":samples,"maximum_grip_error":max_error,"push_ticks":cart.push_ticks,"contact_ticks":contact_ticks,"minimum_face_clearance":face_clearance,"trace":push_trace}
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	var report={"build":"0.4.3","all_passed":passed,"checks":checks,"evidence":evidence,"physics_fps":Engine.physics_ticks_per_second,"method":"Native children, actual existing low cover and warning/impact timer, held crouch and reversal Input, and actual physical trolley contact. Only fixture start positions/resources and warning phase are prepared; no child or cart positions/velocities are driven afterward. Tests measure visible contact, stationary support, distinct threat/cold poses, curved polygon validity, pause and release. Not campaign traversal or artistic acceptance."}
	if "--record-performance" in OS.get_cmdline_user_args():
		report["recording"]=await record(g); report["recorded_frames"]=recorded_frames; report["fps"]=30
		add(checks,"recorded_push_forearm_stays_clear_at_render_sampling",render_measurements.push_frames==180 and render_measurements.minimum_face_clearance>=8.5,str(render_measurements))
		add(checks,"recorded_live_grips_follow_the_rendered_handle",render_measurements.live_grip_frames>=60 and render_measurements.maximum_grip_error<2.5,"live_grip_frames=%d maximum_error=%.3f"%[render_measurements.live_grip_frames,render_measurements.maximum_grip_error])
		add(checks,"recorded_release_keeps_the_forearm_below_the_face",render_measurements.release_frames==45 and render_measurements.minimum_release_face_clearance>=8.5 and render_measurements.maximum_release_shoulder_step<8,"release_frames=%d minimum_clearance=%.3f maximum_shoulder_step=%.3f"%[render_measurements.release_frames,render_measurements.minimum_release_face_clearance,render_measurements.maximum_release_shoulder_step])
		for check in checks:
			if not check.passed: report.all_passed=false
	return report

static func beat(g,label,count,actions=[]):
	release()
	for action in actions: Input.action_press(action)
	caption=label; cues.append({"frame":recorded_frames,"label":label})
	await tick(g,count)

static func record(g):
	folder=g.report_path("performance_motion_frames"); DirAccess.make_dir_recursive_absolute(folder)
	recorded_frames=0; cues=[]
	render_measurements={"push_frames":0,"live_grip_frames":0,"minimum_face_clearance":INF,"maximum_grip_error":0.0,"release_frames":0,"minimum_release_face_clearance":INF,"maximum_release_shoulder_step":0.0}
	await prepare_cover(g); recording=true
	await beat(g,"QUIET / CROUCH / WEIGHT",40,["crouch"])
	await beat(g,"STAND / SETTLE",30)
	await beat(g,"STEP / TURN",30,["right"])
	await beat(g,"REVERSE / PLANT",30,["left"])
	await prepare_cover(g); Input.action_press("crouch"); await tick(g,18); g.shell_clock=8.4
	recording=true; await beat(g,"LOW COVER / WATCHING THE OTHER CHILD",92,["crouch"])
	await prepare_cover(g); g.warmth=10; g.wetness=.6; recording=true
	await beat(g,"COLD / QUIET HANDS",75)
	var cart=await prepare_cart(g)
	if cart!=null:
		recording=true
		await beat(g,"MOVING SHELTER / HANDS ON HANDLE",180,["right","crouch","interact"])
		await beat(g,"RELEASE / SETTLE",45,["crouch"])
	recording=false; release()
	return {"enabled":true,"frames":recorded_frames,"fps":30,"duration_seconds":recorded_frames/30.0,"frame_directory":folder,"cues":cues,"render_measurements":render_measurements,"scope":"Native character performance study at existing cover and a real moving shelter cart. Initial fixture placements and an existing warning-clock phase are explicit. Actual Input drives crouch/stand/turn and pushing; no body teleport/velocity animation occurs after setup. Cuts/setup are excluded. A targeted acting study, not continuous campaign traversal or artistic acceptance."}
