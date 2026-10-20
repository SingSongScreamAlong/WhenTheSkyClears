extends SceneTree
var g
var out=""
var samples=[]
var active=false
var last_us=0
var wall_start=0
var stage_name=""
var phase_name=""
var scene_wall=0
var held={}
var startup_ms=0.0
var foreground
var quick=false
class StudyGroundPlane extends Node2D:
	func _draw():
		draw_rect(Rect2(-20000,700,40000,10000),Color("27302e"))
		draw_line(Vector2(-20000,700),Vector2(20000,700),Color("7c8876"),2)
func _initialize():call_deferred("run")
func _process(_dt):
	var now=Time.get_ticks_usec()
	if active and last_us>0:
		samples.append({"case":stage_name,"phase":phase_name,"ms":float(now-last_us)/1000.0,"wall_s":float(now-scene_wall)/1e6,"girl":g.player.position,"boy":g.boy.position,"camera":g.camera.position,"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"process_ms":Performance.get_monitor(Performance.TIME_PROCESS)*1000,"physics_ms":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000})
	last_us=now
	return false
func action(name,pressed):
	if held.get(name,false)==pressed:return
	held[name]=pressed
	var keys={"left":KEY_A,"right":KEY_D,"jump":KEY_SPACE,"sprint":KEY_SHIFT,"crouch":KEY_S}
	var e=InputEventKey.new();e.keycode=keys[name];e.physical_keycode=keys[name];e.pressed=pressed
	Input.parse_input_event(e)
func release():
	for name in ["left","right","jump","sprint","crouch"]:action(name,false)
func stats(values):
	values.sort();var over16=0;var over20=0;var over33=0;var over50=0;var total=0.0
	for v in values:total+=v;over16+=int(v>16.9);over20+=int(v>20);over33+=int(v>33.334);over50+=int(v>50)
	return {"samples":values.size(),"p50_ms":values[int(values.size()*.50)],"p95_ms":values[int(values.size()*.95)],"p99_ms":values[int(values.size()*.99)],"worst_ms":values[-1],"mean_ms":total/values.size(),"above16_9":over16,"above20":over20,"above33_3":over33,"above50":over50}
func span(seconds,label,keys=[]):
	if quick:seconds=minf(seconds,.12)
	phase_name=label
	for a in ["left","right","jump","sprint","crouch"]:action(a,a in keys)
	var start=Time.get_ticks_usec()
	while float(Time.get_ticks_usec()-start)/1e6<seconds:await process_frame
func finish():
	active=false;release();g.mode="pause"
	if g.get("soundscape")!=null:g.soundscape.stop_all()
	if is_instance_valid(g.ambience):g.ambience.stop();g.ambience.stream=null
	await create_timer(.2).timeout
	root.remove_child(g);g.queue_free();await create_timer(.2).timeout;quit(0)
func run():
	var args=OS.get_cmdline_user_args();out=args[args.find("--evidence-dir")+1];DirAccess.make_dir_recursive_absolute(out);quick="--quick" in args
	root.mode=Window.MODE_WINDOWED;root.size=Vector2i(1440,810);root.position=Vector2i(80,80)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED);Engine.max_fps=60
	var start=Time.get_ticks_usec();g=load("res://scenes/main.tscn").instantiate();root.add_child(g);startup_ms=float(Time.get_ticks_usec()-start)/1000
	g.smoke_test=true;g.last_house_save_path="user://qa_study_never_written.json"
	for node in g.get_children():
		if node.get_script()!=null and str(node.get_script().resource_path)=="res://scripts/foreground.gd":foreground=node
	assert(foreground!=null)
	var plane=StudyGroundPlane.new();plane.z_index=0;g.add_child(plane)
	var cases=[["full_rain",5,true,true],["open_rain",5,true,true,2300]]
	if quick:cases=cases.slice(0,1)
	var summaries={}
	for c in cases:
		active=false;release();g.last_house.start(false);var start_x=float(c[4]) if c.size()>4 else 8294.0
		g.player.position=Vector2(start_x,699);g.boy.position=Vector2(start_x-54,699);g.player.reset_feet();g.boy.reset_feet();g.chapter_card=0;g.message_time=0
		g.camera.position=Vector2(start_x+166,480);g.set_meta("study_stage",c[1]);g.set_meta("study_rain",c[3]);g.world.visible=c[1]>0;foreground.visible=c[1]>=5;g.boy.visible=c[2];plane.visible=c[1]<5
		stage_name=c[0];DisplayServer.window_set_title("WTSC DIAGNOSTIC / "+stage_name+" / real time60 target / capture IO OFF")
		var before=samples.size();scene_wall=Time.get_ticks_usec();last_us=scene_wall;active=true
		await span(3,"cold_entry");await span(3,"warm_stationary");await span(2.5,"move_right",["right"]);await span(2,"reverse_left",["left"]);await span(1,"stop");await span(1.8,"sprint",["right","sprint"]);await span(.24,"jump",["jump","left"]);await span(1.26,"air_land",["left"]);await span(1,"crouch",["crouch","left"]);await span(1,"settle")
		active=false;release();var per={}
		for phase in ["cold_entry","warm_stationary","move_right","reverse_left","stop","sprint","jump","air_land","crouch","settle"]:
			var values=[]
			for sample in samples.slice(before):
				if sample.phase==phase:values.append(sample.ms)
			if not values.is_empty():per[phase]=stats(values)
		summaries[stage_name]=per
	var rd=RenderingServer.get_rendering_device();var gpu=rd.call("get_device_name") if rd!=null and rd.has_method("get_device_name") else "unavailable"
	var settings={"window_size":DisplayServer.window_get_size(),"canvas_reference":root.content_scale_size,"camera_zoom":g.camera.zoom,"window_mode":root.mode,"current_screen":DisplayServer.window_get_current_screen(),"refresh_hz":DisplayServer.screen_get_refresh_rate(DisplayServer.window_get_current_screen()),"vsync_mode":DisplayServer.window_get_vsync_mode(),"max_fps":Engine.max_fps,"physics_hz":Engine.physics_ticks_per_second,"renderer":ProjectSettings.get_setting("rendering/renderer/rendering_method"),"gpu":gpu,"startup_scene_load_ms":startup_ms}
	var f=FileAccess.open(out.path_join("timing.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"settings":settings,"summary":summaries,"samples":samples,"scope":"Actual main-game scene and native keyboard-event replay with automatic camera. Real wall-clock timing, no fixed-fps and no screenshot IO in measurement. Cold means first3seconds per case in one fresh process; not a system/driver-cache cold boot. Cases reset only between measurement sequences; no human/physical-controller acceptance."},"\t"));f.close();await finish()
