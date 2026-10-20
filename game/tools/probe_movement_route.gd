extends SceneTree

func _initialize(): call_deferred("run")

func run():
	var game=load("res://scripts/game.gd").new(); root.add_child(game)
	game.smoke_test=true; game.load_chapter(4,false); game.mode="playing"
	game.player.position=Vector2(3400,698); game.boy.position=Vector2(3346,698)
	game.player.reset_feet(); game.boy.reset_feet(); game.health=100; game.warmth=100; game.food=100
	var jump_hold=0
	var gap_leap=false
	for frame in range(1000):
		await physics_frame
		Input.action_press("right"); Input.action_release("sprint")
		if jump_hold>0:
			jump_hold-=1
			if jump_hold==0: Input.action_release("jump")
		var need_jump=false
		if game.player.is_on_floor():
			if not game.ground_at(game.player.position.x+30): need_jump=true; gap_leap=true; Input.action_press("sprint")
			for platform in game.level.platforms:
				if platform.x-game.player.position.x>0 and platform.x-game.player.position.x<45 and platform.y<game.player.position.y-12 and platform.y>game.player.position.y-145: need_jump=true
		if need_jump and jump_hold==0: Input.action_press("jump"); jump_hold=24
		if gap_leap and not game.player.is_on_floor(): Input.action_press("sprint")
		if absf(game.player.position.x-game.boy.position.x)>155: Input.action_release("right")
		if frame%30==0:
			var p=game.player
			var collisions=[]
			for i in range(p.get_slide_collision_count()): collisions.append({"normal":var_to_str(p.get_slide_collision(i).get_normal()),"position":var_to_str(p.get_slide_collision(i).get_position())})
			print(JSON.stringify({"frame":frame,"girl":var_to_str(p.position),"boy":var_to_str(game.boy.position),"velocity":var_to_str(p.velocity),"input":p.input_axis,"jump_held":Input.is_action_pressed("jump"),"floor":p.is_on_floor(),"wall":p.is_on_wall(),"climbing":p.climbing,"climb_clock":p.climb_clock,"target":var_to_str(p.climb_target),"collisions":collisions}))
		if game.player.position.x>4500: break
	Input.action_release("right"); Input.action_release("jump"); Input.action_release("sprint")
	print("ROUTE_PROBE_REACHED ",game.player.position.x>4500)
	game.queue_free(); await process_frame; await process_frame; quit()
