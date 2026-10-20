extends RefCounted
static func frames(g,n):
	for i in range(n): await g.get_tree().physics_frame
static func run(g):
	g.smoke_test=true;g.load_chapter(3,false);g.mode="playing";g.flags={};g.cache_remaining={}
	g.player.position=Vector2(3190,699);g.boy.position=Vector2(3145,699);g.scrap=6;g.medicine=2
	await frames(g,8);g.update_prompt()
	g.assert_check("full_pack_normal_prompt_selects_pump",g.near_item.get("id","")=="school_drain")
	Input.action_press("interact");g.interact();await frames(g,245);Input.action_release("interact")
	g.assert_check("full_pack_pump_completes_without_cache_assignment",g.flags.get("school_drain",false))
	g.update_prompt();g.assert_check("full_cache_reports_unavailable",g.near_item.is_empty() and "PACK FULL" in g.prompt)
	g.scrap=0;g.medicine=0;g.player.action_time=0;g.update_prompt()
	g.assert_check("cache_returns_when_pack_has_room",g.near_item.get("id","")=="school_cupboard")
	g.load_chapter(2,false);g.mode="playing";await frames(g,3)
	var before=g.clock;var beam=g.beam_x();var played=g.playtime
	var event=InputEventAction.new();event.action="pause";event.pressed=true;g._unhandled_input(event)
	await frames(g,120)
	g.assert_check("pause_freezes_clock_and_searchlight",g.mode=="pause" and g.clock==before and g.beam_x()==beam and g.playtime==played)
	g.mode="inventory";await frames(g,60);g.assert_check("inventory_freezes_hazard_clock",g.clock==before)
	g.mode="playing";await frames(g,60);g.assert_check("resume_advances_clock",g.clock>before+.9)
	var pad_count=0
	for ev in InputMap.action_get_events("heal"):
		if ev is InputEventJoypadButton and ev.button_index==JOY_BUTTON_LEFT_SHOULDER:pad_count+=1
	g.assert_check("medicine_has_left_shoulder_binding",pad_count==1)
	g.health=40;g.medicine=1;var pad=InputEventJoypadButton.new();pad.button_index=JOY_BUTTON_LEFT_SHOULDER;pad.pressed=true;g._unhandled_input(pad)
	g.assert_check("gamepad_event_uses_medicine",g.medicine==0 and g.health==85)
	var unique="user://qa_trust_"+str(Time.get_ticks_usec())
	g.journey_save_path=unique+".json";g.rehearsal_save_path=unique+".rehearsal";g.settings_path=unique+".settings"
	g.save_path=g.journey_save_path;g.save_exists=false;g.smoke_test=false;g.start_crossing();g.write_save();g.return_to_title()
	g.assert_check("rehearsal_does_not_enable_main_continue",not g.save_exists and not FileAccess.file_exists(g.journey_save_path))
	var resumed=g.continue_journey();g.assert_check("continue_without_main_save_stays_title",not resumed and g.mode=="menu" and not g.journey_active)
	g.new_journey();g.flags["qa_main"]=true;g.rations=3;g.write_save();var main=FileAccess.get_file_as_string(g.journey_save_path)
	g.start_crossing();g.write_save();g.return_to_title()
	g.assert_check("rehearsal_preserves_main_bytes",FileAccess.get_file_as_string(g.journey_save_path)==main and g.save_exists)
	g.continue_journey();g.assert_check("continue_restores_actual_main_state",g.chapter==0 and g.flags.get("qa_main",false) and g.rations==3 and not g.section_preview)
	g.write_save();g.assert_check("atomic_save_retains_valid_backup",g.read_valid_save(g.save_path+".bak")!=null and not FileAccess.file_exists(g.save_path+".tmp"))
	var file=FileAccess.open(g.save_path,FileAccess.WRITE);file.store_string('{"schema":1,"flags":[]}');file.close()
	g.flags={};var recovered=g.load_save(true)
	g.assert_check("malformed_flags_recovers_backup",recovered and g.flags is Dictionary and g.flags.get("qa_main",false) and not g.save_notice.is_empty())
	DirAccess.remove_absolute(g.save_path+".bak")
	file=FileAccess.open(g.save_path,FileAccess.WRITE);file.store_string('{"schema":1,"flags":[]}');file.close()
	g.flags={"safe":true};var rejected=g.load_save(true)
	g.assert_check("invalid_save_without_backup_is_rejected",not rejected and g.flags.get("safe",false) and not g.save_exists)
	g.assert_check("invalid_flag_value_rejected",not g.valid_save_data({"schema":1,"flags":{"bad":[]}}))
	g.assert_check("invalid_memories_type_rejected",not g.valid_save_data({"schema":1,"memories":[]}))
	g.assert_check("invalid_cache_amount_rejected",not g.valid_save_data({"schema":1,"cache_remaining":{"a":{"rations":-1}}}))
	g.assert_check("invalid_numeric_type_rejected",not g.valid_save_data({"schema":1,"health":"many"}))
	g.assert_check("legacy_schema_one_is_supported",g.valid_save_data({"schema":1,"build":"0.3.0","flags":{},"memories":{},"chapter":1}))
	for path in [g.journey_save_path,g.rehearsal_save_path,g.settings_path]:
		for suffix in ["",".bak",".tmp"]:
			if FileAccess.file_exists(path+suffix):DirAccess.remove_absolute(path+suffix)
	g.smoke_test=true
	var passed=true
	for check in g.test_log:
		if not check.passed:passed=false
	var f=FileAccess.open(g.report_path("trust_checks.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"all_passed":passed,"checks":g.test_log,"scope":"Native scene, real prompts/held input/event mapping, paused frames and unique disposable disk saves. Scenario setup repositions actors. No physical controller or human playtest claimed."},"\t"));f.close()
	print("TRUST_RESULT ",passed," checks=",g.test_log.size());g.quit_game(0 if passed else 1)
