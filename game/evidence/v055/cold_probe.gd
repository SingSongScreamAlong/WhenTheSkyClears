extends SceneTree
var g
var events=[]
var active=false
var entry=0
var phase="startup"
var origin=0
func stamp(kind):
	if active:events.append({"event":kind,"phase":phase,"us":Time.get_ticks_usec()-origin})
func _initialize():call_deferred("run")
func _process(_dt):stamp("process");return false
func run():
	var args=OS.get_cmdline_user_args();var out=args[args.find("--evidence-dir")+1]
	root.mode=Window.MODE_WINDOWED;root.size=Vector2i(1440,810);root.position=Vector2i(80,80)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED);Engine.max_fps=60
	origin=Time.get_ticks_usec();active=true
	RenderingServer.frame_pre_draw.connect(func():stamp("render_pre"))
	RenderingServer.frame_post_draw.connect(func():stamp("render_post"))
	stamp("scene_create_begin");g=load("res://scenes/main.tscn").instantiate();root.add_child(g);stamp("scene_create_end")
	g.smoke_test=true;g.last_house_save_path="user://qa_cold_probe_never_written.json"
	for step in range(2):
		phase="first_entry" if step==0 else "repeat_entry"
		stamp("section_setup_begin");g.last_house.start(false);g.player.position=Vector2(8294,699);g.boy.position=Vector2(8240,699);g.player.reset_feet();g.boy.reset_feet();g.camera.position=Vector2(8460,480);g.chapter_card=0;g.message_time=0;stamp("section_setup_end")
		DisplayServer.window_set_title("WTSC cold-frame phase diagnostic / no capture I/O")
		var start=Time.get_ticks_usec()
		while Time.get_ticks_usec()-start<3000000:await process_frame
	active=false
	var f=FileAccess.open(out.path_join("phase_events.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"events":events,"scope":"First and repeat entry in one fresh native process. All constructor, setup and first-render events retained; no prewarm, capture or per-frame disk I/O. pre/post signals bracket render submission, not a GPU hardware timer."},"\t"));f.close()
	g.mode="pause";g.soundscape.stop_all();g.ambience.stop();g.ambience.stream=null
	await create_timer(.2).timeout;root.remove_child(g);g.queue_free();await create_timer(.2).timeout;quit(0)
