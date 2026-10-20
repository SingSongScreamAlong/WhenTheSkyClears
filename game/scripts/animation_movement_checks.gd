extends SceneTree

const Child=preload("res://scripts/child_v2.gd")
const Basic=preload("res://scripts/movement_checks.gd")
const ORIGIN=100000.0

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
	var steps=0
	var level={"ground":[],"platforms":[]}
	func in_water(_x,_y=700.0): return false
	func wind_speed_scale(_child): return 1.0
	func play_step(_p,_db): steps+=1
	func spawn_dust(_p,_count): pass
	func surface_y_at(x,fallback=700.0):
		var ray=PhysicsRayQueryParameters2D.create(Vector2(x,fallback-36),Vector2(x,fallback+41),1)
		var hit=get_world_2d().direct_space_state.intersect_ray(ray)
		return hit.position.y if not hit.is_empty() else fallback

func _initialize(): call_deferred("run")

func ticks(count):
	for i in range(count): await physics_frame

func place(child,x,y=698.0):
	child.position=Vector2(ORIGIN+x,y); child.velocity=Vector2.ZERO
	child.climbing=false; child.climb_clock=0; child.coyote=0; child.jump_buffer=0
	child.action_time=0; child.hit_time=0; child.leap_axis=0; child.ai_axis=0
	child.ai_jump=false; child.was_floor=false; child.moving_last=false; child.reset_feet()

func run():
	var basic=await Basic.run(null)
	var checks=basic.checks
	var fixture=Fixture.new(); root.add_child(fixture)
	Basic.add_collision(fixture,PackedVector2Array([Vector2(ORIGIN,700),Vector2(ORIGIN+4000,700),Vector2(ORIGIN+4000,1400),Vector2(ORIGIN,1400)]))
	fixture.player=Child.new(); fixture.player.game=fixture; fixture.player.position=Vector2(ORIGIN+300,698); fixture.add_child(fixture.player)
	fixture.boy=Child.new(); fixture.boy.game=fixture; fixture.boy.is_girl=false; fixture.boy.controlled=false; fixture.boy.position=Vector2(ORIGIN+180,698); fixture.add_child(fixture.boy)
	await ticks(10)
	for child in [fixture.player,fixture.boy]:
		fixture.player.controlled=false; fixture.boy.controlled=false; child.controlled=true
		Basic.release_input(); place(child,450); await ticks(10)
		var maximum_reach=0.0; var drift=0.0; var count=0; var previous=[]; var previous_phase=[]
		var scale_body=1.0 if child.is_girl else .84
		for segment in range(3):
			Basic.release_input(); Input.action_press("right" if segment<2 else "left")
			if segment==1: Input.action_press("sprint")
			for frame in range(110):
				await physics_frame
				var pose=child.body_pose(); var current=[]
				for side in range(2):
					var contact=child.position+child.feet[side]*scale_body; current.append(contact)
					maximum_reach=maxf(maximum_reach,(pose.hip+Vector2(-2 if side==0 else 2,0)).distance_to(child.feet[side]))
					var stance=.42 if absf(child.velocity.x)>220 else .5
					if previous.size()==2 and child.foot_phase[side]<stance and previous_phase[side]<stance and absf(previous_phase[side]-child.foot_phase[side])<.15 and frame>12:
						drift=maxf(drift,absf(contact.x-previous[side].x)); count+=1
				previous=current; previous_phase=child.foot_phase.duplicate()
		var label="girl" if child.is_girl else "boy"
		Basic.check(checks,label+"_walk_run_reverse_constant_leg_reach",maximum_reach<=52.5,"max=%0.4f pixels, authored leg=52.5"%maximum_reach)
		Basic.check(checks,label+"_stance_stays_planted_in_both_directions",count>100 and drift<.02,"samples=%d max_drift=%0.5f"%[count,drift])
		Basic.release_input(); await ticks(30)
		child.action_time=.6; child.hit_time=.4; child.land_time=.24
		fixture.mode="pause"
		var snapshot=[child.anim_time,child.action_time,child.hit_time,child.land_time,child.body_lean,child.cloth_drag]
		await ticks(35)
		var after=[child.anim_time,child.action_time,child.hit_time,child.land_time,child.body_lean,child.cloth_drag]
		Basic.check(checks,label+"_pause_freezes_pose_and_action_timers",snapshot==after)
		fixture.mode="playing"; child.action_time=0; child.hit_time=0

	fixture.player.controlled=true; fixture.boy.controlled=false
	Basic.release_input(); place(fixture.player,350); await ticks(10)
	fixture.player.action_time=.8; fixture.player.jump_buffer=.14
	Input.action_press("jump"); Input.action_press("right"); Input.action_press("sprint")
	var before_work=fixture.player.position; var before_stamina=fixture.stamina
	await ticks(20)
	Basic.check(checks,"held_work_cannot_execute_buffered_jump",fixture.player.is_on_floor() and fixture.player.position.distance_to(before_work)<.1 and fixture.player.jump_buffer<=0,str(fixture.player.velocity))
	Basic.check(checks,"held_work_does_not_spend_running_stamina",absf(fixture.stamina-before_stamina)<.001)
	Basic.release_input(); fixture.player.action_time=0; await ticks(35); fixture.pending_action={"kind":"pump"}
	fixture.player.action_time=1; await ticks(1)
	Basic.check(checks,"work_pose_eases_in",fixture.player.work_blend>0 and fixture.player.work_blend<.5,str(fixture.player.work_blend))
	await ticks(16); fixture.player.action_time=0; await ticks(1)
	Basic.check(checks,"work_pose_eases_out",fixture.player.work_blend>.3 and fixture.player.work_blend<1,str(fixture.player.work_blend))
	fixture.pending_action={}; await ticks(30)

	Basic.add_collision(fixture,PackedVector2Array([Vector2(ORIGIN+2200,350),Vector2(ORIGIN+2240,350),Vector2(ORIGIN+2240,700),Vector2(ORIGIN+2200,700)]))
	place(fixture.player,2187); await ticks(10)
	Input.action_press("right"); Input.action_press("sprint"); await ticks(8)
	var blocked_stamina=fixture.stamina; var blocked_steps=fixture.steps; var blocked_x=fixture.player.position.x
	await ticks(45)
	Basic.check(checks,"wall_pressure_does_not_spend_running_stamina",absf(fixture.stamina-blocked_stamina)<.001,str(fixture.stamina-blocked_stamina))
	Basic.check(checks,"wall_pressure_does_not_cycle_footsteps",fixture.steps==blocked_steps and absf(fixture.player.position.x-blocked_x)<.05)

	# A tap shortly before touching down remains a short jump. Holding the same
	# buffered input must still produce a full jump, through native collision.
	var buffered_heights=[]
	for release_tap in [false,true]:
		Basic.release_input(); place(fixture.player,350,668); fixture.player.velocity.y=280; await ticks(2)
		# Teleport setup must not inherit the previous fixture's floor contact.
		fixture.player.coyote=0
		Input.action_press("jump"); await ticks(1)
		if release_tap: Input.action_release("jump")
		var launched=false; var minimum=700.0
		for frame in range(90):
			await physics_frame
			if fixture.player.velocity.y< -100: launched=true
			if launched: minimum=minf(minimum,fixture.player.position.y)
			if launched and fixture.player.is_on_floor(): break
		buffered_heights.append(700-minimum if launched else 0)
	Basic.release_input()
	Basic.check(checks,"buffered_jump_preserves_tap_height",buffered_heights[0]>80 and buffered_heights[1]>15 and buffered_heights[1]<buffered_heights[0]*.75,str(buffered_heights))

	# A full-height wall with a roof above its ledge must not start an automatic
	# mantle into a blocked standing volume.
	Basic.add_collision(fixture,PackedVector2Array([Vector2(ORIGIN+2600,635),Vector2(ORIGIN+2800,635),Vector2(ORIGIN+2800,700),Vector2(ORIGIN+2600,700)]))
	Basic.add_collision(fixture,PackedVector2Array([Vector2(ORIGIN+2600,500),Vector2(ORIGIN+2800,500),Vector2(ORIGIN+2800,570),Vector2(ORIGIN+2600,570)]))
	fixture.level.platforms=[{"x":ORIGIN+2600,"y":635,"w":200,"h":65}]
	place(fixture.player,2588,670); fixture.player.velocity.y=50
	var mantles=fixture.player.mantle_count
	Input.action_press("right"); await ticks(16); Basic.release_input()
	Basic.check(checks,"blocked_mantle_does_not_start",fixture.player.mantle_count==mantles)

	var passed=true
	for check in checks:
		if not check.passed: passed=false
	var report={"all_passed":passed,"checks":checks,"physics_fps":Engine.physics_ticks_per_second,"method":"Real child controllers, native collision, and input in isolated fixtures. Both children walk, run and reverse; tests measure planted ankles and anatomical reach, pause, work, stamina, buffered tap/held jumps and blocked mantles. Campaign traversal and artistic acceptance are separate."}
	var args=OS.get_cmdline_user_args(); var idx=args.find("--evidence-dir")
	var output=args[idx+1] if idx>=0 and idx+1<args.size() else "res://evidence/v040/animation_movement"
	DirAccess.make_dir_recursive_absolute(output)
	var file=FileAccess.open(output+"/movement_checks.json",FileAccess.WRITE); file.store_string(JSON.stringify(report,"\t")); file.close()
	print("ANIMATION_MOVEMENT_RESULT ",JSON.stringify(report))
	fixture.queue_free(); await process_frame
	quit(0 if passed else 1)
