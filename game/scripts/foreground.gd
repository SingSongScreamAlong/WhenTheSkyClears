extends Node2D
var game
func _ready(): texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
func _process(_dt): queue_redraw()
func _draw():
	if game==null or game.world==null or game.level.is_empty(): return
	for c in game.level.covers:
		if c.kind=="wall":
			game.world.paint_asset(self,"wall",Vector2(c.x,float(c.get("y",game.surface_y_at(c.x,700)))+5),c.w+20,82,Color(.48,.57,.55))
	# Foot-level foreground accents sit in front of the actors; major scenery
	# stays behind them, so stealth reads without hiding the route.
	var left=game.camera.position.x-800
	for i in range(maxi(0,int((left-40)/67)),int(minf(float(game.level.width),left+1660)/67)+1):
		var x=i*67.0+game.world.noise_at(i*2)*21
		if not game.ground_at(x): continue
		var y=float(game.surface_y_at(x,700))
		var wind=sin(game.clock*1.3+i)*2
		var height=4+game.world.noise_at(i)*7
		var theme=game.world.zone_at(x)
		if theme=="school_courtyard" or theme=="rail_yard": height*=.5
		draw_polyline(PackedVector2Array([Vector2(x,y+3),Vector2(x+wind+2,y-height*.5),Vector2(x+wind+5,y-height)]),Color(.10,.16,.14,.65),1.1,true)
		if theme=="rain_gully" and i%7==0:
			for reed in range(3):
				var bend=wind*(1+reed*.3)
				draw_polyline(PackedVector2Array([Vector2(x+reed*4,y+3),Vector2(x+reed*4+bend,y-11),Vector2(x+reed*4+bend*2,y-19+reed*3)]),Color(.12,.20,.16,.52),.8,true)
