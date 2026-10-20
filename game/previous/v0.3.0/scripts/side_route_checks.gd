extends RefCounted

# Targeted reachability fixtures complement the uninterrupted campaign test.
# Set-up changes are explicit below. After the initial placement, navigation,
# jumping, companion following, landing and searching use native game physics.
static func run(game):
	game.test_log=[]
	var results=[]
	var count=0
	for chapter_index in range(game.levels.size()):
		var optional_caches=[]
		for source in game.levels[chapter_index].interact:
			if source.kind=="cache" and source.get("route","")=="raised_supply_spur":
				optional_caches.append(source.duplicate(true))
		for target in optional_caches:
			count+=1
			_release_inputs()
			game.flags={}; game.cache_remaining={}
			# This fixture tests the optional climb, not earlier mandatory puzzles.
			for gate in game.levels[chapter_index].gates:
				if float(gate.x)<float(target.x): game.flags[gate.key]=true
			for bridge in game.levels[chapter_index].get("bridges",[]):
				if float(bridge.x)<float(target.x): game.flags[bridge.key]=true
			game.load_chapter(chapter_index,false)
			game.level=game.level.duplicate(true)
			game.level.hazard_lanes=[]
			game.level.erase("danger")
			game.level.searchlight=false
			game.mode="playing"; game.journey_active=true
			game.rations=0; game.scrap=0; game.medicine=0
			game.health=100; game.warmth=100; game.food=100; game.stamina=100
			game.wetness=0; game.pending_action={}; game.action_progress=0
			game.shell_clock=0; game.shell_warning=0; game.exposure=0
			var start_x=float(target.x)-410.0
			game.player.position=Vector2(start_x,game.surface_y_at(start_x,700)-2)
			game.boy.position=Vector2(start_x-52,game.surface_y_at(start_x-52,700)-2)
			game.player.velocity=Vector2.ZERO; game.boy.velocity=Vector2.ZERO
			game.player.reset_feet(); game.boy.reset_feet(); game.boy.following=true
			game.trail.clear()
			var initial_girl=game.player.position
			var initial_boy=game.boy.position
			var minimum_girl_y=game.player.position.y
			var minimum_boy_y=game.boy.position.y
			var landed=false
			var searched=false
			var boy_arrived=false
			var jump_hold=0
			var jump_count=0
			var frames=0
			var landing_frame=-1
			var search_frame=-1
			var failure=""
			# Let the newly created collision bodies settle before the approach.
			for settle in range(12): await game.get_tree().physics_frame
			for frame in range(1080):
				await game.get_tree().physics_frame
				frames=frame+1
				minimum_girl_y=minf(minimum_girl_y,game.player.position.y)
				minimum_boy_y=minf(minimum_boy_y,game.boy.position.y)
				if game.mode!="playing":
					failure="unexpected mode during native climb: "+str(game.mode)
					break
				Input.action_release("left"); Input.action_release("right")
				Input.action_release("sprint"); Input.action_release("crouch")
				if jump_hold>0:
					jump_hold-=1
					if jump_hold==0: Input.action_release("jump")
				var at_cache=absf(game.player.position.x-float(target.x))<=18.0 and absf(game.player.position.y-float(target.y))<=20.0 and game.player.is_on_floor()
				if at_cache:
					if not landed: landing_frame=frame
					landed=true
					game.update_prompt()
					if not searched and not game.near_item.is_empty() and game.near_item.get("id","")==target.id:
						Input.action_press("interact")
						game.interact()
				else:
					if not searched: Input.action_release("interact")
					if game.player.position.x<float(target.x)-12:
						Input.action_press("right")
					elif game.player.position.x>float(target.x)+18:
						Input.action_press("left")
					# Authored steps drive the same input-level jump decisions used
					# by a player, with a full held jump rather than a position snap.
					if game.player.is_on_floor() and jump_hold==0 and game.player.position.x<float(target.x)-12:
						var need_jump=not game.ground_at(game.player.position.x+30)
						for platform in game.level.platforms:
							var ahead=float(platform.x)-game.player.position.x
							var rise=game.player.position.y-float(platform.y)
							if ahead>0 and ahead<55 and rise>12 and rise<145: need_jump=true
						if need_jump:
							Input.action_press("jump"); jump_hold=24; jump_count+=1
				if game.flags.get(target.id,false):
					if not searched: search_frame=frame
					searched=true; Input.action_release("interact")
				if absf(game.boy.position.x-float(target.x))<100 and absf(game.boy.position.y-float(target.y))<24 and game.boy.is_on_floor(): boy_arrived=true
				if searched and boy_arrived: break
			_release_inputs()
			if failure.is_empty() and not landed: failure="no grounded landing at the cache height within 18 simulated seconds"
			elif failure.is_empty() and not searched: failure="landed, but the actual held cache search did not finish"
			elif failure.is_empty() and not boy_arrived: failure="cache searched, but companion did not reach the raised route"
			var detail={"chapter":chapter_index+1,"id":target.id,"target":_vector(Vector2(target.x,target.y)),"initial_girl":_vector(initial_girl),"initial_boy":_vector(initial_boy),"final_girl":_vector(game.player.position),"final_boy":_vector(game.boy.position),"girl_velocity":_vector(game.player.velocity),"boy_velocity":_vector(game.boy.velocity),"girl_on_floor":game.player.is_on_floor(),"boy_on_floor":game.boy.is_on_floor(),"girl_minimum_y":minimum_girl_y,"boy_minimum_y":minimum_boy_y,"landed_at_cache":landed,"searched":searched,"boy_arrived":boy_arrived,"jump_inputs":jump_count,"frames":frames,"simulated_seconds":frames/60.0,"landing_frame":landing_frame,"search_frame":search_frame,"failure":failure}
			results.append(detail)
			game.assert_check(str(target.id)+"_native_climb_and_held_search",landed and searched,JSON.stringify(detail))
			game.assert_check(str(target.id)+"_companion_follows_raised_route",boy_arrived,JSON.stringify(detail))
			print("SIDE_ROUTE_RESULT ",JSON.stringify(detail))
	game.assert_check("all_six_authored_supply_spurs_exercised",count==6,str(count))
	var passed=true
	for check in game.test_log:
		if not check.passed: passed=false
	var report={"build":"0.3.0","all_passed":passed,"checks":game.test_log,"routes":results,"method":"Targeted native Godot physics fixtures. Each route starts both children once on authored ground 410 pixels before its raised cache. Prior gates are explicitly unlocked and timed dangers are disabled to isolate the climb. After set-up there are no position changes, collision edits, forced jump velocities or resource grants. Native Input actions drive the climb and full held search; the existing companion AI must follow. This does not replace the continuous campaign test."}
	var file=FileAccess.open(game.report_path("side_route_checks.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")); file.close()
	print("SIDE_ROUTES_COMPLETE ",JSON.stringify({"all_passed":passed,"routes":count,"checks":game.test_log.size()}))
	game.call_deferred("quit_game",0 if passed else 1)


static func _release_inputs():
	for action in ["left","right","jump","sprint","crouch","interact"]: Input.action_release(action)


static func _vector(value):
	return {"x":value.x,"y":value.y}
