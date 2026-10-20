extends SceneTree

# This harness instantiates the real child controller on an isolated collision
# fixture, outside the campaign. It does not grant progress or alter saves.
const Child=preload("res://scripts/child_v2.gd")
const BASE_X=100000.0

class Fixture extends Node2D:
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
	var player
	var boy
	var level={"ground":[],"platforms":[]}
	func in_water(_x,_y=700.0): return false
	func wind_speed_scale(_child): return 1.0
	func play_step(_p,_db): pass
	func spawn_dust(_p,_count): pass
	func surface_y_at(x,fallback=700.0):
		var local=x-100000.0
		if local<0 or local>2200: return fallback
		if local<1200: return 700.0
		if local<=1800: return 700.0-(local-1200)*.1
		return 640.0+(local-1800)*.15

func _initialize(): call_deferred("local_run")

func local_run():
	var report=await run(null)
	DirAccess.make_dir_recursive_absolute("res://evidence/v040/character")
	var file=FileAccess.open("res://evidence/v040/character/movement_checks.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")); file.close()
	print("MOVEMENT_CHECKS_RESULT ",JSON.stringify(report))
	quit(0 if report.all_passed else 1)

static func frames(tree,count):
	for i in range(count): await tree.physics_frame

static func release_input():
	for action in ["left","right","jump","crouch","sprint","interact"]: Input.action_release(action)

static func check(results,name,passed,details=""):
	results.append({"name":name,"passed":passed,"details":details})

static func place(fixture,x):
	var p=fixture.player
	p.position=Vector2(BASE_X+x,fixture.surface_y_at(BASE_X+x)-2)
	p.velocity=Vector2.ZERO; p.climbing=false; p.climb_clock=0; p.coyote=0; p.jump_buffer=0; p.leap_axis=0
	p.action_time=0; p.was_floor=false; p.moving_last=false; p.facing=1; p.last_direction=1; p.reset_feet()

static func jump_height(fixture,tree,hold_frames):
	release_input(); place(fixture,260); await frames(tree,8)
	var start=fixture.player.position.y
	var minimum=start
	Input.action_press("jump")
	for i in range(100):
		await tree.physics_frame
		minimum=minf(minimum,fixture.player.position.y)
		if i==hold_frames: Input.action_release("jump")
		if i>hold_frames+3 and fixture.player.is_on_floor(): break
	Input.action_release("jump")
	return start-minimum

static func add_collision(fixture,polygon):
	var body=StaticBody2D.new(); body.collision_layer=1; body.collision_mask=2
	var shape=CollisionPolygon2D.new(); shape.polygon=polygon; body.add_child(shape); fixture.add_child(body)

static func run(game):
	var tree=game.get_tree() if game!=null else Engine.get_main_loop()
	var original_mode=""
	if game!=null: original_mode=game.mode; game.mode="pause"
	var results=[]
	var fixture=Fixture.new(); tree.root.add_child(fixture)
	fixture.level.ground=[{"x":BASE_X,"y":700,"w":1200,"h":600},{"x":BASE_X+1200,"y":700,"w":1000,"h":600,"profile":[[0,0],[600,-60],[1000,0]]}]
	add_collision(fixture,PackedVector2Array([Vector2(BASE_X,700),Vector2(BASE_X+1200,700),Vector2(BASE_X+1800,640),Vector2(BASE_X+2200,700),Vector2(BASE_X+2200,1300),Vector2(BASE_X,1300)]))
	add_collision(fixture,PackedVector2Array([Vector2(BASE_X+680,580),Vector2(BASE_X+980,580),Vector2(BASE_X+980,622),Vector2(BASE_X+680,622)]))
	fixture.player=Child.new(); fixture.player.game=fixture; fixture.player.position=Vector2(BASE_X+180,698); fixture.add_child(fixture.player)
	fixture.boy=Child.new(); fixture.boy.game=fixture; fixture.boy.controlled=false; fixture.boy.is_girl=false; fixture.boy.position=Vector2(BASE_X+80,698); fixture.add_child(fixture.boy)
	# The campaign normally sets up these actions before running a test wrapper.
	for action in ["left","right","jump","crouch","sprint","interact"]:
		if not InputMap.has_action(action): InputMap.add_action(action)
	release_input(); await frames(tree,10)
	Input.action_press("right"); await frames(tree,10)
	check(results,"walk_reaches_cruise_in_ten_ticks",absf(fixture.player.velocity.x-166)<.1,str(fixture.player.velocity.x))
	var begin_stop=fixture.player.position.x
	Input.action_release("right")
	var stop_ticks=0
	while absf(fixture.player.velocity.x)>1 and stop_ticks<20:
		await tree.physics_frame; stop_ticks+=1
	check(results,"release_stops_within_eight_ticks",stop_ticks<=8 and fixture.player.position.x-begin_stop<14,"ticks=%d distance=%0.3f"%[stop_ticks,fixture.player.position.x-begin_stop])
	await frames(tree,18)
	var settled=[fixture.player.position+fixture.player.feet[0],fixture.player.position+fixture.player.feet[1]]
	await frames(tree,20)
	var idle_drift=maxf(settled[0].distance_to(fixture.player.position+fixture.player.feet[0]),settled[1].distance_to(fixture.player.position+fixture.player.feet[1]))
	check(results,"idle_support_feet_do_not_slide",idle_drift<.01,str(idle_drift))
	Input.action_press("right"); await frames(tree,10); Input.action_release("right"); Input.action_press("left"); await frames(tree,1)
	check(results,"reversal_brakes_before_pivot",fixture.player.velocity.x>0 and fixture.player.facing>0,str(fixture.player.velocity.x))
	await frames(tree,7)
	check(results,"reversal_responds_within_eight_ticks",fixture.player.velocity.x<0 and fixture.player.facing<0,str(fixture.player.velocity.x))
	release_input(); await frames(tree,12)
	Input.action_press("crouch"); await frames(tree,1)
	check(results,"crouch_enters_without_height_pop",fixture.player.col.shape.size.y>74 and fixture.player.col.shape.size.y<99,str(fixture.player.col.shape.size.y))
	await frames(tree,10)
	check(results,"crouch_reaches_low_pose",absf(fixture.player.crouch_blend-1)<.01 and absf(fixture.player.col.position.y+fixture.player.col.shape.size.y/2)<.01)
	place(fixture,720); await frames(tree,8); Input.action_release("crouch"); await frames(tree,15)
	check(results,"ceiling_keeps_low_clearance",fixture.player.crouching and fixture.player.col.shape.size.y<74.1,str(fixture.player.col.shape.size.y))
	Input.action_press("right"); await frames(tree,280); Input.action_release("right")
	check(results,"standing_returns_after_clearance",fixture.player.position.x>BASE_X+1000 and fixture.player.col.shape.size.y>98.9,str(fixture.player.position.x-BASE_X))
	var full=await jump_height(fixture,tree,28)
	var short=await jump_height(fixture,tree,3)
	check(results,"jump_release_controls_apex",full>80 and short>25 and short<full*.82,"held=%0.3f short=%0.3f"%[full,short])
	place(fixture,1300); await frames(tree,10); Input.action_press("right")
	var maximum_y=0.0; var maximum_x_drift=0.0; var count=0; var last=[]; var last_phases=[]
	for i in range(170):
		await tree.physics_frame
		var current=[]
		for side in range(2):
			var contact=fixture.player.position+fixture.player.feet[side]; current.append(contact)
			if fixture.player.is_on_floor() and fixture.player.foot_phase[side]<.5:
				maximum_y=maxf(maximum_y,absf(contact.y-fixture.surface_y_at(contact.x,contact.y))); count+=1
				if last.size()==2 and last_phases[side]<.5 and absf(last_phases[side]-fixture.player.foot_phase[side])<.15: maximum_x_drift=maxf(maximum_x_drift,absf(contact.x-last[side].x))
		last=current; last_phases=fixture.player.foot_phase.duplicate()
	Input.action_release("right")
	check(results,"slope_stance_follows_collision_profile",count>100 and maximum_y<2,"samples=%d max_y=%0.5f"%[count,maximum_y])
	check(results,"slope_stance_stays_planted",maximum_x_drift<.01,"max_x=%0.5f"%maximum_x_drift)
	place(fixture,2170); await frames(tree,8); Input.action_press("right")
	for i in range(30):
		await tree.physics_frame
		if not fixture.player.is_on_floor(): break
	await frames(tree,3)
	var late_before={"coyote":fixture.player.coyote,"x":fixture.player.position.x-BASE_X,"y":fixture.player.position.y,"floor":fixture.player.is_on_floor(),"held":Input.is_action_pressed("jump")}
	Input.action_press("jump"); await frames(tree,2)
	check(results,"coyote_jump_after_leaving_edge",fixture.player.velocity.y< -400,JSON.stringify({"before":late_before,"velocity_y":fixture.player.velocity.y,"coyote":fixture.player.coyote,"buffer":fixture.player.jump_buffer}))
	release_input(); fixture.queue_free(); await tree.process_frame
	if game!=null: game.mode=original_mode
	var passed=true
	for result in results:
		if not result.passed: passed=false
	return {"build":"0.4.0","all_passed":passed,"checks":results,"method":"Real child_v2 controller and native collisions in an isolated flat, overhead-clearance and graded-ground fixture. Input drives acceleration, stopping, reversing, crouching, both jump heights, slope stance and coyote jump. Scenario placement does not claim campaign traversal."}
