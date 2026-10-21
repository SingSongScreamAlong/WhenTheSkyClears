extends Node2D
var game
func _ready(): texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
func _process(_dt): queue_redraw()
func _draw():
	if game==null or game.world==null or game.level.is_empty(): return
	for mill in game.get("mill_encounters") if game.get("mill_encounters")!=null else []:
		if is_instance_valid(mill): mill.draw_foreground(self)
	for sluice in game.get("sluice_encounters") if game.get("sluice_encounters")!=null else []:
		if is_instance_valid(sluice): sluice.draw_foreground(self)
	for trolley in game.get("trolley_encounters") if game.get("trolley_encounters")!=null else []:
		if is_instance_valid(trolley): trolley.draw_foreground(self)
	for puzzle in game.puzzle_encounters:
		if is_instance_valid(puzzle) and puzzle.has_method("draw_foreground"): puzzle.draw_foreground(self)
	for c in game.level.covers:
		if c.kind=="wall" and not c.get("rear_plane",false):
			game.world.paint_asset(self,"wall",Vector2(c.x,float(c.get("y",game.surface_y_at(c.x,700)))+5),c.w+20,82,Color(.56,.65,.63))
	# Foot-level foreground accents sit in front of the actors; major scenery
	# stays behind them, so stealth reads without hiding the route.
	var left=game.camera.position.x-800
	for i in range(maxi(0,int((left-40)/67)),int(minf(float(game.level.width),left+1660)/67)+1):
		var x=i*67.0+game.world.noise_at(i*2)*21
		if not game.ground_at(x) or game.world.near_route_focus(x): continue
		var y=float(game.surface_y_at(x,700))
		var wind=sin(game.clock*1.3+i)*2+game.world.foliage_displacement(x,y)
		var height=3+game.world.noise_at(i)*5
		var theme=game.world.zone_at(x)
		if theme in ["school_courtyard","rail_yard","shattered_arcade","signal_yard","drainage_tunnel"]: height*=.5
		draw_polyline(PackedVector2Array([Vector2(x,y+3),Vector2(x+wind+2,y-height*.5),Vector2(x+wind+5,y-height)]),Color(.10,.16,.14,.65),1.1,true)
		if theme in ["rain_gully","canal"] and i%7==0:
			for reed in range(3):
				var bend=wind*(1+reed*.3)
				draw_polyline(PackedVector2Array([Vector2(x+reed*4,y+3),Vector2(x+reed*4+bend,y-11),Vector2(x+reed*4+bend*2,y-19+reed*3)]),Color(.12,.20,.16,.52),.8,true)
	# These small foreground arcs sit over the ankles only where water is
	# physically deep enough. The dry raised route keeps its clear silhouette.
	for water in game.level.get("water_zones",[]):
		var water_y=float(water.top)+float(game.water_offsets.get(water.key,0))
		for child in [game.player,game.boy]:
			if child==null or child.position.x<water.x or child.position.x>water.x+water.w: continue
			if child.position.y<water_y-3 or child.position.y>water_y+84: continue
			var speed=clampf(absf(child.velocity.x)/90.0,0,1)
			var spread=fposmod(game.clock*1.25+child.position.x*.01,1.0)
			draw_set_transform(Vector2(child.position.x,water_y+2),0,Vector2(1,.20))
			for ring in range(2):
				var radius=9+spread*12+ring*7
				draw_arc(Vector2.ZERO,radius,0,PI,18,Color(.43,.59,.55,(.14+.09*speed)*(1-spread)),1.3,true)
			draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
