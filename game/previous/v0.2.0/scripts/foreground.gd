extends Node2D
var game
func _ready(): texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
func _process(_dt): queue_redraw()
func _draw():
	if game==null or game.world==null or game.level.is_empty(): return
	for c in game.level.covers:
		if c.kind=="wall":
			game.world.paint_asset(self,"wall",Vector2(c.x,705),c.w+20,82,Color(.48,.57,.55))
	# Foot-level foreground accents sit in front of the actors; major scenery
	# stays behind them, so stealth reads without hiding the route.
	var left=game.camera.position.x-800
	for i in range(85):
		var x=i*73.0
		if x<left or x>left+1600 or not game.ground_at(x): continue
		var wind=sin(game.clock*1.3+i)*2
		draw_polyline(PackedVector2Array([Vector2(x,707),Vector2(x+wind+4,693),Vector2(x+wind+10,687)]),Color(.12,.2,.18,.85),1.9,true)
