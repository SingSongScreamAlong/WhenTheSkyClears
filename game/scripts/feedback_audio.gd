extends Node
# Original synthesized rain/cloth and the existing project cues/CC0 footsteps.
# All spatial sources use the camera listener (Godot's default screen center).
var g
var exterior
var interior
var indoor=0.0
var duck=0.0
var cooldown={}
var voices=[]
var caption=""
var caption_time=0.0
var audit_enabled=false
var events=[]
var last_sweep=-10.0
var shutting_down=false
var bus_names=["Music","Weather","Actions","Threat"]
func _init(game):g=game
func setup():
	for name in bus_names:
		if AudioServer.get_bus_index("WTSC"+name)<0:
			AudioServer.add_bus();var idx=AudioServer.bus_count-1;AudioServer.set_bus_name(idx,"WTSC"+name);AudioServer.set_bus_send(idx,"Master")
	exterior=loop_player("rain_open",-80);interior=loop_player("rain_roof",-80)
func loop_player(name,db):
	var a=AudioStreamPlayer.new();a.stream=load("res://assets/audio/"+name+".wav");a.stream.loop_mode=AudioStreamWAV.LOOP_FORWARD;a.stream.loop_end=int(a.stream.get_length()*a.stream.mix_rate);a.bus="WTSCWeather";a.volume_db=db;add_child(a);return a
func allowed():return not g.smoke_test or audit_enabled
func apply():
	AudioServer.set_bus_volume_db(0,linear_to_db(maxf(g.volume,.00001)));AudioServer.set_bus_mute(0,g.muted or g.volume<=0)
	for name in bus_names:
		var idx=AudioServer.get_bus_index("WTSC"+name)
		if idx>=0:
			AudioServer.set_bus_volume_db(idx,linear_to_db(maxf(float(g.access.mix[name]),.00001)))
			AudioServer.set_bus_mute(idx,float(g.access.mix[name])<=0)
func tick(dt):
	if shutting_down:return
	caption_time=maxf(0,caption_time-dt);duck=maxf(0,duck-dt)
	var active=g.slice_active and allowed()
	if active:
		if not exterior.playing:exterior.play();interior.play()
		var roof=(float(g.in_safe_zone(g.player.position.x,g.player.position.y))+float(g.in_safe_zone(g.boy.position.x,g.boy.position.y)))*.5
		indoor=lerpf(indoor,roof,1-exp(-dt*2.8))
		var pause_db=0 if g.mode=="playing" else -8
		exterior.volume_db=lerpf(-19,-36,indoor)+pause_db-(9 if duck>0 else 0)
		interior.volume_db=lerpf(-38,-23,indoor)+pause_db-(9 if duck>0 else 0)
	else:
		exterior.stop();interior.stop();indoor=0
	if is_instance_valid(g.ambience):g.ambience.volume_db=-14-(6 if g.slice_active else 0)-(7 if duck>0 else 0)
	voices=voices.filter(func(a):return is_instance_valid(a))
	for a in voices:a.stream_paused=g.mode not in ["playing","settings"]
	if g.slice_active and g.mode=="playing" and allowed():
		var x=g.player.position.x
		var beam=g.last_house.shop_beam_x() if x<3450 else g.last_house.beam_x()
		var in_lane=(x>1950 and x<3250 and g.player.position.y<650) or (x>5400 and x<7200)
		if in_lane and absf(beam-x)<340 and g.playtime-last_sweep>5 and not g.sheltered:
			last_sweep=g.playtime
			cue("warning",-14,Vector2(beam,650),"LIGHT "+("LEFT" if beam<x else "RIGHT")+" - COVER BOTH CHILDREN")
func cue(name,db=-12,at=null,text="",stream=null):
	if not allowed():return null
	var now=Time.get_ticks_msec()/1000.0
	if now-float(cooldown.get(name,-100))<(.32 if name=="warning" else .07):return null
	cooldown[name]=now
	var threat=name in ["warning","blast"]
	var bus="WTSCThreat" if threat else "WTSCActions"
	voices=voices.filter(func(a):return is_instance_valid(a))
	var same=voices.filter(func(a):return a.bus==bus)
	if same.size()>=(2 if threat else 6):same[0].stop();same[0].queue_free();voices.erase(same[0])
	var spatial=g.slice_active
	var a=AudioStreamPlayer2D.new() if spatial else AudioStreamPlayer.new()
	a.stream=stream if stream!=null else g.sfx.get(name)
	if a.stream==null:a.free();return null
	a.bus=bus;a.volume_db=db-(6 if not threat and duck>0 else 0);a.pitch_scale=randf_range(.97,1.03) if name=="step" else 1.0
	if spatial:a.position=g.player.position if at==null else at;a.max_distance=1800;a.panning_strength=1.0
	add_child(a);a.finished.connect(a.queue_free);a.play();voices.append(a)
	if threat:duck=2.4
	if text!="":caption=text;caption_time=3.0
	if events.size()>127:events.pop_front()
	events.append({"name":name,"bus":bus,"spatial":spatial,"at":str(at),"db":a.volume_db,"caption":text,"time":g.playtime})
	return a
func stop_all():
	shutting_down=true
	for a in voices:
		if is_instance_valid(a):a.stop();a.stream=null;a.queue_free()
	voices.clear()
	for a in [exterior,interior]:
		if is_instance_valid(a):a.stop();a.stream=null
