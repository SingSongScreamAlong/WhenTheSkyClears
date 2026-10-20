extends RefCounted
static func frames(g,n):
	for i in range(n):await g.get_tree().physics_frame
static func key(g,code,pressed=true):
	var e=InputEventKey.new();e.physical_keycode=code;e.keycode=code;e.pressed=pressed;Input.parse_input_event(e);await frames(g,2)
static func pad(g,code,pressed=true):
	var e=InputEventJoypadButton.new();e.button_index=code;e.pressed=pressed;Input.parse_input_event(e);await frames(g,2)
static func shot(g,name):
	await RenderingServer.frame_post_draw
	g.get_viewport().get_texture().get_image().save_png(g.report_path(name+".png"))
static func run(g):
	if "--audio-capture" in g.qa_args:await audio_capture(g);return
	var capture="--access-capture" in g.qa_args
	g.smoke_test=true;var a=g.access
	g.settings_path="user://qa_access_"+str(Time.get_ticks_usec())+".json"
	a.reset();g.last_house.start(false);g.chapter_card=0;await frames(g,20)
	g.assert_check("default_keyboard_preserved",a.label("interact","keyboard")=="E" and a.label("jump","keyboard")=="Space")
	g.assert_check("default_pad_preserved",a.label("heal","controller")=="LB / L1" and a.label("interact","controller")=="X / Square")
	g.assert_check("conflict_rejected",not a.try_bind("jump","keyboard",KEY_E,false) and "Already used" in a.notice)
	g.assert_check("escape_reserved",not a.try_bind("jump","keyboard",KEY_ESCAPE,false))
	g.assert_check("menu_start_reserved",not a.try_bind("jump","controller",JOY_BUTTON_START,false))
	g.mode="settings";a.page="bindings";a.bind_device="keyboard";a.begin_bind("jump")
	await key(g,KEY_K);await key(g,KEY_K,false)
	g.assert_check("raw_key_capture_rebinds_without_gameplay",a.rebind_action=="" and a.label("jump","keyboard")=="K" and g.mode=="settings")
	a.begin_bind("interact");await key(g,KEY_K);await key(g,KEY_K,false)
	g.assert_check("captured_conflict_stays_pending",a.rebind_action=="interact" and "Already used" in a.notice)
	if capture:await shot(g,"03_binding_conflict")
	await key(g,KEY_ESCAPE);await key(g,KEY_ESCAPE,false)
	g.assert_check("escape_cancels_binding_without_leaving_settings",a.rebind_action=="" and g.mode=="settings")
	a.bind_device="controller";a.begin_bind("interact");await pad(g,JOY_BUTTON_RIGHT_STICK);await pad(g,JOY_BUTTON_RIGHT_STICK,false)
	g.assert_check("raw_pad_capture_rebinds",a.label("interact","controller")=="Button 8" and a.rebind_action=="")
	a.begin_bind("jump");await pad(g,JOY_BUTTON_START);await pad(g,JOY_BUTTON_START,false)
	g.assert_check("pad_start_cancels_capture",a.rebind_action=="" and g.mode=="settings")
	# Save a nontrivial valid key permutation, not only a free key.
	a.try_bind("left","keyboard",KEY_J,false);a.try_bind("right","keyboard",KEY_A,false);a.try_bind("left","keyboard",KEY_D,false)
	a.text_scale=1.4;a.crouch_toggle=true;a.mix.Weather=.3;g.volume=.7;g.reduced_motion=true
	g.assert_check("settings_atomic_write",a.save_settings(true))
	a.reset();a.load_settings()
	g.assert_check("settings_and_key_permutation_persist",a.text_scale==1.4 and a.crouch_toggle and a.mix.Weather==.3 and is_equal_approx(g.volume,.7) and g.reduced_motion and a.label("left","keyboard")=="D" and a.label("right","keyboard")=="A")
	# Backup recovery from malformed primary remains independent of game saves.
	a.save_settings(true);var f=FileAccess.open(g.settings_path,FileAccess.WRITE);f.store_string("{bad");f.close();a.text_scale=1;a.load_settings()
	g.assert_check("malformed_settings_recovers_backup",a.text_scale==1.4)
	# Legacy preference files migrate without changing their three old values.
	f=FileAccess.open(g.settings_path,FileAccess.WRITE);f.store_string(JSON.stringify({"volume":.4,"muted":true,"reduced_motion":true}));f.close();a.load_settings()
	g.assert_check("legacy_preferences_migrate",is_equal_approx(g.volume,.4) and g.muted and g.reduced_motion and a.text_scale==1 and not a.crouch_toggle)
	f=FileAccess.open(g.settings_path,FileAccess.WRITE);f.store_string(JSON.stringify({"volume":"bad","text_scale":{},"bindings":{"keyboard":{"jump":"bad"},"controller":[]}}));f.close();a.reset();a.load_settings()
	g.assert_check("invalid_preference_types_are_safe",g.volume==.6 and a.text_scale==1 and a.label("jump","keyboard")=="Space")
	a.text_scale=1.4;a.crouch_toggle=true;g.reduced_motion=true
	g.mode="settings";a.page="access"
	if capture:await shot(g,"02_access_140_percent")
	a.reset();g.assert_check("reset_restores_defaults",a.text_scale==1 and not a.crouch_toggle and g.volume==.6 and a.label("left","keyboard")=="A")
	g.mode="playing";a.try_bind("jump","keyboard",KEY_K,false)
	await key(g,KEY_K);await key(g,KEY_K,false);await frames(g,3)
	g.assert_check("rebound_raw_key_drives_native_jump",not g.player.is_on_floor() and g.player.position.y<680)
	await frames(g,65);a.reset()
	g.mode="playing";await key(g,KEY_D);var x=g.player.position.x;await frames(g,35);await key(g,KEY_D,false)
	g.assert_check("raw_keyboard_moves_native_body",g.player.position.x>x+55)
	a.crouch_toggle=true;await key(g,KEY_S);await key(g,KEY_S,false);await frames(g,8)
	g.assert_check("toggle_crouch_survives_key_release",g.player.crouching and a.crouch_latched)
	await pad(g,JOY_BUTTON_B);await pad(g,JOY_BUTTON_B,false);await frames(g,8)
	g.assert_check("pad_toggles_crouch_back",not a.crouch_latched and not g.player.crouching and a.last_device=="controller")
	a.crouch_toggle=false;await key(g,KEY_S);g.assert_check("default_hold_crouches",g.player.crouching)
	await key(g,KEY_S,false);await frames(g,8);g.assert_check("default_release_stands",not g.player.crouching)
	# Toggle cannot stand through the arcade ceiling; moving out releases it.
	g.player.position=Vector2(2400,699);g.boy.position=Vector2(2348,699);a.crouch_toggle=true;a.crouch_latched=true;await frames(g,12)
	await key(g,KEY_S);await key(g,KEY_S,false);await frames(g,8)
	g.assert_check("toggle_respects_overhead_clearance",not a.crouch_latched and g.player.crouching and not g.player.can_stand())
	g.player.position=Vector2(1100,699);g.boy.position=Vector2(1048,699);await frames(g,12)
	g.assert_check("toggle_stands_after_leaving_low_ceiling",not g.player.crouching)
	a.crouch_toggle=false
	var axis=InputEventJoypadMotion.new();axis.axis=JOY_AXIS_LEFT_X;axis.axis_value=1;Input.parse_input_event(axis);var start_x=g.player.position.x;await frames(g,35)
	axis=InputEventJoypadMotion.new();axis.axis=JOY_AXIS_LEFT_X;axis.axis_value=0;Input.parse_input_event(axis);await frames(g,8)
	g.assert_check("simulated_stick_moves_native_body",g.player.position.x>start_x+60 and a.last_device=="controller")
	await pad(g,JOY_BUTTON_A);await pad(g,JOY_BUTTON_A,false);await frames(g,3)
	g.assert_check("simulated_pad_jump_uses_native_body",not g.player.is_on_floor() and g.player.position.y<680)
	await frames(g,65)
	await pad(g,JOY_BUTTON_START);await pad(g,JOY_BUTTON_START,false);var before=g.clock;await frames(g,30)
	g.assert_check("simulated_start_pauses_and_freezes",g.mode=="pause" and g.clock==before)
	await pad(g,JOY_BUTTON_START);await pad(g,JOY_BUTTON_START,false)
	g.assert_check("simulated_start_resumes",g.mode=="playing")
	await pad(g,JOY_BUTTON_BACK);await pad(g,JOY_BUTTON_BACK,false);before=g.clock;await frames(g,25)
	g.assert_check("simulated_pack_freezes",g.mode=="inventory" and g.clock==before)
	await pad(g,JOY_BUTTON_BACK);await pad(g,JOY_BUTTON_BACK,false)
	g.assert_check("simulated_pack_closes",g.mode=="playing")
	g.hud.activate("settings");await frames(g,3);g.hud.selected=1
	await pad(g,JOY_BUTTON_A);await pad(g,JOY_BUTTON_A,false)
	g.assert_check("pad_menu_accept_opens_access_tab",g.mode=="settings" and a.page=="access")
	await pad(g,JOY_BUTTON_B);await pad(g,JOY_BUTTON_B,false)
	g.assert_check("pad_cancel_returns_to_sound_tab",a.page=="sound" and g.mode=="settings")
	await pad(g,JOY_BUTTON_B);await pad(g,JOY_BUTTON_B,false)
	g.assert_check("pad_cancel_closes_settings",g.mode=="playing")
	# Actual focus/accept path cycles text size and confirms a default reset.
	g.hud.activate("settings");a.page="access";await frames(g,4);g.hud.selected=3
	await key(g,KEY_ENTER);await key(g,KEY_ENTER,false)
	g.assert_check("keyboard_menu_changes_text_size",is_equal_approx(a.text_scale,1.2))
	await frames(g,3);g.hud.selected=7;await pad(g,JOY_BUTTON_A);await pad(g,JOY_BUTTON_A,false)
	g.assert_check("reset_requires_confirmation",a.page=="reset" and is_equal_approx(a.text_scale,1.2))
	await frames(g,3);g.hud.selected=3;await pad(g,JOY_BUTTON_A);await pad(g,JOY_BUTTON_A,false)
	g.assert_check("confirmed_ui_reset_restores_defaults",a.page=="access" and a.text_scale==1 and not a.crouch_toggle)
	g.mode="settings";a.page="bindings";a.bind_device="controller";a.text_scale=1.4
	if capture:await shot(g,"05_controller_bindings_140_percent")
	g.mode="inventory"
	if capture:await shot(g,"06_pack_140_percent")
	a.text_scale=1;g.mode="settings";a.page="sound"
	if capture:await shot(g,"01_sound_mix")
	g.assert_check("device_prompt_uses_current_binding",a.label("interact")=="X / Square" and "X / Square" in g.control_text("Hold E to search"))
	await key(g,KEY_L,false);await key(g,KEY_L);await key(g,KEY_L,false)
	g.assert_check("keyboard_prompt_returns",a.last_device=="keyboard" and "HOLD E" in g.control_text("Hold E to search"))
	g.volume=0;g.apply_volume();g.assert_check("master_zero_is_muted",AudioServer.is_bus_mute(0))
	g.volume=.6;g.muted=true;g.apply_volume();g.assert_check("master_mute_is_applied",AudioServer.is_bus_mute(0))
	g.muted=false;a.mix.Weather=0;g.apply_volume();g.assert_check("weather_bus_zero_is_silent",AudioServer.is_bus_mute(AudioServer.get_bus_index("WTSCWeather")))
	a.mix.Weather=.9;g.apply_volume();g.assert_check("weather_bus_restored",not AudioServer.is_bus_mute(AudioServer.get_bus_index("WTSCWeather")))
	# No audio hardware is claimed by these control/data checks.
	g.soundscape.audit_enabled=true;g.mode="playing";g.player.position=Vector2(4700,699);g.boy.position=Vector2(4648,699)
	await frames(g,120);var outdoor=g.soundscape.indoor
	g.player.position=Vector2(8550,699);g.boy.position=Vector2(8498,699);await frames(g,120)
	g.assert_check("roof_transition_follows_actual_safe_zones",outdoor<.05 and g.soundscape.indoor>.95)
	var cue=g.play_sfx("warning",-14,Vector2(8880,650),"LIGHT RIGHT - COVER BOTH CHILDREN")
	g.assert_check("threat_spatial_bus_and_caption",cue is AudioStreamPlayer2D and cue.bus=="WTSCThreat" and g.soundscape.caption_time>0 and "COVER" in g.soundscape.caption)
	g.assert_check("threat_ducks_ambience",g.soundscape.duck>2)
	await frames(g,3)
	g.assert_check("rain_duck_reaches_players",g.soundscape.interior.volume_db < -30)
	for i in range(12):g.play_sfx("cloth",-14,g.player.position)
	g.assert_check("repeated_action_debounced",g.soundscape.voices.size()<=8)
	g.mode="pause";await frames(g,2);g.assert_check("pause_stops_active_cues",g.soundscape.voices.all(func(v):return v.stream_paused))
	g.mode="playing";g.flags["last_house_complete"]=true;a.text_scale=1.4
	if capture:await shot(g,"04_gameplay_feedback_140_percent")
	g.soundscape.audit_enabled=false;g.soundscape.stop_all()
	# Restart loops after stop_all only happens during shutdown, so end now.
	for suffix in ["",".tmp",".bak"]:DirAccess.remove_absolute(g.settings_path+suffix)
	var passed=g.test_log.all(func(c):return c.passed)
	var report={"build":"0.5.4","all_passed":passed,"checks":g.test_log,"method":"Native keyboard and synthetic InputEventJoypadButton injection, real controller/physics/menu paths and disposable preference files. No physical controller or human hearing validation. Targeted audio state/fixture setups are separate from route completion."}
	f=FileAccess.open(g.report_path("access_checks.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close();print("ACCESS_CHECKS ",passed," count=",g.test_log.size())
	g.quit_game(0 if passed else 1)
static func audio_capture(g):
	g.smoke_test=true;g.soundscape.audit_enabled=true;g.last_house.start(false);g.chapter_card=0;g.mode="settings"
	g.access.reset();g.access.page="sound"
	g.ambience.play()
	var record=AudioEffectRecord.new();AudioServer.add_bus_effect(0,record);record.set_recording_active(true)
	g.player.position=Vector2(4700,699);g.boy.position=Vector2(4648,699)
	await g.get_tree().create_timer(2).timeout
	# Each isolated positional cue has equal distance from the settled listener.
	g.soundscape.exterior.volume_db=-80;g.soundscape.interior.volume_db=-80
	g.soundscape.cue("collect",0,Vector2(g.camera.position.x-500,g.camera.position.y),"LEFT SOURCE")
	await g.get_tree().create_timer(1.5).timeout
	g.soundscape.cue("collect",0,Vector2(g.camera.position.x+500,g.camera.position.y),"RIGHT SOURCE")
	await g.get_tree().create_timer(1.5).timeout
	g.soundscape.cue("warning",-6,Vector2(g.camera.position.x+300,650),"THREAT RIGHT - COVER BOTH CHILDREN")
	await g.get_tree().create_timer(2.7).timeout
	g.player.position=Vector2(8550,699);g.boy.position=Vector2(8498,699)
	await g.get_tree().create_timer(3).timeout
	g.soundscape.cue("cloth",-4,g.player.position,"BAG SET DOWN")
	await g.get_tree().create_timer(1).timeout
	g.soundscape.cue("bread",-4,g.player.position,"SHARING FOOD")
	await g.get_tree().create_timer(1).timeout
	record.set_recording_active(false);var wav=record.get_recording();var err=wav.save_to_wav(g.report_path("native_mix.wav"))
	var report={"build":"0.5.4","saved":err==OK,"seconds":wav.get_length(),"audio_driver":AudioServer.get_driver_name(),"events":g.soundscape.events,"scope":"Actual native master bus recording in a deliberate positional/roof transition fixture. No microphone or OS loopback. No subjective listening/physical device claim."}
	var f=FileAccess.open(g.report_path("audio_capture.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	print("AUDIO_CAPTURE ",JSON.stringify(report));g.quit_game(0 if err==OK and wav.get_length()>8 else 1)
