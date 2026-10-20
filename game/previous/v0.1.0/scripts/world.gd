extends Node2D

var game
var textures = {}
var bounds = {}
var rng = RandomNumberGenerator.new()
var grasses = []
var rocks = []
var font = preload("res://assets/fonts/display.ttf")

func _ready():
	for key in ["Sky_Painted", "Distant_Hills", "Village_Warm", "Village_Empty", "Woods", "Camp", "School", "Battlefield", "Foreground_Tree", "Ground_Painted"]:
		var tex = load("res://assets/environments/" + key + "_v001.png")
		textures[key] = tex
		bounds[key] = tex.get_image().get_used_rect()
	# Ignore faint matte pixels around the original paint layers. These source
	# rectangles retain every visible painted edge and align feet to the route.
	var painted_bounds={"Battlefield":Rect2(0,133,1672,690),"Camp":Rect2(1,391,1670,349),"Distant_Hills":Rect2(0,505,1672,436),"Foreground_Tree":Rect2(35,6,1470,993),"School":Rect2(10,174,1648,575),"Village_Empty":Rect2(0,180,1671,600),"Village_Warm":Rect2(1,182,1669,599),"Woods":Rect2(0,59,1672,724)}
	for key in painted_bounds: bounds[key]=painted_bounds[key]
	rng.seed = 271019
	for i in range(1450): grasses.append(Vector3(rng.randf_range(0,6000),rng.randf_range(5,23),rng.randf_range(-10,10)))
	for i in range(350): rocks.append(Vector3(rng.randf_range(0,6000),rng.randf_range(3,13),rng.randf_range(2,9)))

func art(key, x, bottom, width, tint = Color.WHITE):
	var r = bounds[key]
	var h = width * float(r.size.y)/float(r.size.x)
	draw_texture_rect_region(textures[key],Rect2(x,bottom-h,width,h),r,tint)

func scenery(key, factor, width, bottom, tint):
	var left = game.camera.position.x - 800
	var offset = fposmod(-left*factor,width)
	for i in range(-1,2): art(key,left+offset+i*width,bottom,width,tint)

func _process(_dt): queue_redraw()

func _draw():
	if game == null or game.level.is_empty(): return
	var l = game.level
	var cx = game.camera.position.x
	var left = cx-800
	var t = game.clock
	var sky = Color(l.sky)
	draw_rect(Rect2(left-100,-350,1800,1500),sky)
	var sky_tint = [Color(1, .91, .74, .72),Color(.56,.72,.75,.66),Color(.44,.55,.61,.67),Color(.39,.50,.58,.7),Color(.7,.74,.77,.48)][game.chapter]
	draw_texture_rect(textures.Sky_Painted,Rect2(left-100,-180,1800,1050),false,sky_tint)
	# Quiet shafts of light, painted horizons, and independent depth planes.
	var ray_col = Color(.9,.86,.65,.05) if game.chapter == 0 else Color(.65,.77,.83,.025)
	for i in range(5):
		var x = left+fposmod(190+i*386-left*.04,1800)-100
		draw_colored_polygon(PackedVector2Array([Vector2(x,-40),Vector2(x+45,-40),Vector2(x-160,760),Vector2(x-460,760)]),ray_col)
	scenery("Distant_Hills",.12,2100,710,Color(.65,.74,.77,.72))
	var haze = Color(l.fog)
	draw_rect(Rect2(left,430,1600,380),Color(haze,.18))
	match game.chapter:
		0:
			scenery("Village_Warm",.48,1750,692,Color(.82,.83,.71,.88))
			art("Woods",4100,703,1600,Color(.44,.56,.48,.8))
		1:
			scenery("Woods",.38,1800,715,Color(.44,.57,.56,.9))
			scenery("Woods",.65,2100,720,Color(.37,.47,.46,.8))
		2:
			scenery("Battlefield",.24,2150,685,Color(.44,.52,.58,.8))
			scenery("Camp",.61,1700,703,Color(.64,.68,.7,.85))
		3:
			scenery("Battlefield",.26,2200,700,Color(.54,.61,.66,.9))
			art("School",980,700,1760,Color(.73,.76,.77,.9))
			art("Village_Empty",3400,705,1900,Color(.48,.57,.61,.85))
		4:
			scenery("Battlefield",.22,2500,700,Color(.53,.60,.65,.7))
			# Monumental title forms belong to the world, behind the traversable bases.
			for pair in [["WHEN",1700,435],["THE SKY",2950,460],["CLEARS",4330,420]]:
				draw_string(font,Vector2(pair[1],pair[2]),pair[0],HORIZONTAL_ALIGNMENT_LEFT,-1,210,Color(.12,.18,.21,.71))
	# Soft near-ground mist makes charcoal contacts readable.
	for j in range(9):
		draw_rect(Rect2(left,535+j*19,1600,20),Color(haze,.012+j*.004))
	if l.get("searchlight",false):
		var bx = game.beam_x()
		draw_colored_polygon(PackedVector2Array([Vector2(bx-260,-200),Vector2(bx-115,720),Vector2(bx+130,720)]),Color(.84,.88,.72,.14))
		draw_line(Vector2(bx-260,-200),Vector2(bx+125,720),Color(.9,.91,.72,.08),2,true)
	# Craters have atmospheric depth, rather than exposing a repeated sky image.
	draw_rect(Rect2(left,700,1600,600),Color("34474a") if game.chapter>1 else Color("39463c"))
	for i in range(10): draw_rect(Rect2(left,720+i*28,1600,29),Color(.04,.08,.09,.035+i*.035))
	for g in l.ground: terrain(g,true)
	for p in l.platforms: terrain(p,false)
	for c in l.covers: cover(c)
	for p in l.props: prop(p)
	for p in l.interact: interact_prop(p)
	for g in l.gates: gate(g)
	for m in l.memories:
		if not game.memories.has(m.id):
			var pos = Vector2(m.x,m.y-12+sin(t*2+m.x)*4)
			glow(pos,Color(.67,.79,.84),18,.1)
			draw_colored_polygon(PackedVector2Array([pos+Vector2(-5,-7),pos+Vector2(6,-5),pos+Vector2(4,6),pos+Vector2(-6,5)]),Color("c9d3c8"))
	for cp in l.checkpoints:
		draw_line(Vector2(cp-22,700),Vector2(cp-22,655),Color(.18,.25,.24),3,true)
		glow(Vector2(cp-22,654),Color(.88,.69,.36),11,.15)
		draw_circle(Vector2(cp-22,654),2,Color("d9b975"))
	for g in grasses:
		if g.x < left-30 or g.x>left+1630 or not game.ground_at(g.x): continue
		var wind = sin(t*1.4+g.x*.028)*3
		draw_polyline(PackedVector2Array([Vector2(g.x,702),Vector2(g.x+g.z*.4+wind,700-g.y*.65),Vector2(g.x+g.z+wind*2,700-g.y)]),Color(.13,.19,.18,.83),1.6,true)
	for r in rocks:
		if r.x < left or r.x>left+1600 or not game.ground_at(r.x): continue
		draw_colored_polygon(PackedVector2Array([Vector2(r.x,702),Vector2(r.x-r.y,696),Vector2(r.x-1,696-r.z),Vector2(r.x+r.y,701)]),Color(.17,.22,.21))
	# Original painted foreground oaks move on their own parallax plane.
	if game.chapter <= 1:
		for i in range(2):
			var x=left+fposmod(i*1800-left*1.13,3600)-1050
			art("Foreground_Tree",x,808,1040,Color(.08,.14,.12,.77))
	if game.shell_warning > 0:
		draw_rect(Rect2(left,-100,1600,1100),Color(.77,.68,.48,game.shell_warning*.05))
	if game.flash>0: draw_rect(Rect2(left,-300,1600,1500),Color(.82,.85,.75,game.flash*.17))
	# Fine drifting particles are deterministic; no imported stock particle effects.
	for i in range(100):
		var x = left+fposmod(i*97.3+t*(8+i%7)-left*.18,1640)-20
		var y = fposmod(i*53.3+t*(2+i%5),760)
		draw_circle(Vector2(x,y),.5+(i%3)*.35,Color(.85,.88,.77,.08+(i%4)*.025))
	if game.chapter == 3:
		for i in range(140):
			var x = left+fposmod(i*47.4+t*170,1700)-60
			var y = fposmod(i*77.6+t*790,920)-40
			draw_line(Vector2(x,y),Vector2(x-5,y+19),Color(.7,.8,.86,.13),.8,true)
	for p in game.dust:
		draw_circle(p.p,p.size,Color(.65,.65,.51,p.life*.3))

func terrain(p, earth):
	var x = float(p.x)
	var y = float(p.y)
	var w = float(p.w)
	var ink = Color("182120") if game.chapter < 2 else Color("182126")
	if earth:
		var polygon = PackedVector2Array([Vector2(x,y+400)])
		for i in range(int(w/16)+1):
			var xx = minf(x+w,x+i*16)
			polygon.append(Vector2(xx,y+2*sin(xx*.13)+sin(xx*.37)))
		polygon.append(Vector2(x+w,y));polygon.append(Vector2(x+w,y+500))
		draw_colored_polygon(polygon,ink)
		for i in range(int(w/55)):
			var xx = x+i*55+13
			draw_line(Vector2(xx,y+4),Vector2(xx+16,y+6),Color(.4,.44,.35,.24),2,true)
	else:
		draw_rect(Rect2(x,y,w,p.h),ink)
		draw_line(Vector2(x,y),Vector2(x+w,y),Color(.48,.52,.45,.7),2,true)
		for i in range(int(w/40)):
			draw_line(Vector2(x+i*40+18,y+3),Vector2(x+i*40+9,y+p.h),Color(.07,.12,.14,.65),1,true)
		if p.kind == "letter":
			draw_rect(Rect2(x+9,y+27,w-18,700-y-27),Color(.13,.19,.22,.8))
		elif p.kind == "log":
			draw_line(Vector2(x+8,y+13),Vector2(x+w-8,y+15),Color(.38,.37,.28,.45),2,true)

func glow(pos, color, radius, strength):
	for j in range(7,0,-1): draw_circle(pos,radius*j/7.0,Color(color,strength*(1.0-j/8.0)*.24))

func cover(c):
	var x = float(c.x)
	var w = float(c.w)
	var col = Color("202a2b")
	if c.kind == "tent":
		draw_colored_polygon(PackedVector2Array([Vector2(x-w/2,700),Vector2(x-40,582),Vector2(x+24,570),Vector2(x+w/2,700)]),Color("364446"))
		draw_line(Vector2(x-40,582),Vector2(x+24,570),Color("737d75"),2,true)
		draw_colored_polygon(PackedVector2Array([Vector2(x-20,700),Vector2(x+10,600),Vector2(x+32,700)]),col)
	elif c.kind == "tree":
		draw_line(Vector2(x-45,700),Vector2(x-30,470),col,42,true)
		draw_line(Vector2(x-30,520),Vector2(x+90,580),col,28,true)
	else:
		draw_rect(Rect2(x-w/2,653,w,47),col)
		for i in range(int(w/28)):
			draw_rect(Rect2(x-w/2+i*28+1,655,25,17),Color("354142"))
			draw_rect(Rect2(x-w/2+i*28+11,675,25,17),Color("303b3b"))
		draw_line(Vector2(x-w/2,651),Vector2(x+w/2,651),Color(.58,.6,.49,.55),2,true)
	# Universal readable shelter marker: three sloping strokes, no bright UI sign.
	draw_polyline(PackedVector2Array([Vector2(x-7,637),Vector2(x,632),Vector2(x+7,637)]),Color(.7,.75,.66,.5),1,true)

func prop(p):
	var x = float(p.x)
	var y = float(p.y)
	var ink = Color("26312f")
	match p.kind:
		"cart":
			draw_rect(Rect2(x-49,y-51,98,30),ink)
			for dx in [-31,31]:
				draw_arc(Vector2(x+dx,y-13),15,0,TAU,18,ink,4,true)
				for a in range(4): draw_line(Vector2(x+dx,y-13),Vector2(x+dx,y-13)+Vector2.from_angle(a*PI/2+.3)*14,ink,2,true)
			draw_line(Vector2(x+48,y-38),Vector2(x+96,y-59),ink,4,true)
		"sign":
			draw_line(Vector2(x,y),Vector2(x-3,y-97),ink,6,true)
			draw_rect(Rect2(x-51,y-94,112,29),ink)
			draw_string(font,Vector2(x-44,y-74),p.label,HORIZONTAL_ALIGNMENT_LEFT,-1,11,Color("9ba599"))
		"bench":
			draw_rect(Rect2(x-51,y-35,102,9),ink)
			for dx in [-39,39]: draw_line(Vector2(x+dx,y-32),Vector2(x+dx+6,y),ink,6,true)
			draw_rect(Rect2(x-51,y-68,102,19),ink)
		"washing":
			for dx in [-100,100]: draw_line(Vector2(x+dx,y),Vector2(x+dx,y-136),ink,4,true)
			draw_line(Vector2(x-100,y-128),Vector2(x+100,y-122),ink,1.2,true)
			for i in range(4):
				var px = x-72+i*42
				draw_colored_polygon(PackedVector2Array([Vector2(px,y-126),Vector2(px+27,y-125),Vector2(px+30+sin(game.clock*1.6+i)*7,y-85),Vector2(px+sin(game.clock*1.6+i)*5,y-83)]),Color(.37,.44,.42,.7))
		"well":
			draw_rect(Rect2(x-37,y-38,74,38),ink)
			for dx in [-30,30]: draw_line(Vector2(x+dx,y-38),Vector2(x+dx,y-119),ink,5,true)
			draw_line(Vector2(x-48,y-116),Vector2(x+48,y-116),ink,7,true)
			draw_line(Vector2(x,y-116),Vector2(x,y-45),ink,1,true)
		"stump":
			draw_colored_polygon(PackedVector2Array([Vector2(x-42,y),Vector2(x-27,y-53),Vector2(x+16,y-56),Vector2(x+31,y)]),ink)
		"barricade":
			for i in range(5):
				draw_line(Vector2(x+i*20,y),Vector2(x-24+i*24,y-97),ink,8,true)
			draw_line(Vector2(x-25,y-32),Vector2(x+115,y-45),ink,6,true)

func interact_prop(p):
	var pos = Vector2(p.x,p.y)
	var used = game.flags.get(p.get("id",""),false)
	match p.kind:
		"cache":
			draw_rect(Rect2(pos+Vector2(-16,-23),Vector2(32,23)),Color("353e36") if not used else Color("29312e"))
			draw_line(pos+Vector2(-16,-23),pos+Vector2(16,-23),Color("8f9277"),2,true)
			draw_line(pos+Vector2(0,-22),pos,Color("777a63"),2,true)
			if not used: glow(pos+Vector2(0,-25),Color(.85,.75,.48),24,.18)
		"fire":
			for dx in [-10,0,10]: draw_line(pos+Vector2(dx-9,-2),pos+Vector2(dx+10,-7),Color("30342b"),4,true)
			glow(pos+Vector2(0,-19),Color(1,.59,.23),110,.3)
			for i in range(6):
				var offset = sin(game.clock*6+i*1.6)*5
				draw_colored_polygon(PackedVector2Array([pos+Vector2(-10+i*3,-5),pos+Vector2(-8+i*3+offset,-23-i%3*8),pos+Vector2(-3+i*3,-5)]),Color(.83,.44+i*.04,.18,.85))
		"wheel", "latch":
			draw_line(pos,pos+Vector2(0,-69),Color("3d4843"),7,true)
			draw_arc(pos+Vector2(0,-59),16,0,TAU,24,Color("a3a589") if not used else Color("626e61"),3,true)
			for i in range(4): draw_line(pos+Vector2(0,-59),pos+Vector2.from_angle(i*PI/2+game.clock*.12 if not used else i*PI/2)*14+Vector2(0,-59),Color("808b77"),2,true)
		"repair":
			draw_rect(Rect2(pos+Vector2(-18,-36),Vector2(36,36)),Color("394840"))
			draw_line(pos+Vector2(-14,-29),pos+Vector2(14,-8),Color("8b9278"),3,true)
		"end":
			draw_line(pos+Vector2(-70,0),pos+Vector2(-70,-150),Color("33464a"),4,true)
			draw_line(pos+Vector2(70,0),pos+Vector2(70,-150),Color("33464a"),4,true)
			draw_line(pos+Vector2(-70,-150),pos+Vector2(70,-150),Color("33464a"),4,true)
			glow(pos+Vector2(0,-110),Color(.82,.87,.8),190,.18)

func gate(g):
	var open = game.gate_open(g)
	var x = float(g.x)
	var bottom = float(g.y) - (g.h-15 if open else 0)
	for i in range(7): draw_line(Vector2(x-12+i*4,bottom),Vector2(x-12+i*4,bottom-g.h),Color("273631"),2,true)
	for dx in [-21,21]: draw_line(Vector2(x+dx,g.y),Vector2(x+dx,g.y-g.h-23),Color("3c4b41"),6,true)
	draw_line(Vector2(x-22,g.y-g.h-23),Vector2(x+22,g.y-g.h-23),Color("8b957d"),3,true)
	if g.has("plate"):
		var px = float(g.plate)
		draw_rect(Rect2(px-40,696,80,4),Color("8e9b86") if open else Color("596c62"))
		for i in range(12): draw_line(Vector2(px+40+i*22,699),Vector2(px+51+i*22,699),Color(.55,.63,.53,.24),1,true)
