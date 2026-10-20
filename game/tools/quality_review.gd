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
		timeline.append({"frame":movie_frame,"gap":absf(g.player.position.x-g.boy.position.x),"girl":g.player.position,"boy":g.boy.position,"girl_velocity":g.player.velocity,"boy_velocity":g.boy.velocity,"girl_floor":g.player.is_on_floor(),"boy_floor":g.boy.is_on_floor(),"girl_state":g.child_status(g.player),"boy_state":g.child_status(g.boy)})
		movie_frame+=1
	if label!="":labels.append({"label":label,"end_frame":movie_frame,"girl":str(g.player.position),"boy":str(g.boy.position)})
func use():Input.action_press("interact");g.update_prompt();g.interact()
func stats(values):
	values.sort();var sum=0.0;var over16=0;var over33=0
	for x in values:sum+=x;over16+=int(x>16.667);over33+=int(x>33.334)
	return {"samples":values.size(),"mean":sum/values.size(),"median":values[int(values.size()*.5)],"p95":values[int(values.size()*.95)],"p99":values[int(values.size()*.99)],"maximum":values[-1],"above_16_667":over16,"above_33_334":over33}
func finish():
	release();g.mode="pause"
	if g.get("soundscape")!=null:g.soundscape.stop_all()
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
	seed(53)
	setup(1100);await advance(20)
	Input.action_press("right");await advance(65,"walk",45);release()
	Input.action_press("left");await advance(55,"reverse",20);release()
	for i in range(4):
		Input.action_press("right" if i%2==0 else "left");await advance(32,"quick_"+str(i),18);release()
	await advance(30,"settle",20)
	setup(3700);await advance(15);Input.action_press("right");await advance(60,"doorway",35);release();Input.action_press("left");await advance(48,"doorway_reverse",20);release()
	setup(5362);Input.action_press("crouch");await advance(100,"cover_stop",80);release()
	setup(3900);await advance(15);use();await advance(175,"support",55);release()
	setup(8294);await advance(15);use();await advance(42,"bag",17);release()
	Input.action_press("right");await advance(80);release();use();await advance(70,"meal",28);release()
	g.flags["last_house_complete"]=true;await advance(65,"relief",45)
	for place in [1250,2750,4770,6120,8550]:
		setup(place);await advance(25,"composition_"+str(place),24)
	var f=FileAccess.open(out.path_join("quality_review.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"frames":movie_frame/2,"fps":30,"labels":labels,"pairs":timeline,"probes":probes,"scope":"Actual native runtime driven by identical Input actions in matched visual fixtures. Initial positions reset between scenarios. Not a continuous route or a human/physical-controller/artistic acceptance test."},"\t"));f.close();await finish()
