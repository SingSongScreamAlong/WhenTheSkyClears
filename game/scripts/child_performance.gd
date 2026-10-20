extends RefCounted
# Visual timing only. The native CharacterBody, input and collision sizes own
# movement. Root motion and gameplay routes are never changed by these poses.
var c
var crouch_blend=0.0
var start_remaining=0.0
var stop_remaining=0.0
var turn_remaining=0.0
var moving_before=false
var facing_before=1.0
var floor_before=false
var vertical_before=0.0
var impact=0.4
func _init(child):c=child;facing_before=c.facing
func update(dt):
	var active=c.game!=null and c.game.slice_active
	if not active:return
	var moving=absf(c.velocity.x)>10
	if moving and not moving_before and c.is_on_floor():start_remaining=.18
	if not moving and moving_before and c.is_on_floor():stop_remaining=.24
	if c.facing!=facing_before:turn_remaining=.22
	if c.is_on_floor() and not floor_before:impact=clampf(vertical_before/600.0,.25,1.0)
	start_remaining=maxf(0,start_remaining-dt);stop_remaining=maxf(0,stop_remaining-dt);turn_remaining=maxf(0,turn_remaining-dt)
	crouch_blend=lerpf(crouch_blend,1.0 if c.crouching else 0.0,1-exp(-dt*18))
	moving_before=moving;facing_before=c.facing;floor_before=c.is_on_floor();vertical_before=c.velocity.y
func offset():
	var start=sin(clampf(start_remaining/.18,0,1)*PI)
	var stop=sin(clampf(stop_remaining/.24,0,1)*PI)
	var turn=sin(clampf(turn_remaining/.22,0,1)*PI)
	return {"hip":Vector2(c.facing*(start-stop)*1.3,start*1.4+stop*.8+turn*.7),"shoulder":Vector2(c.facing*(start*3-stop*2.8-turn*2.0),start*1.3+stop*1.5+turn*.8),"tilt":c.facing*(turn*.05-stop*.03)}
