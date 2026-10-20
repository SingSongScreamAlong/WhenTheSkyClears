extends SceneTree
var g
var out
var checks=[]
func _initialize():call_deferred("run")
func frames(n):
	for i in range(n):await physics_frame
func send(button):
	var e=InputEventJoypadButton.new();e.button_index=button;e.pressed=true;Input.parse_input_event(e);await frames(2)
	e=InputEventJoypadButton.new();e.button_index=button;e.pressed=false;Input.parse_input_event(e);await frames(2)
func run():
	var args=OS.get_cmdline_user_args();out=args[args.find("--evidence-dir")+1];DirAccess.make_dir_recursive_absolute(out)
	g=load("res://scenes/main.tscn").instantiate();root.add_child(g);g.smoke_test=true;g.settings_path="user://qa_ui_never_written.json";g.last_house.start(false);g.chapter_card=0;g.settings_return="menu"
	for scale in [1.0,1.2,1.4]:
		g.access.text_scale=scale
		for page in ["sound","access","bindings_keyboard","bindings_controller","reset","pack","gameplay"]:
			g.mode="inventory" if page=="pack" else ("playing" if page=="gameplay" else "settings")
			g.access.page="bindings" if page.begins_with("bindings") else page;g.access.bind_device="controller" if page=="bindings_controller" else "keyboard";g.access.notice="";g.hud.selected=0
			if page=="gameplay":g.player.position=Vector2(8550,699);g.boy.position=Vector2(8498,699)
			await frames(4);await RenderingServer.frame_post_draw
			get_root().get_texture().get_image().save_png(out.path_join(str(roundi(scale*100))+"_"+page+".png"))
			if page not in ["pack","gameplay"]:
				var count=g.hud.buttons.size();await send(JOY_BUTTON_DPAD_DOWN);var navigates=g.hud.selected==1
				g.hud.selected=count-1;await send(JOY_BUTTON_A)
				checks.append({"scale":scale,"page":page,"button_count":count,"dpad_advances_focus":navigates,"accept_back_returns_title":g.mode=="menu"})
	var passed=checks.all(func(c):return c.dpad_advances_focus and c.accept_back_returns_title)
	var f=FileAccess.open(out.path_join("settings_review.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"all_passed":passed,"checks":checks,"scope":"Source-native UI rendering at100/120/140 percent using exact release runtime bytes. Screen/page setup is deliberate; synthetic D-pad and accept/back navigation uses actual UI input. Physical controller not tested; screenshots need visual inspection for clipping."},"\t"));f.close()
	print("SETTINGS_REVIEW ",passed," cases=",checks.size());g.quit_game(0 if passed else 1)
