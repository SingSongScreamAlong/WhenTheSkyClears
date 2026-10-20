extends SceneTree
var g
var out=""
var movie_frame=0
var timeline=[]
var probes=[]
var labels=[]
var measuring=false
var last_usec=0
var intervals=[]
var calls=[]
func _initialize():call_deferred("run")
func _process(_dt):
	var now=Time.get_ticks_usec()
	if measuring and last_usec>0:
		intervals.append(float(now-last_usec)/1000.0);calls.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	last_usec=now
	return false
func release():
	for a in ["left","right","jump","sprint","crouch","interact"]:Input.action_release(a)
func setup(x):
	release();g.last_house.start(false);g.chapter_card=0;g.clock=0;g.playtime=0
	g.player.position=Vector2(x,699);g.boy.position=Vector2(x-54,699);g.player.reset_feet();g.boy.reset_feet()
	g.camera.position=Vector2(x+170,480)
func advance(n,label="",snap=-1):
	for i in range(n):
		await physics_frame;await RenderingServer.frame_post_draw
		if movie_frame%2==0:root.get_texture().get_image().save_jpg(out.path_join("frames/%05d.jpg"%(movie_frame/2)),.9)
		if i==snap:root.get_texture().get_image().save_png(out.path_join(label+".png"))
		for child in [g.player,g.boy]:
			var probe=child.get("render_probe")
			if probe is Dictionary and not probe.is_empty():
				var p=probe.duplicate(true);p["frame"]=movie_frame;p["child"]=str(child.name);p["position"]=child.position;p["velocity"]=child.velocity;p["floor"]=child.is_on_floor();probes.append(p)
		movie_frame+=1
	if label!="":labels.append({"label":label,"end_frame":movie_frame,"girl":str(g.player.position),"boy":str(g.boy.position)})
func use():Input.action_press("interact");g.update_prompt();g.interact()
func stats(values):
	values.sort();var sum=0.0;var over16=0;var over33=0
	for x in values:sum+=x;over16+=int(x>16.667);over33+=int(x>33.334)
	return {"samples":values.size(),"mean":sum/values.size(),"median":values[int(values.size()*.5)],"p95":values[int(values.size()*.95)],"p99":values[int(values.size()*.99)],"maximum":values[-1],"above_16_667":over16,"above_33_334":over33}
func finish():
	release();g.mode="pause"
	if is_instance_valid(g.ambience):g.ambience.stop();g.ambience.stream=null
	# Dummy audio advances independently of the fixed visual clock. Give its
	# playback thread a real mixing interval before freeing the player/tree.
	await create_timer(.15).timeout
	root.remove_child(g);g.queue_free();g=null
	await create_timer(.15).timeout;call_deferred("quit",0)
func run():
	var args=OS.get_cmdline_user_args();var idx=args.find("--evidence-dir");out=args[idx+1]
	DirAccess.make_dir_recursive_absolute(out.path_join("frames"))
	g=load("res://scenes/main.tscn").instantiate();root.add_child(g);g.smoke_test=true
	g.last_house_save_path="user://qa_visual_never_written.json"
	if "--perf" in args:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		var scenes={}
		for place in [6120,8550]:
			setup(place);Input.action_press("crouch") if place==6120 else Input.action_release("crouch")
			await create_timer(2).timeout;intervals=[];calls=[];measuring=true
			await create_timer(8).timeout;measuring=false
			scenes[str(place)]={"frame_interval_ms":stats(intervals),"draw_calls":stats(calls),"static_memory_bytes":Performance.get_monitor(Performance.MEMORY_STATIC)}
		var f=FileAccess.open(out.path_join("performance.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"Uncapped VSync-disabled native Godot4.6 source runtime,1440x810, audio dummy. Two8-second fixed viewpoints after2-second warmup each; no screenshot IO during measurement. Not human input latency, Mac or packaged performance.","scenes":scenes},"\t"));f.close();await finish();return
	setup(1000);await advance(25)
	Input.action_press("right");await advance(50,"start_walk",5)
	release();await advance(24,"stop",10)
	Input.action_press("left");await advance(50,"turn",5)
	release();Input.action_press("crouch");await advance(22,"crouch",10)
	Input.action_press("right");await advance(40,"crouch_travel",25)
	release();await advance(22)
	Input.action_press("jump");await advance(22,"jump",13);Input.action_release("jump");await advance(46,"landing",26)
	setup(1000);await advance(8);Input.action_press("right");Input.action_press("sprint");await advance(70,"sprint_start",10)
	release();await advance(30,"sprint_stop",10);Input.action_press("left");Input.action_press("sprint");await advance(56,"sprint_turn",8);release();await advance(20)
	setup(3900);await advance(15);use();await advance(72,"girl_support",55);await advance(105,"boy_support",96);release()
	setup(8294);await advance(15);use();await advance(36,"bag_lowering",16);release();await advance(24,"bag_rest",20)
	setup(8554);g.flags["bag_down"]=true;await advance(15);use();await advance(22,"meal_offer",14);await advance(38,"meal_taste",16);release();await advance(30)
	g.flags["last_house_complete"]=true;await advance(45,"quiet",35)
	var f=FileAccess.open(out.path_join("pose_review.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"frames":movie_frame/2,"fps":30,"labels":labels,"probes":probes,"scope":"Native fixed-input pose/acting fixture; initial scenario positions deliberately reset between locomotion, support, bag and meal. Existing game logic/input/physics owns each action. Not a continuous route or human playtest."},"\t"));f.close();await finish()
