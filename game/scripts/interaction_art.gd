extends RefCounted

# Original painted sprites remain intact. Source rectangles separate the lever
# so the work animation rotates around its actual bearing, not the whole pump.
var atlas=preload("res://assets/props/Interaction_Props_v041.png")
var regions={
	"rations":Rect2(25,49,516,390),
	"medicine":Rect2(594,43,394,411),
	"scrap":Rect2(1022,77,506,374),
	"pump":Rect2(54,435,384,554),
	"lever":Rect2(505,669,582,108),
	"lantern":Rect2(1171,475,260,487)
}
var states={}
var chapter=-1
const PUMP_REST_ANGLE=PI-.36

func tick(game,dt):
	if game==null or game.level.is_empty(): return
	if chapter!=game.chapter:
		chapter=game.chapter; states.clear()
	if game.mode!="playing": return
	for item in game.level.get("interact",[]):
		var id=str(item.get("id",""))
		var used=bool(game.flags.get(id,false))
		if not states.has(id): states[id]={"settled":1.0 if used else 0.0,"cycle":0.0}
		var state=states[id]
		state.settled=move_toward(float(state.settled),1.0 if used else 0.0,dt*2.4)
		var working=not game.pending_action.is_empty() and str(game.pending_action.get("id",""))==id
		if working: state.cycle+=dt
		else: state.cycle=move_toward(float(state.cycle),0.0,dt*5)

func progress(game,item):
	if game.pending_action.is_empty() or str(game.pending_action.get("id",""))!=str(item.get("id","")): return 0.0
	return clampf(game.action_progress/maxf(.01,game.action_duration),0,1)

func settled(game,item):
	var id=str(item.get("id",""))
	return float(states.get(id,{}).get("settled",1.0 if game.flags.get(id,false) else 0.0))

func paint(canvas,key,bottom,width,tint=Color.WHITE):
	var source=regions[key]
	var height=width*source.size.y/source.size.x
	canvas.draw_texture_rect_region(atlas,Rect2(bottom-Vector2(width*.5,height),Vector2(width,height)),source,tint)

func cache_contents(game,item):
	var remaining=game.cache_remaining.get(str(item.get("id","")),{})
	var resources=[]
	for resource in ["rations","medicine","scrap"]:
		if int(remaining.get(resource,item.get(resource,0)))>0: resources.append(resource)
	return resources

func draw_cache(canvas,game,item,pos):
	var contents=cache_contents(game,item)
	var used=bool(game.flags.get(item.get("id",""),false))
	if used or contents.is_empty():
		# Leave a quiet, empty timber container as a persistent search history.
		canvas.paint_asset(canvas,"crate",pos+Vector2(0,4),37,24,Color(.48,.48,.41,.68))
		return
	var widths={"rations":52.0,"medicine":32.0,"scrap":47.0}
	var span=(contents.size()-1)*31.0
	for index in range(contents.size()):
		var resource=contents[index]
		var bottom=pos+Vector2(index*31-span*.5,3)
		canvas.contact_shadow(canvas,bottom,18,.19)
		paint(canvas,resource,bottom,widths[resource],Color(.94,.95,.90))
	# The rummage is local to the cloth edge; the whole supply box never bobs.
	var work=progress(game,item)
	if work>0:
		var at=pos+Vector2(-8,-15)
		canvas.draw_line(at,at+Vector2(14,sin(game.action_progress*9)*1.5),Color(.78,.74,.61,.65),1.2,true)

func pump_angle(game,item):
	var id=str(item.get("id",""))
	var cycle=float(states.get(id,{}).get("cycle",0))
	return PUMP_REST_ANGLE+sin(cycle*5.2)*.27 if progress(game,item)>0 else PUMP_REST_ANGLE

func draw_pump(canvas,game,item,pos):
	# Put the mechanism beside the two-person working space. Its left-facing
	# handle reaches their hands while the iron body remains visible.
	canvas.contact_shadow(canvas,pos+Vector2(45,3),29,.28)
	paint(canvas,"pump",pos+Vector2(45,5),62,Color(.94,.98,.95))
	# The sprite's circular bearing is 9% from its left edge, 38% down.
	var pivot=pos+Vector2(54,-79)
	canvas.draw_set_transform(pivot,pump_angle(game,item),Vector2.ONE)
	canvas.draw_texture_rect_region(atlas,Rect2(-9,-6,104,18),regions.lever,Color(.97,.96,.90))
	canvas.draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	canvas.draw_circle(pivot,2.0,Color(.35,.39,.34))
	var work=progress(game,item)
	if work>0:
		var cycle=float(states.get(str(item.id),{}).get("cycle",0))
		for drop in range(5):
			var phase=fposmod(cycle*1.3+drop*.20,1)
			var at=pos+Vector2(17-phase*9,-52+phase*49)
			canvas.draw_line(at,at+Vector2(-.5,3.0),Color(.64,.76,.72,(1-phase)*.48),1.2,true)
	if int(item.get("scrap_cost",0))>0:
		var opened=settled(game,item)
		for zone in game.level.get("water_zones",[]):
			if zone.get("key","")==item.id:
				opened=clampf(float(game.water_offsets.get(item.id,0))/62.0,0,1)
				break
		var lift=46*opened
		canvas.paint_beam(pos+Vector2(117,8),pos+Vector2(117,-104),9,Color(.63,.67,.55))
		canvas.paint_beam(pos+Vector2(170,8),pos+Vector2(170,-108),9,Color(.63,.67,.55))
		for plank in range(4):
			canvas.paint_beam(pos+Vector2(118,-12-plank*16-lift),pos+Vector2(170,-14-plank*16-lift),12,Color(.65,.66,.53))
		var chain=PackedVector2Array()
		for n in range(17):
			var t=n/16.0
			chain.append(pos+Vector2(54,-79).lerp(Vector2(143,-105),t)+Vector2(0,sin(t*PI)*5*(1-opened)))
		canvas.draw_polyline(chain,Color(.28,.32,.26,.85),2,true)
		canvas.draw_polyline(chain,Color(.69,.67,.53,.46),.7,true)
		canvas.draw_arc(pos+Vector2(143,-105),5,0,TAU,16,Color(.44,.47,.37),2,true)
		canvas.draw_line(pos+Vector2(143,-100),pos+Vector2(143,-60-lift),Color(.53,.55,.43),1.6,true)

func draw_lantern(canvas,game,pos,scale=1.0):
	paint(canvas,"lantern",pos,17*scale,Color(.98,.97,.89))
	var flame=pos+Vector2(0,-11*scale)
	canvas.glow(flame,Color(.98,.69,.32),48*scale,.12+sin(game.clock*4.3)*.008)
