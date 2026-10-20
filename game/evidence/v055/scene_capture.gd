extends SceneTree
var g
var out=""
var frame=0
var timeline=[]
var held={}
func _initialize():call_deferred("run")
func key(name,on):
	if held.get(name,false)==on:return
	held[name]=on
	var keys={"left":KEY_A,"right":KEY_D,"jump":KEY_SPACE,"crouch":KEY_S}
	var e=InputEventKey.new();e.keycode=keys[name];e.physical_keycode=keys[name];e.pressed=on;Input.parse_input_event(e)
func release():
	for a in ["left","right","jump","crouch"]:key(a,false)
func advance(n,phase,keys=[],shot=false):
	for a in ["left","right","jump","crouch"]:key(a,a in keys)
	for i in range(n):
		await physics_frame;await RenderingServer.frame_post_draw
		if frame%2==0:root.get_texture().get_image().save_jpg(out.path_join("frames/%05d.jpg"%(frame/2)),.91)
		if shot and i==n-1:root.get_texture().get_image().save_png(out.path_join(phase+".png"))
		timeline.append({"frame":frame,"phase":phase,"girl":g.player.position,"boy":g.boy.position,"camera":g.camera.position,"clock":g.clock,"floor_girl":g.player.is_on_floor(),"floor_boy":g.boy.is_on_floor(),"both_covered":g.is_covered(g.player) and g.is_covered(g.boy)})
		frame+=1
func run():
	var args=OS.get_cmdline_user_args();var base=args[args.find("--evidence-dir")+1]
	root.mode=Window.MODE_WINDOWED;root.size=Vector2i(1440,810);root.position=Vector2i(80,80)
	g=load("res://scenes/main.tscn").instantiate();root.add_child(g);g.smoke_test=true;g.last_house_save_path="user://qa_scene_never_written.json";Engine.max_fps=0
	DisplayServer.window_set_title("WTSC OFFLINE EVIDENCE CAPTURE / image IO active / FPS assessed separately")
	for context in [["house",1100],["room",8294],["arcade",2250]]:
		out=base.path_join(context[0]);DirAccess.make_dir_recursive_absolute(out.path_join("frames"));frame=0;timeline=[];release();g.last_house.start(false);g.chapter_card=0;g.message_time=0;g.clock=0
		g.player.position=Vector2(context[1],699);g.boy.position=Vector2(context[1]-54,699);g.player.reset_feet();g.boy.reset_feet();g.camera.position=Vector2(context[1]+166,480)
		await advance(60,"stationary",[],true);await advance(120,"move_right",["right"],true);await advance(120,"reverse_left",["left"],true);await advance(60,"stop",[],true);await advance(40,"jump",["right","jump"],true);await advance(20,"land",[],true);await advance(60,"crouch",["left","crouch"],true)
		var f=FileAccess.open(out.path_join("capture.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"frames":frame/2,"fps":30,"canvas_reference":root.content_scale_size,"window_size":root.size,"camera_zoom":g.camera.zoom,"timeline":timeline,"scope":"Actual native main-game scene, continuous keyboard-event replay in each context. Only resets between context clips. Fixed60simulation with image IO; offline visual evidence, not frame-pacing evidence."},"\t"));f.close()
	release();g.mode="pause"
	if g.get("soundscape")!=null:g.soundscape.stop_all()
	if is_instance_valid(g.ambience):g.ambience.stop();g.ambience.stream=null
	await create_timer(.2).timeout;root.remove_child(g);g.queue_free();await create_timer(.2).timeout;quit(0)
