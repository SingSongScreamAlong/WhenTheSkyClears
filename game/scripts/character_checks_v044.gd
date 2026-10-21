extends RefCounted

const Child=preload("res://scripts/child_v2.gd")
const Pump=preload("res://scripts/refinement_checks.gd")
const Crossing=preload("res://scripts/sluice_checks.gd")
const Garden=preload("res://scripts/garden_puzzle_checks_v044.gd")
const BASE=60000.0
static var recording=false
static var recorded_frames=0
static var frame_folder=""
static var caption=""
static var cues=[]
static var camera_center=Vector2.ZERO
static var camera_follow=false

class LiftDeck extends AnimatableBody2D:
	var drive_velocity=Vector2.ZERO
	func _physics_process(dt): position+=drive_velocity*dt

class SupportFixture extends Node2D:
	var mode="playing"
	var chapter=0
	var stamina=100.0
	var health=100.0
	var warmth=100.0
	var wetness=0.0
	var shell_warning=0.0
	var exposure=0.0
	var lane_warning=""
	var pending_action={}
	var level={"ground":[],"platforms":[]}
	var player
	var boy
	var mirror_input=false
	func _physics_process(_dt):
		if mirror_input and is_instance_valid(boy): boy.ai_axis=Input.get_axis("left","right")
	func in_water(_x,_y=700.0): return false
	func wind_speed_scale(_child): return 1.0
	func play_step(_p,_db): pass
	func spawn_dust(_p,_count): pass
	func surface_y_at(x,fallback=700.0):
		var query=PhysicsRayQueryParameters2D.create(Vector2(x,fallback-36),Vector2(x,fallback+41),1)
		var hit=get_world_2d().direct_space_state.intersect_ray(query)
		return float(hit.position.y) if not hit.is_empty() else fallback

static func release():
	for action in ["left","right","jump","sprint","crouch","interact","companion"]: Input.action_release(action)

static func tick(g,count=1):
	for frame in range(count):
		await g.get_tree().physics_frame
		if recording:
			await g.get_tree().process_frame
			g.chapter_card=0; g.message="CHARACTER MOTION STUDY / "+caption; g.message_time=1
			g.camera.zoom=Vector2(2.15,2.15)
			g.camera.position=g.player.position+Vector2(15,-95) if camera_follow else camera_center
			await RenderingServer.frame_post_draw
			g.get_viewport().get_texture().get_image().save_jpg(frame_folder.path_join("%05d.jpg"%recorded_frames),.92)
			recorded_frames+=1

static func add(checks,name,passed,details=""):
	checks.append({"check":name,"passed":passed,"details":details})

static func static_floor(parent,points):
	var body=StaticBody2D.new(); body.collision_layer=1; body.collision_mask=2
	var col=CollisionPolygon2D.new(); col.polygon=points; body.add_child(col); parent.add_child(body)
	return body

static func fixture(g,deck=false,vertical=false):
	recording=false; release(); g.mode="pause"
	var world=SupportFixture.new(); g.get_tree().root.add_child(world)
	static_floor(world,PackedVector2Array([Vector2(BASE,700),Vector2(BASE+1200,700),Vector2(BASE+1600,660),Vector2(BASE+2200,660),Vector2(BASE+2200,1300),Vector2(BASE,1300)]))
	world.level.ground=[{"x":BASE,"y":700,"w":2200,"h":600}]
	var body=null
	if deck:
		if vertical:
			body=LiftDeck.new(); body.sync_to_physics=true
		else:
			body=RigidBody2D.new(); body.gravity_scale=0; body.lock_rotation=true
			body.mass=10000; body.linear_damp=0; body.freeze=true
		body.name="NativeSupportDeck"; body.collision_layer=1; body.collision_mask=2
		body.set_meta("mechanism_drive_only",true)
		body.position=Vector2(BASE+360,679)
		var shape=CollisionShape2D.new(); shape.shape=RectangleShape2D.new(); shape.shape.size=Vector2(230,18)
		body.add_child(shape); world.add_child(body)
	for index in range(2):
		var child=Child.new(); child.game=world; child.is_girl=index==0; child.controlled=index==0
		child.position=Vector2(BASE+350-index*45,668 if deck else 698)
		if index==0: world.player=child
		else: world.boy=child
		world.add_child(child)
	await tick(g,12)
	return {"world":world,"body":body}

static func dispose(g,world):
	world.mode="pause"; world.queue_free(); release(); await tick(g,2)

static func planted_shape(child):
	var scale_body=1.0 if child.is_girl else .84
	var result=[]
	for i in range(2): result.append(child.position+child.feet[i]*scale_body)
	return result

static func head_and_support_checks(g,checks,evidence):
	var fixture_data=await fixture(g)
	var world=fixture_data.world; world.mirror_input=true
	add(checks,"intermediate_painted_angles_are_loaded",world.player.head_angles!=null and world.boy.head_angles!=null)
	Input.action_press("right"); await tick(g,20); release(); Input.action_press("left")
	var previous=world.player.head_yaw; var maximum_step=0.0; var intermediate=0; var anticipation=false
	for frame in range(36):
		await tick(g)
		var child=world.player; var mix=child.head_render_profile()
		maximum_step=maxf(maximum_step,absf(child.head_yaw-previous)); previous=child.head_yaw
		if mix.quarter>.35 or mix.front>.35: intermediate+=1
		if child.head_goal<0 and child.head_turn_elapsed<.055 and child.head_yaw>.5: anticipation=true
	add(checks,"native_reversal_anticipates_before_rotating_the_head",anticipation and world.player.facing<0)
	add(checks,"head_rotation_crosses_painted_intermediate_angles",intermediate>=6 and world.player.head_yaw<-.98 and maximum_step<.25,"intermediate_ticks=%d maximum_yaw_step=%.4f"%[intermediate,maximum_step])
	var yaw=world.player.head_yaw; var elapsed=world.player.head_turn_elapsed
	world.mode="pause"; await tick(g,14)
	add(checks,"pause_freezes_attention_and_head_rotation",yaw==world.player.head_yaw and elapsed==world.player.head_turn_elapsed)
	world.mode="playing"; release(); world.mirror_input=false; world.boy.ai_axis=0
	await tick(g,35)
	evidence.head={"intermediate_ticks":intermediate,"maximum_yaw_step":maximum_step}
	await dispose(g,world)

	var support_results=[]
	for velocity in [Vector2(60,0),Vector2(0,-45)]:
		fixture_data=await fixture(g,true,velocity.y!=0); world=fixture_data.world; var deck=fixture_data.body
		Input.action_press("crouch"); world.boy.forced_crouch=true; await tick(g,14)
		var origins=[]; var relative=[]; var phases=[]
		for child in [world.player,world.boy]:
			origins.append(child.position); phases.append(child.phase)
			var feet=planted_shape(child); relative.append([feet[0]-deck.position,feet[1]-deck.position])
		var start=deck.position; var maximum_drift=0.0; var contact_ticks=[0,0]
		if deck is RigidBody2D: deck.freeze=false; deck.linear_velocity=velocity
		else: deck.drive_velocity=velocity
		for frame in range(90):
			await tick(g)
			for index in range(2):
				var child=[world.player,world.boy][index]; var feet=planted_shape(child)
				if child.is_on_floor() and child.get_platform_velocity().length()>10: contact_ticks[index]+=1
				for foot in range(2): maximum_drift=maxf(maximum_drift,(feet[foot]-deck.position).distance_to(relative[index][foot]))
		var travel=deck.position.distance_to(start); var carried=true; var still=true
		for index in range(2):
			var child=[world.player,world.boy][index]
			carried=carried and child.position.distance_to(origins[index])>travel-3 and child.is_on_floor()
			still=still and absf(child.phase-phases[index])<.02
		var axis="horizontal" if velocity.x!=0 else "vertical"
		add(checks,axis+"_native_platform_physically_carries_both_children",travel>55 and carried and contact_ticks[0]>75 and contact_ticks[1]>75,"travel=%.3f contacts=%s"%[travel,str(contact_ticks)])
		add(checks,axis+"_support_soles_stay_planted_relative_to_the_deck",maximum_drift<1.5 and still,"maximum_relative_sole_drift=%.4f no_walking_gait=%s"%[maximum_drift,str(still)])
		support_results.append({"axis":axis,"travel":travel,"sole_drift":maximum_drift,"contact_ticks":contact_ticks})
		await dispose(g,world)
	evidence.platforms=support_results
	fixture_data=await fixture(g,true); world=fixture_data.world
	var controlled_deck=fixture_data.body; var at=controlled_deck.position
	controlled_deck.freeze=false; Input.action_press("interact"); Input.action_press("right"); await tick(g,14)
	add(checks,"ordinary_E_walking_cannot_bypass_a_mechanism_only_deck",absf(controlled_deck.linear_velocity.x)<3 and controlled_deck.position.distance_to(at)<2 and not world.player.pushing,"deck_speed=%.3f travel=%.3f"%[controlled_deck.linear_velocity.x,controlled_deck.position.distance_to(at)])
	await dispose(g,world)

static func prepare_attention(g):
	recording=false; release(); g.flags={}; g.cache_remaining={}; g.load_chapter(1,false)
	g.level=g.level.duplicate(true); g.level.erase("danger"); g.level.hazard_lanes=[]; g.level.searchlight=false
	for gate in g.level.gates: g.flags[gate.key]=true
	g.mode="playing"; g.health=100; g.warmth=100; g.food=100; g.stamina=100; g.wetness=0
	g.pending_action={}; g.trail.clear(); g.chapter_card=0
	g.player.position=Vector2(12880,538); g.boy.position=Vector2(12838,538)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.boy.following=true
	g.player.reset_feet(); g.boy.reset_feet(); await tick(g,20)
	camera_follow=true; camera_center=Vector2(12880,435)

static func authored_work_checks(g,checks,evidence):
	var pump=await Pump.prepare(g)
	add(checks,"real_cooperative_pump_is_reached_and_started",Pump.start_work(g,pump))
	var previous=[g.player.body_pose().shoulder,g.boy.body_pose().shoulder]
	var maximum_step=0.0; var maximum_error=0.0; var samples=0; var origin=[g.player.position,g.boy.position]; var drift=0.0
	for frame in range(85):
		await tick(g)
		for index in range(2):
			var child=[g.player,g.boy][index]; var pose=child.body_pose(); var arms=child.arm_pose(pose)
			maximum_step=maxf(maximum_step,pose.shoulder.distance_to(previous[index])); previous[index]=pose.shoulder
			drift=maxf(drift,child.position.distance_to(origin[index]))
			var contacts=g.character_work_contacts(child); var scale_body=1.0 if child.is_girl else .84
			if contacts.has("near") and child.work_blend>.96:
				for grip in ["near","far"]: maximum_error=maxf(maximum_error,child.to_global(arms[grip]*scale_body).distance_to(contacts[grip]))
				samples+=1
	release()
	for frame in range(35):
		await tick(g)
		for index in range(2):
			var child=[g.player,g.boy][index]; var pose=child.body_pose()
			maximum_step=maxf(maximum_step,pose.shoulder.distance_to(previous[index])); previous[index]=pose.shoulder
	add(checks,"cooperative_hands_follow_actual_pump_geometry",samples>75 and maximum_error<2.5,"samples=%d maximum_error=%.3f"%[samples,maximum_error])
	add(checks,"prop_reach_and_release_keep_weight_over_stationary_feet",drift<.15 and maximum_step<9 and g.player.work_blend<.03 and g.boy.work_blend<.03,"foot_drift=%.4f maximum_shoulder_step=%.3f"%[drift,maximum_step])
	evidence.work={"grip_samples":samples,"maximum_grip_error":maximum_error,"maximum_shoulder_step":maximum_step,"foot_drift":drift}

static func rig_contact_sample(child):
	var pose=child.body_pose(); var arms=child.arm_pose(pose); var scale_body=1.0 if child.is_girl else .84
	var contacts=child.game.character_work_contacts(child); var error=0.0; var count=0
	for grip in ["near","far"]:
		if contacts.has(grip): error=maxf(error,child.to_global(arms[grip]*scale_body).distance_to(contacts[grip])); count+=1
	var elbow=child.near_elbow(arms.near_shoulder,arms.near,pose.head)
	var face=pose.head+Vector2(pose.head_facing*7,-2)
	var clearance=Geometry2D.get_closest_point_to_segment(face,elbow,arms.near).distance_to(face)*scale_body
	return {"grips":count,"error":error,"clearance":clearance,"head":str(pose.head),"near":str(arms.near),"shoulder":str(arms.near_shoulder)}

static func authored_support_checks(g,checks,evidence):
	var crossing=await Crossing.prepare(g); await Crossing.approach(g,crossing); await Crossing.command(g,"companion")
	await tick(g,50)
	var rail=rig_contact_sample(g.boy)
	add(checks,"real_counterweight_brace_retains_its_authored_grips",rail.grips==2 and rail.error<2.5,str(rail))
	add(checks,"real_rail_brace_keeps_the_near_forearm_clear_of_the_cheek",rail.clearance>7,"cheek_clearance=%.3f"%rail.clearance)
	evidence.brace=rail
	var node=await Garden.prepare(g,true)
	add(checks,"real_ferry_fixture_has_both_native_floor_contacts",node!=null and node.both_boarded() and node.both_low())
	if node==null: return
	var origins=[]; var relative=[]
	for child in [g.player,g.boy]:
		origins.append(child.position); var feet=planted_shape(child); relative.append([feet[0]-node.body.position,feet[1]-node.body.position])
	var at=node.body.position; var drift=0.0; var samples=0; var errors=[0.0,0.0]; var clearance=[INF,INF]; var contacts=0
	Input.action_press("interact")
	for frame in range(150):
		await tick(g)
		if node.both_boarded(): contacts+=1
		for index in range(2):
			var child=[g.player,g.boy][index]; var feet=planted_shape(child)
			for foot in range(2): drift=maxf(drift,(feet[foot]-node.body.position).distance_to(relative[index][foot]))
			var sample=rig_contact_sample(child)
			if sample.grips==2 and child.work_blend>(.96 if index==0 else .77):
				errors[index]=maxf(errors[index],sample.error); clearance[index]=minf(clearance[index],sample.clearance)
				if index==0: samples+=1
	release()
	add(checks,"actual_cranking_carries_both_planted_silhouettes",node.body.position.distance_to(at)>65 and drift<1.5 and contacts>130,"travel=%.3f sole_drift=%.4f true_contact_ticks=%d"%[node.body.position.distance_to(at),drift,contacts])
	add(checks,"actual_reel_hands_follow_the_visible_moving_crank",samples>90 and errors[0]<2.5,"samples=%d maximum_girl_error=%.3f"%[samples,errors[0]])
	add(checks,"settled_ferry_rail_hands_meet_the_real_support",errors[1]<2.5 and clearance[1]>7,"boy_grip_error=%.3f cheek_clearance=%.3f"%[errors[1],clearance[1]])
	evidence.ferry={"travel":node.body.position.distance_to(at),"maximum_sole_drift":drift,"grip_error":errors,"cheek_clearance":clearance,"contact_ticks":contacts}

static func run(g):
	recording=false; recorded_frames=0; cues=[]
	var checks=[]; var evidence={}
	await head_and_support_checks(g,checks,evidence)
	await authored_work_checks(g,checks,evidence)
	await authored_support_checks(g,checks,evidence)
	var report={"build":"0.4.4","all_passed":true,"checks":checks,"evidence":evidence,"physics_fps":Engine.physics_ticks_per_second,"method":"Native child controllers, actual Input and physical rigid ferry and synchronized animatable lift decks in isolated support fixtures; real authored cooperative pump geometry for hand reach and work release. No child positions or velocities are driven after each explicit setup. Intermediate head artwork is measured through the native renderer's angle selection. Recording is a bounded character study, not campaign traversal or artistic acceptance."}
	if "--record-character-v044" in OS.get_cmdline_user_args():
		report.recording=await record(g); report.recorded_frames=recorded_frames; report.fps=30
	for check in checks:
		if not check.passed: report.all_passed=false
	return report

static func beat(g,label,count,actions=[]):
	release()
	for action in actions: Input.action_press(action)
	caption=label; cues.append({"frame":recorded_frames,"label":label}); await tick(g,count)

static func record(g):
	frame_folder=g.report_path("character_v044_motion_frames"); DirAccess.make_dir_recursive_absolute(frame_folder)
	recorded_frames=0; cues=[]
	await prepare_attention(g); recording=true
	await beat(g,"QUIET ATTENTION",25)
	await beat(g,"STEP / HEAD LEADS",24,["right"])
	await beat(g,"ANTICIPATE / TURN THROUGH DRAWN ANGLES",28,["left"])
	await beat(g,"SETTLE / RETAIN THE PLANTED SOLE",25)
	recording=false; var pump=await Pump.prepare(g); Pump.start_work(g,pump)
	camera_follow=false; camera_center=Vector2(pump.x+15,pump.y-105); recording=true
	await beat(g,"REACH / SHARED LEVER CONTACT",75,["interact"])
	await beat(g,"RELEASE / WEIGHT SETTLES",35)
	recording=false; var crossing=await Crossing.prepare(g); await Crossing.approach(g,crossing); await Crossing.command(g,"companion"); await tick(g,35)
	camera_follow=false; camera_center=g.boy.position+Vector2(55,-100); recording=true
	await beat(g,"BRACE / WEIGHT ON THE RAIL",55)
	recording=false; await Crossing.command(g,"companion"); recording=true
	await beat(g,"CALL / LOOK / RELEASE THE HOLD",40,["left"])
	recording=false; var ferry=await Garden.prepare(g,true)
	if ferry!=null:
		camera_follow=true; recording=true
		await beat(g,"REAL FERRY / REEL / SOLES TRAVEL WITH THE DECK",120,["crouch","interact"])
		await beat(g,"BRAKE / RELEASE / KEEP THE SUPPORT",30,["crouch"])
	recording=false; release()
	return {"enabled":true,"frames":recorded_frames,"fps":30,"duration_seconds":recorded_frames/30.0,"frame_directory":frame_folder,"cues":cues,"scope":"Normal-speed native character attention/work study. Authored shelf, cooperative pump, physical counterweight cradle and genuine cranked rigid ferry with both children aboard; explicit initial placements and prepared progress for isolated visual fixtures. Actual Input drives movement, work and release. Setup/cuts excluded; no campaign completion or artistic acceptance claim."}

static func capture(g):
	await prepare_attention(g); Input.action_press("left"); await tick(g,12); release(); g.mode="pause"
	var hud_visible=g.hud.visible; g.hud.hide()
	g.chapter_card=0; g.message_time=0; g.camera.zoom=Vector2(2.65,2.65)
	g.camera.position=g.player.position+Vector2(0,-90)
	await g.get_tree().process_frame; g.camera.position=g.player.position+Vector2(0,-90)
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path("27_character_attention_study.png"))
	g.hud.visible=hud_visible
