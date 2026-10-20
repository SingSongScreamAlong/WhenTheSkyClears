extends RefCounted
# Shared preferences are separate from journey state. Menu navigation stays fixed
# so an unfortunate gameplay binding can always be cancelled or reset.
const KEYS={"left":[KEY_A,KEY_LEFT],"right":[KEY_D,KEY_RIGHT],"jump":[KEY_SPACE,KEY_W,KEY_UP],"crouch":[KEY_S,KEY_DOWN],"sprint":[KEY_SHIFT],"interact":[KEY_E],"companion":[KEY_Q],"pack":[KEY_TAB],"heal":[KEY_H],"restart":[KEY_R],"pause":[KEY_ESCAPE],"fullscreen":[KEY_F11,KEY_F],"mute":[KEY_M]}
const PADS={"jump":JOY_BUTTON_A,"crouch":JOY_BUTTON_B,"interact":JOY_BUTTON_X,"companion":JOY_BUTTON_Y,"pause":JOY_BUTTON_START,"pack":JOY_BUTTON_BACK,"sprint":JOY_BUTTON_RIGHT_SHOULDER,"heal":JOY_BUTTON_LEFT_SHOULDER,"left":JOY_BUTTON_DPAD_LEFT,"right":JOY_BUTTON_DPAD_RIGHT}
const ACTIONS=["left","right","jump","crouch","sprint","interact","companion","pack","heal","restart"]
const NAMES={"left":"Move left","right":"Move right","jump":"Jump","crouch":"Crouch","sprint":"Run","interact":"Interact","companion":"Wait / call","pack":"Open pack","heal":"Medicine","restart":"Checkpoint"}
var g
var text_scale=1.0
var crouch_toggle=false
var crouch_latched=false
var mix={"Music":.8,"Weather":.9,"Actions":1.0,"Threat":1.0}
var bindings={"keyboard":{},"controller":{}}
var last_device="keyboard"
var bind_device="keyboard"
var rebind_action=""
var notice=""
var page="sound"
func _init(game):g=game
func install():
	for action in KEYS:
		if not InputMap.has_action(action):InputMap.add_action(action)
		InputMap.action_erase_events(action)
		for key in KEYS[action]:
			var ev=InputEventKey.new();ev.physical_keycode=key;InputMap.action_add_event(action,ev)
	for action in PADS:
		var ev=InputEventJoypadButton.new();ev.button_index=PADS[action];InputMap.action_add_event(action,ev)
	for action in ["left","right"]:
		var ev=InputEventJoypadMotion.new();ev.axis=JOY_AXIS_LEFT_X;ev.axis_value=-1 if action=="left" else 1;InputMap.action_add_event(action,ev)
	for device in bindings:
		for action in bindings[device]:_replace(action,device,int(bindings[device][action]))
func _replace(action,device,code):
	for ev in InputMap.action_get_events(action):
		if (device=="keyboard" and ev is InputEventKey) or (device=="controller" and ev is InputEventJoypadButton):InputMap.action_erase_event(action,ev)
	var ev=InputEventKey.new() if device=="keyboard" else InputEventJoypadButton.new()
	if device=="keyboard":ev.physical_keycode=code
	else:ev.button_index=code
	InputMap.action_add_event(action,ev)
func label(action,device=""):
	if device=="":device=last_device
	for ev in InputMap.action_get_events(action):
		if device=="keyboard" and ev is InputEventKey:return OS.get_keycode_string(ev.physical_keycode)
		if device=="controller" and ev is InputEventJoypadButton:
			var names={0:"A / Cross",1:"B / Circle",2:"X / Square",3:"Y / Triangle",4:"View / Select",6:"Menu / Start",9:"LB / L1",10:"RB / R1",13:"D-pad left",14:"D-pad right"}
			return names.get(ev.button_index,"Button "+str(ev.button_index))
	return "Unassigned"
func begin_bind(action):
	rebind_action=action;notice="Press a key or controller button. Esc / Start cancels."
func observe(event):
	if event is InputEventKey and event.pressed and not event.echo:last_device="keyboard"
	elif event is InputEventJoypadButton and event.pressed:last_device="controller"
	elif event is InputEventJoypadMotion and absf(event.axis_value)>.45:last_device="controller"
	if rebind_action=="":return false
	if event is InputEventKey and event.pressed:
		if event.echo:return true
		var code=event.physical_keycode if event.physical_keycode else event.keycode
		if code==KEY_ESCAPE:rebind_action="";notice="Binding cancelled.";return true
		if bind_device=="keyboard":try_bind(rebind_action,bind_device,code)
	elif event is InputEventJoypadButton and event.pressed:
		if event.button_index==JOY_BUTTON_START:rebind_action="";notice="Binding cancelled.";return true
		if bind_device=="controller":try_bind(rebind_action,bind_device,event.button_index)
	return true
func try_bind(action,device,code,persist=true):
	if action not in ACTIONS or device not in bindings:return false
	if (device=="keyboard" and (code<=0 or code in [KEY_ESCAPE,KEY_ENTER,KEY_KP_ENTER,KEY_F,KEY_F11,KEY_M])) or (device=="controller" and (code<0 or code>=JOY_BUTTON_MAX or code==JOY_BUTTON_START)):
		notice="Reserved for menu, fullscreen or mute. Choose another input.";return false
	for other in ACTIONS:
		if other==action:continue
		for ev in InputMap.action_get_events(other):
			if (device=="keyboard" and ev is InputEventKey and ev.physical_keycode==code) or (device=="controller" and ev is InputEventJoypadButton and ev.button_index==code):
				notice="Already used by "+NAMES[other]+". Choose another input or reset controls.";return false
	bindings[device][action]=code;_replace(action,device,code);rebind_action="";crouch_latched=false
	notice=NAMES[action]+" is now "+label(action,device)+"."
	if persist:save_settings()
	return true
func crouch_pressed():return crouch_latched if crouch_toggle else Input.is_action_pressed("crouch")
func reset():
	g.volume=.6;g.muted=false;g.reduced_motion=false;text_scale=1.0;crouch_toggle=false;crouch_latched=false
	mix={"Music":.8,"Weather":.9,"Actions":1.0,"Threat":1.0};bindings={"keyboard":{},"controller":{}};rebind_action="";install();g.apply_volume();notice="Default settings and controls restored. Journey saves kept.";save_settings()
func data():return {"schema":2,"volume":g.volume,"muted":g.muted,"reduced_motion":g.reduced_motion,"text_scale":text_scale,"crouch_toggle":crouch_toggle,"mix":mix,"bindings":bindings}
func save_settings(force=false):
	if g.smoke_test and not force:return false
	var f=FileAccess.open(g.settings_path+".tmp",FileAccess.WRITE)
	if f==null:notice="Could not save settings.";return false
	f.store_string(JSON.stringify(data(),"\t"));f.close()
	if read_prefs(g.settings_path)!=null:DirAccess.copy_absolute(g.settings_path,g.settings_path+".bak")
	var err=DirAccess.rename_absolute(g.settings_path+".tmp",g.settings_path)
	if err!=OK:notice="Could not finish saving settings; previous file kept."
	return err==OK
func read_prefs(path):
	if not FileAccess.file_exists(path):return null
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK:return null
	var d=parser.data
	return d if d is Dictionary else null
func load_settings():
	var d=read_prefs(g.settings_path)
	if d==null:d=read_prefs(g.settings_path+".bak")
	if d==null:return
	for key in ["volume","text_scale"]:
		var v=d.get(key,.6 if key=="volume" else 1.0)
		if (v is int or v is float) and is_finite(float(v)):
			if key=="volume":g.volume=clampf(float(v),0,1)
			else:text_scale=clampf(float(v),1,1.4)
	if d.get("muted",false) is bool:g.muted=d.get("muted",false)
	if d.get("reduced_motion",false) is bool:g.reduced_motion=d.get("reduced_motion",false)
	if d.get("crouch_toggle",false) is bool:crouch_toggle=d.get("crouch_toggle",false)
	if d.get("mix") is Dictionary:
		for key in mix:
			var v=d.mix.get(key,mix[key])
			if (v is int or v is float) and is_finite(float(v)):mix[key]=clampf(float(v),0,1)
	bindings={"keyboard":{},"controller":{}}
	if d.get("bindings") is Dictionary:
		for device in bindings:
			var proposed={};var source=d.bindings.get(device,{})
			if not source is Dictionary:continue
			for action in ACTIONS:
				var v=source.get(action)
				if not (v is int or v is float) or not is_finite(float(v)):continue
				var code=int(v)
				if device=="keyboard" and code>0 and code not in [KEY_ESCAPE,KEY_ENTER,KEY_KP_ENTER,KEY_F,KEY_F11,KEY_M]:proposed[action]=code
				if device=="controller" and code>=0 and code<JOY_BUTTON_MAX and code!=JOY_BUTTON_START:proposed[action]=code
			var used={};var conflict=false
			for action in ACTIONS:
				var codes=[proposed[action]] if proposed.has(action) else (KEYS[action] if device=="keyboard" else ([PADS[action]] if PADS.has(action) else []))
				for code in codes:
					if used.has(code):conflict=true
					used[code]=true
			if not conflict:bindings[device]=proposed
	install();notice="";crouch_latched=false;g.apply_volume()
