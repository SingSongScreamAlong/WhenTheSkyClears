extends Node

# Authored adaptation beats. No relationship, spoken dialogue, or trauma event
# is inferred here. The ordinary act changes meaning across the existing road.
var game
var data = JSON.parse_string(FileAccess.get_file_as_string("res://story/moments.json"))
var active = false
var final_moment = false
var elapsed = 0.0
var current = {}
var old_following = true
var final_target_x = 0.0
var hud_presence = 1.0

func reset():
	active = false
	final_moment = false
	elapsed = 0.0
	current = {}
	hud_presence = 1.0

func available():
	for moment in data.moments:
		if int(moment.chapter) != game.chapter or game.flags.get(moment.id, false): continue
		if absf(game.player.position.x - float(moment.x)) > 58: continue
		if absf(game.player.position.y - float(moment.y)) > 35: continue
		var permitted = true
		for key in moment.get("requires", []):
			if not game.flags.get(key, false): permitted = false
		if permitted: return moment
	return {}

func can_begin():
	return game.player.is_on_floor() and game.boy.is_on_floor() and absf(game.player.position.x-game.boy.position.x) < 65 and absf(game.player.position.y-game.boy.position.y) < 18 and game.in_safe_zone(game.player.position.x) and game.in_safe_zone(game.boy.position.x) and game.player.can_stand() and game.boy.can_stand()

func begin(moment):
	if not can_begin():
		game.announce_message("Bring him close, under the same roof.  [Q]", 3)
		return
	current = moment.duplicate(true)
	active = true; final_moment = false; elapsed = 0.0
	old_following = game.boy.following
	settle()
	game.mode = "stillness"
	game.message_time = 0
	game.hud.selected = 0

func begin_final():
	current = data.final.duplicate(true)
	if not game.flags.get("care_village", false): current.lines = current.unfamiliar_lines
	active = true; final_moment = true; elapsed = 0.0
	old_following = game.boy.following
	final_target_x = minf(game.player.position.x+42, float(game.level.width)-65)
	settle()
	game.message_time = 0
	game.hud.selected = 0

func settle():
	game.pending_action = {}; game.action_progress = 0
	for child in [game.player, game.boy]:
		child.velocity = Vector2.ZERO
		child.action_time = 0; child.ai_jump = false; child.leap_axis = 0
		child.crouching = false; child.forced_crouch = false
		child.col.shape.size.y = 99.0 if child.is_girl else 84.0
		child.col.position.y = -child.col.shape.size.y/2

func finish():
	if not active: return
	if not final_moment:
		game.flags[current.id] = true
		game.mode = "playing"
	game.boy.following = old_following
	active = false
	game.player.velocity = Vector2.ZERO; game.boy.velocity = Vector2.ZERO
	game.player.hand_active = false; game.boy.hand_active = false
	game.write_save()

func visible_line():
	if not active or elapsed < 1.1: return ""
	if final_moment and elapsed < 6.8: return str(current.lines[0])
	return str(current.lines[0] if elapsed < 4.8 else current.lines[1])

func kept_pages():
	var pages = []
	for moment in data.moments:
		if game.flags.get(moment.id, false): pages.append(str(moment.kept))
	for line in game.memories.values(): pages.append(str(line))
	return pages

func _process(dt):
	if game == null: return
	if game.mode == "playing":
		var needed = game.always_show_hud or game.health < 60 or game.warmth < 45 or game.food < 40 or game.wetness > .12 or game.shell_warning > 0 or game.exposure > .1 or game.lane_warning != "" or game.chapter_card > 0
		hud_presence = move_toward(hud_presence, 1.0 if needed else .0, dt*.65)
	if active and game.mode in ["stillness", "ending"]: elapsed += dt
	# Sound recedes over several seconds; warnings and footsteps retain their
	# independent levels. Settings and the player's mute remain authoritative.
	if is_instance_valid(game.ambience):
		var db = -25.0 if active else (-14.0 if game.chapter == 0 else -18.0)
		game.ambience.volume_db = lerpf(game.ambience.volume_db, db, 1-exp(-dt*.7))

func _physics_process(dt):
	if not active or not game.mode in ["stillness", "ending"]: return
	var walking = final_moment and elapsed > 3.2 and game.boy.position.x < final_target_x-1
	if walking:
		game.boy.facing = 1
		# Use the native controller and planted-foot solver for this synchronous
		# tick. Other world nodes remain held in ending mode throughout the beat.
		var held_mode = game.mode
		game.mode = "playing"
		game.boy.ai_axis = .26; game.boy.ai_jump = false
		game.boy._physics_process(dt)
		game.mode = held_mode
	else: game.boy.velocity = Vector2.ZERO
	var gap = game.boy.position.x-game.player.position.x
	game.player.facing = signf(gap) if absf(gap)>8 else game.player.facing
	if not walking: game.boy.facing = -signf(gap) if absf(gap)>8 else 1
	var contact = (game.player.position+game.boy.position)*.5+Vector2(0,-53)
	for child in [game.player, game.boy]:
		child.hand_active = not walking and absf(gap)<65
		child.contact_hand = contact
		if not walking or child != game.boy: child.update_animation(dt)
	# The held frame belongs to the player; there is no automatic exit or reward.
