extends RefCounted
static var cutoff_frame=0
static var recording=false
static var recorded_frames=0
static var recording_folder=""

static func tick(g):
	await g.get_tree().physics_frame
	if recording:
		await RenderingServer.frame_post_draw
		var frame=g.get_viewport().get_texture().get_image()
		frame.save_jpg(recording_folder.path_join("%05d.jpg"%recorded_frames),.88)
		recorded_frames+=1

# The mill is exercised through contact, character weight, native rigid-body
# travel and Input navigation. These fixtures never press E at the machinery.
static func release_inputs():
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)

static func point(p): return {"x":p.x,"y":p.y}

static func add(results,name,passed,details=""):
	results.append({"check":name,"passed":passed,"details":details})

static func prepare(g,index,data,boy_at_risk=false):
	recording=false
	release_inputs(); g.flags={}; g.cache_remaining={}
	# Earlier campaign puzzles are outside this bounded physical encounter.
	# The mill's own key is deliberately absent throughout initial set-up.
	for gate in g.levels[index].gates:
		if float(gate.x)<float(data.bridge_x): g.flags[gate.key]=true
	for bridge in g.levels[index].get("bridges",[]):
		if float(bridge.x)<float(data.bridge_x): g.flags[bridge.key]=true
	g.load_chapter(index,false); g.level=g.level.duplicate(true)
	g.level.hazard_lanes=[]; g.level.erase("danger"); g.level.searchlight=false
	g.mode="playing"; g.health=100; g.food=100; g.warmth=100; g.stamina=100; g.wetness=0; g.invulnerable=0
	g.rations=0; g.scrap=0; g.medicine=0; g.trail.clear(); g.pending_action={}; g.action_progress=0
	var start=float(data.bridge_x)-140 if not boy_at_risk else 16270.0
	g.player.position=Vector2(start,g.surface_y_at(start,700)-2)
	var boy_x=float(data.wheel_x)+float(data.radius)+180 if boy_at_risk else start-52
	g.boy.position=Vector2(boy_x,g.surface_y_at(boy_x,700)-2)
	g.player.velocity=Vector2.ZERO; g.boy.velocity=Vector2.ZERO; g.player.reset_feet(); g.boy.reset_feet(); g.boy.following=not boy_at_risk
	for frame in range(12): await tick(g)
	cutoff_frame=Engine.get_physics_frames()+3600
	for node in g.mill_encounters:
		if node.data.id==data.id: return node
	return null

static func navigate(g,target_x,target_y,climb,require_boy,max_frames):
	var jump_hold=0; var jumps=0; var complete=false; var frames=0
	for frame in range(max_frames):
		await tick(g); frames=frame+1
		if g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
		Input.action_release("left"); Input.action_release("right"); Input.action_release("sprint"); Input.action_release("crouch")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var at_target=absf(g.player.position.x-target_x)<14 and g.player.is_on_floor() and (target_y==INF or absf(g.player.position.y-target_y)<24)
		var boy_target=absf(g.boy.position.x-target_x)<100 and g.boy.is_on_floor() and (target_y==INF or absf(g.boy.position.y-target_y)<24)
		if at_target and (boy_target or not require_boy): complete=true; break
		if not at_target:
			if g.player.position.x<target_x-10: Input.action_press("right")
			elif g.player.position.x>target_x+14: Input.action_press("left")
		if require_boy and absf(g.player.position.x-g.boy.position.x)>130 and absf(g.player.position.y-g.boy.position.y)<30: Input.action_release("right")
		if climb and g.player.is_on_floor() and jump_hold==0 and not at_target:
			for p in g.level.platforms:
				var ahead=float(p.x)-g.player.position.x; var rise=g.player.position.y-float(p.y)
				if ahead>0 and ahead<55 and rise>12 and rise<145:
					Input.action_press("jump"); jump_hold=24; jumps+=1; break
	release_inputs()
	return {"reached":complete,"frames":frames,"jump_inputs":jumps,"girl":point(g.player.position),"boy":point(g.boy.position),"mode":g.mode}

static func on_wheel(child,node):
	if not child.is_on_floor(): return false
	for collision in range(child.get_slide_collision_count()):
		if child.get_slide_collision(collision).get_collider()==node.wheel: return true
	return false

static func stand_on_wheel(g,node):
	release_inputs(); Input.action_press("right"); Input.action_press("jump")
	var girl_contact=false; var boy_contact=false; var warning=false; var loading=false; var frames=0
	var premature_travel=0.0
	for frame in range(360):
		await tick(g); frames=frame+1
		if g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
		if frame==24: Input.action_release("jump")
		# Full held jump from the second tread reaches the circular crown. A
		# short coast stops the girl on its top rather than walking off the rim.
		if g.player.position.x>float(node.data.wheel_x)-30: Input.action_release("right")
		girl_contact=girl_contact or on_wheel(g.player,node); boy_contact=boy_contact or on_wheel(g.boy,node)
		loading=loading or node.state=="loading"
		if node.state=="warning": warning=true; break
		premature_travel=maxf(premature_travel,float(node.travel))
	release_inputs()
	return {"warning":warning,"loading":loading,"girl_contact":girl_contact,"boy_contact":boy_contact,"frames":frames,"travel_before_warning":premature_travel,"girl":point(g.player.position),"boy":point(g.boy.position),"state":node.state}

static func retreat(g,node,require_boy):
	var target=float(node.data.wheel_x)-190
	var safe_x=float(node.data.wheel_x)-float(node.data.radius)-34
	var safe_before_release=false; var complete=false; var frames=0
	Input.action_press("left")
	for frame in range(300):
		await tick(g); frames=frame+1
		if g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
		if g.player.position.x<safe_x and (g.boy.position.x<safe_x or not require_boy) and node.state in ["loading","warning"]: safe_before_release=true
		if g.player.position.x<target+12 and (g.boy.position.x<safe_x or not require_boy): complete=true; break
	release_inputs()
	return {"reached":complete,"safe_before_release":safe_before_release,"frames":frames,"girl":point(g.player.position),"boy":point(g.boy.position),"state":node.state,"travel":node.travel}

static func approach_stairs(g,data,require_boy):
	var steps=[]
	for platform in g.level.platforms:
		if float(platform.x)>float(data.bridge_x)+float(data.bridge_w) and float(platform.x)<float(data.wheel_x) and float(platform.y)<650:
			steps.append(platform)
	steps.sort_custom(func(a,b): return float(a.x)<float(b.x))
	var legs=[]
	var complete=steps.size()>=2
	for step in steps:
		# The circular rim overlaps the last tread; stop before its genuine side
		# collision and jump onto the crown instead of demanding a walk through it.
		var leg=await navigate(g,float(step.x)+float(step.w)-35,float(step.y),true,require_boy,720)
		legs.append(leg); complete=complete and leg.reached
		if not leg.reached: break
	return {"reached":complete,"legs":legs}

static func run(g):
	recording=false; recorded_frames=0; recording_folder=""
	var checks=[]; var evidence={}
	var chapter=-1; var data={}
	for index in range(g.levels.size()):
		for item in g.levels[index].get("mechanisms",[]):
			if item.kind=="breakaway_mill": chapter=index; data=item; break
	if chapter<0: return {"build":"0.4.0","all_passed":false,"checks":[{"check":"mill_authored","passed":false}],"failure":"No authored breakaway mill found."}
	var node=await prepare(g,chapter,data)
	if node==null: return {"build":"0.4.0","all_passed":false,"checks":[{"check":"mill_native_component_created","passed":false}],"failure":"No instantiated mill component."}
	var wants_record="--record-mill" in OS.get_cmdline_user_args()
	if wants_record:
		recording_folder=g.report_path("motion_frames"); DirAccess.make_dir_recursive_absolute(recording_folder)
		g.chapter_card=0; g.message_time=0; recording=true
	evidence["initial"]={"girl":point(g.player.position),"boy":point(g.boy.position),"wheel":point(node.wheel.position),"state":node.state}
	add(checks,"mill_starts_physically_locked",node.wheel.freeze and node.state=="locked" and node.gate_body.collision_layer!=0 and not g.flags.get(data.key,false))
	var bridge_girl=0; var bridge_boy=0; var bridge_complete=false
	Input.action_press("right")
	for frame in range(360):
		await tick(g)
		if g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
		for child in [g.player,g.boy]:
			if child.position.x>float(data.bridge_x)+12 and child.position.x<float(data.bridge_x)+float(data.bridge_w)-12 and child.is_on_floor() and absf(child.position.y-float(data.bridge_y))<2:
				if child==g.player: bridge_girl+=1
				else: bridge_boy+=1
		if g.player.position.x>float(data.bridge_x)+float(data.bridge_w)+80 and g.boy.position.x>float(data.bridge_x)+float(data.bridge_w)+20: bridge_complete=true; break
	release_inputs()
	add(checks,"both_children_walk_on_real_bridge_deck",bridge_complete and bridge_girl>25 and bridge_boy>25,"girl_floor_frames=%d boy_floor_frames=%d"%[bridge_girl,bridge_boy])
	evidence["stairs"]=await approach_stairs(g,data,true)
	add(checks,"both_children_physically_climb_mill_steps",evidence.stairs.reached,JSON.stringify(evidence.stairs))
	add(checks,"gate_stays_closed_before_wheel_weight",not g.flags.get(data.key,false) and node.gate_lift<1 and node.travel<1)
	evidence["weight_contact"]=await stand_on_wheel(g,node) if evidence.stairs.reached else {"warning":false,"girl_contact":false}
	add(checks,"standing_on_actual_wheel_triggers_warning",evidence.weight_contact.warning and evidence.weight_contact.girl_contact,JSON.stringify(evidence.weight_contact))
	evidence["retreat"]=await retreat(g,node,true) if evidence.weight_contact.warning else {"reached":false,"safe_before_release":false}
	add(checks,"both_children_retreat_before_wheel_releases",evidence.retreat.reached and evidence.retreat.safe_before_release,JSON.stringify(evidence.retreat))
	var opened=false; var premature=false
	if evidence.retreat.reached:
		for frame in range(900):
			await tick(g)
			if g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
			if g.flags.get(data.key,false) and float(node.travel)<float(data.travel_required)-.5: premature=true
			if g.flags.get(data.key,false) and node.gate_lift>=float(data.gate_h)-1: opened=true; break
	var real_travel=node.wheel.position.x-float(data.wheel_x)
	add(checks,"native_rigid_wheel_rolls_required_distance",opened and real_travel>=float(data.travel_required)-.5 and absf(node.wheel.rotation)>.2,"dx=%0.3f rotation=%0.3f"%[real_travel,node.wheel.rotation])
	add(checks,"chain_gate_opens_after_real_travel",opened and not premature and node.gate_lift>=float(data.gate_h)-1,"travel=%0.3f lift=%0.3f"%[node.travel,node.gate_lift])
	evidence["gate_crossing"]=await navigate(g,float(data.exit_x),INF,false,true,1500) if opened else {"reached":false}
	recording=false
	add(checks,"both_children_cross_opened_mill_gate",evidence.gate_crossing.reached and g.player.position.x>float(data.gate_x)+50 and g.boy.position.x>float(data.gate_x)+50,JSON.stringify(evidence.gate_crossing))
	add(checks,"safe_route_preserves_both_children",g.health>99.9 and g.mode=="playing",str(g.health))
	evidence["physical_result"]={"wheel_travel":real_travel,"gate_lift":node.gate_lift,"health":g.health,"hit_children":node.hit_children}
	# Modal screens must suspend native rigid motion as well as the children.
	# Wait two boundary ticks for freeze to reach PhysicsServer before measuring.
	var pause_results=[]
	if opened and is_instance_valid(node.wheel):
		for modal in ["pause","inventory"]:
			g.mode=modal
			for frame in range(2): await tick(g)
			var anchor=node.wheel.position
			for frame in range(30): await tick(g)
			var drift=node.wheel.position.distance_to(anchor)
			add(checks,"moving_wheel_freezes_in_"+modal,node.wheel.freeze and drift<.1,str(drift))
			g.mode="playing"
			var resume_from=node.wheel.position
			for frame in range(30): await tick(g)
			var resumed=node.wheel.position.x-resume_from.x
			add(checks,"moving_wheel_resumes_after_"+modal,not node.wheel.freeze and resumed>20,str(resumed))
			pause_results.append({"mode":modal,"paused_drift":drift,"resumed_x":resumed})
	else:
		for modal in ["pause","inventory"]:
			add(checks,"moving_wheel_freezes_in_"+modal,false,"No actual rolling wheel was available.")
			add(checks,"moving_wheel_resumes_after_"+modal,false,"No actual rolling wheel was available.")
	evidence["modal_motion"]=pause_results
	# Separate targeted hazard scenario: the boy starts waiting in the wheel's
	# eventual path. The girl repeats the actual climb/weight/retreat sequence;
	# the rigid wheel receives no fixture velocity, impulse or state assignment.
	node=await prepare(g,chapter,data,true)
	evidence["risk_initial"]={"girl":point(g.player.position),"boy":point(g.boy.position)}
	var risk_steps=await approach_stairs(g,data,false)
	var risk_contact=await stand_on_wheel(g,node) if risk_steps.reached else {"warning":false}
	var risk_retreat=await retreat(g,node,false) if risk_contact.warning else {"reached":false}
	if risk_retreat.reached:
		for frame in range(900):
			await tick(g)
			if not node.hit_children.is_empty() or g.mode!="playing" or Engine.get_physics_frames()>=cutoff_frame: break
	var hit_boy=false; var hit_girl=false
	for child in node.hit_children:
		if "boy" in str(child).to_lower(): hit_boy=true
		if "girl" in str(child).to_lower(): hit_girl=true
	add(checks,"moving_wheel_can_hit_waiting_boy",risk_retreat.reached and hit_boy and g.health<100,"victims=%s health=%0.3f"%[str(node.hit_children),g.health])
	add(checks,"clear_girl_does_not_hide_boy_wheel_risk",hit_boy and not hit_girl and g.player.position.x<float(data.wheel_x)-float(data.radius)-30,JSON.stringify({"girl":point(g.player.position),"boy":point(g.boy.position)}))
	evidence["boy_risk"]={"steps":risk_steps,"contact":risk_contact,"retreat":risk_retreat,"hits":node.hit_children,"health":g.health,"travel":node.travel}
	release_inputs()
	var passed=true
	for check in checks:
		if not check.passed: passed=false
	var movie={"enabled":wants_record,"frames":recorded_frames,"fps":30,"duration_seconds":recorded_frames/30.0,"scope":"Safe Input-driven native mill playthrough, starting after explicit initial fixture setup and ending when both children have physically crossed the gate. Preparation, modal suspension checks and the separate boy-risk fixture are excluded.","frame_directory":recording_folder}
	var report={"build":"0.4.0","all_passed":passed,"checks":checks,"evidence":evidence,"recording":movie,"method":"Native physical mill fixtures. Only initial actor/resource state and earlier campaign gates are prepared; unrelated timed dangers are disabled. Actual Input walks the collision bridge, jumps the stairs and circular wheel, stands on it to load the breakaway support, and retreats before physical rolling. No E interactions, actor repositioning after setup, forced wheel velocity/state, mechanism progress flags, damage immunity or resource grants drive the encounter. Real wheel translation/rotation and chain lift must open a collision gate, then both children physically cross. A separate repeat leaves the boy waiting ahead to test actual moving-wheel harm to either child. Every navigation/wait has a hard frame bound."}
	print("MILL_CHECKS_RESULT ",JSON.stringify(report))
	return report
