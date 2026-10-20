extends Node2D

var game
var textures = {}
var bounds = {}
var rng = RandomNumberGenerator.new()
var grasses = []
var rocks = []
var font = preload("res://assets/fonts/display.ttf")
var prop_atlas=preload("res://assets/props/painted_survival_atlas_v020.png")
var prop_regions={"wall":Rect2(0,165,488,222),"log":Rect2(488,185,450,202),"crate":Rect2(938,185,316,202),"tent":Rect2(0,435,505,322),"cart":Rect2(505,488,415,269),"rubble":Rect2(920,482,334,275),"door":Rect2(0,767,475,414),"stove":Rect2(475,798,426,383),"winch":Rect2(901,768,353,413)}

func _ready():
	texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	for key in ["Sky_Painted", "Distant_Hills", "Village_Warm", "Village_Empty", "Woods", "Camp", "School", "Battlefield", "Foreground_Tree", "Ground_Painted", "Rail_Yard"]:
		var tex = load("res://assets/environments/" + key + ("_v030.png" if key=="Rail_Yard" else "_v001.png"))
		textures[key] = tex
		bounds[key] = tex.get_image().get_used_rect()
	# Ignore faint matte pixels around the original paint layers. These source
	# rectangles retain every visible painted edge and align feet to the route.
	var painted_bounds={"Battlefield":Rect2(0,133,1672,690),"Camp":Rect2(1,391,1670,349),"Distant_Hills":Rect2(0,505,1672,436),"Foreground_Tree":Rect2(35,6,1470,993),"School":Rect2(10,174,1648,575),"Village_Empty":Rect2(0,180,1671,600),"Village_Warm":Rect2(1,182,1669,599),"Woods":Rect2(0,59,1672,724)}
	for key in painted_bounds: bounds[key]=painted_bounds[key]
	# New focal art is optional while source work is in progress. Existing
	# editions remain editable without a missing preload dependency.
	var canal_path="res://assets/environments/Canal_v040.png"
	if ResourceLoader.exists(canal_path):
		var canal=load(canal_path)
		textures["Canal"]=canal
		bounds["Canal"]=canal.get_image().get_used_rect()
	rng.seed = 271019
	# All small dressing is sampled in world coordinates around the camera.
	# Long chapters keep the same density without allocating a chapter of plants.

func art(key, x, bottom, width, tint = Color.WHITE):
	var r = bounds[key]
	var h = width * float(r.size.y)/float(r.size.x)
	if key in ["Rail_Yard","Canal"]: tint=material_tint(tint,.65)
	draw_texture_rect_region(textures[key],Rect2(x,bottom-h,width,h),r,tint)

func material_tint(tint,amount=.75):
	# Source paint already contains light, wear and warm material color. Keep
	# it visible instead of multiplying every foreground object into green ink.
	var result=tint.lerp(Color(.93,.91,.84,tint.a),amount)
	result.a=tint.a
	return result

func scenery(key, factor, width, bottom, tint):
	var left = game.camera.position.x - 800
	var soft=key in ["Battlefield","Distant_Hills","Woods"]
	var advance=width*.82 if soft else width
	var offset = fposmod(-left*factor,advance)
	for i in range(-1,2):
		var x=left+offset+i*advance
		if soft: soft_horizon(key,x,bottom,width,tint)
		else: art(key,x,bottom,width,tint)

func soft_horizon(key,x,bottom,width,tint):
	# Adjacent atmosphere paintings overlap through a quiet edge fade instead
	# of exposing the rectangular source boundary in a long scrolling shot.
	var region=bounds[key]; var h=width*region.size.y/region.size.x
	for column in range(32):
		var u=(column+.5)/32.0
		var fade=clampf(minf(u/.18,(1-u)/.18),0,1)
		var source=Rect2(region.position+Vector2(region.size.x*column/32.0,0),Vector2(region.size.x/32.0,region.size.y))
		draw_texture_rect_region(textures[key],Rect2(x+width*column/32.0,bottom-h,width/32.0+.15,h),source,Color(tint, tint.a*fade))

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
	for strip in range(24): draw_rect(Rect2(left,430+strip*16,1600,17),Color(haze,.005+strip*.0008))
	match game.chapter:
		0:
			scenery("Village_Warm",.48,1750,692,Color(.82,.83,.71,.88))
			art("Woods",4100,703,1600,Color(.61,.68,.58,.70))
		1:
			scenery("Woods",.38,1800,715,Color(.60,.68,.63,.72))
			scenery("Woods",.65,2100,720,Color(.55,.62,.55,.66))
		2:
			scenery("Battlefield",.24,2150,685,Color(.57,.65,.68,.68))
			scenery("Camp",.61,1700,703,Color(.76,.78,.76,.73))
		3:
			scenery("Battlefield",.26,2200,700,Color(.64,.71,.74,.73))
			art("School",980,700,1760,Color(.73,.76,.77,.9))
			art("Village_Empty",3400,705,1900,Color(.70,.75,.74,.78))
		4:
			scenery("Battlefield",.22,2500,700,Color(.67,.74,.75,.68))
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
	draw_rect(Rect2(left,700,1600,600),Color("23363b") if game.chapter>1 else Color("2e3930"))
	for i in range(10): draw_rect(Rect2(left,720+i*28,1600,29),Color(.04,.08,.09,.035+i*.035))
	draw_zone_dressing(left)
	for mill in game.get("mill_encounters") if game.get("mill_encounters")!=null else []:
		if is_instance_valid(mill): mill.draw_background(self)
	for g in l.ground: terrain(g,true)
	for p in l.platforms: terrain(p,false)
	for bridge in l.get("bridges",[]): draw_bridge(bridge)
	for water in l.get("water_zones",[]): draw_water(water)
	draw_route_details(left)
	draw_actor_contacts()
	for c in l.covers: cover(c)
	for p in l.props: prop(p)
	for p in l.interact: interact_prop(p)
	for g in l.gates: gate(g)
	for h in l.get("hazard_lanes",[]): draw_hazard(h)
	for body in game.pushables:
		contact_shadow(self,Vector2(body.position.x,body.position.y+27),37,.28)
		paint_asset(self,"crate",Vector2(body.position.x,body.position.y+26),83,64,Color(.58,.65,.61))
	for m in l.memories:
		if not game.memories.has(m.id):
			var pos = Vector2(m.x,m.y-12+sin(t*2+m.x)*4)
			glow(pos,Color(.67,.79,.84),18,.1)
			draw_colored_polygon(PackedVector2Array([pos+Vector2(-5,-7),pos+Vector2(6,-5),pos+Vector2(4,6),pos+Vector2(-6,5)]),Color("c9d3c8"))
	for cp in l.checkpoints:
		var cy=surface(float(cp)-22)
		draw_line(Vector2(cp-22,cy),Vector2(cp-22,cy-45),Color(.18,.25,.24),3,true)
		glow(Vector2(cp-22,cy-46),Color(.88,.69,.36),11,.15)
		draw_circle(Vector2(cp-22,cy-46),2,Color("d9b975"))
	draw_surface_dressing(left)
	# Original painted foreground oaks move on their own parallax plane.
	if game.chapter <= 1:
		for i in range(2):
			var x=left+fposmod(i*1800-left*1.13,3600)-1050
			art("Foreground_Tree",x,808,730,Color(.46,.50,.40,.23))
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
	for impact in game.impacts:
		var age=impact.age; var pos=impact.p
		for i in range(11):
			var offset=Vector2((i-5)*15*(1+age*.55),-age*(18+i%3*8)-i%2*18)
			draw_circle(pos+offset,10+age*13,Color(.29,.35,.35,maxf(0,.2-age*.05)))
		if age<.7: draw_arc(pos,28+age*230,PI,TAU,34,Color(.64,.64,.5,(.7-age)*.28),4,true)

func terrain(p, earth):
	var x = float(p.x)
	var y = float(p.y)
	var w = float(p.w)
	var left=float(game.camera.position.x)-900
	if x+w<left or x>left+1800: return
	var ink = Color("182120") if game.chapter < 2 else Color("182126")
	if earth:
		# The painted upper contour is the same piecewise profile as collision.
		# Cut faces below it can fracture freely without changing the foothold.
		var top=PackedVector2Array()
		var start=maxf(x,left-60)
		var finish=minf(x+w,left+1860)
		var samples=[start,finish]
		# The collision surface is piecewise linear. Its actual knots are enough;
		# hundreds of almost-collinear points caused rare triangulation failures
		# when a camera clip landed very close to a profile knot at large X.
		for knot in p.get("profile",[]):
			var xx=x+float(knot[0])
			if xx>start and xx<finish: samples.append(xx)
		samples.sort()
		for xx in samples:
			if top.is_empty() or absf(top[-1].x-xx)>1.0: top.append(Vector2(xx,segment_y(p,xx)))
		var polygon=top.duplicate()
		var right_y=segment_y(p,finish)
		var left_y=segment_y(p,start)
		var right_exposed=finish>=x+w-1 and exposed_bank(x+w,1)
		var left_exposed=start<=x+1 and exposed_bank(x,-1)
		for depth in range(1,17):
			var notch=sin(depth*8.37+x)*11+sin(depth*3.17)*7
			polygon.append(Vector2(finish+notch*(1.0 if right_exposed else 0.0),right_y+depth*34))
		polygon.append(Vector2(start,left_y+570))
		for depth in range(16,0,-1):
			var notch=sin(depth*4.57+x)*12+cos(depth*2.4)*8
			polygon.append(Vector2(start+notch*(1.0 if left_exposed else 0.0),left_y+depth*34))
		draw_colored_polygon(polygon,ink)
		var uv=PackedVector2Array()
		for pt in polygon: uv.append(Vector2(pt.x/760.0,pt.y/760.0))
		texture_repeat=CanvasItem.TEXTURE_REPEAT_ENABLED
		var tint=[Color(.84,.81,.72),Color(.77,.80,.73),Color(.80,.79,.73),Color(.76,.81,.81),Color(.82,.83,.77)][game.chapter]
		var theme=zone_at((start+finish)*.5)
		match theme:
			"rain_gully": tint=Color(.72,.79,.77)
			"rail_yard": tint=Color(.84,.80,.72)
			"school_courtyard": tint=Color(.79,.81,.79)
			"ash_garden": tint=Color(.83,.84,.79)
			"canal": tint=Color(.75,.82,.75)
			"drainage_tunnel": tint=Color(.70,.77,.74)
			"terraced_garden": tint=Color(.87,.84,.70)
			"shattered_arcade": tint=Color(.82,.82,.76)
			"signal_yard": tint=Color(.81,.82,.74)
		draw_polygon(polygon,PackedColorArray([tint]),uv,textures.Ground_Painted)
		# Broad translucent contours retain the source brushwork and communicate
		# packed earth, sediment, damp stone and deep occlusion in the cut banks.
		for layer in range(7):
			var band=PackedVector2Array()
			for pt in top: band.append(pt+Vector2(0,18+layer*36+sin(pt.x*.018+layer*3)*5))
			for i in range(top.size()-1,-1,-1):
				var pt=top[i]
				band.append(pt+Vector2(0,60+layer*40+sin(pt.x*.014+layer)*7))
			draw_colored_polygon(band,Color(.12,.14,.12,.045+layer*.026))
		var turf=PackedVector2Array()
		for pt in top: turf.append(pt+Vector2(0,2))
		for i in range(top.size()-1,-1,-1):
			var pt=top[i]
			# Keep a positive two-pixel minimum thickness at every vertex.
			turf.append(pt+Vector2(0,4+noise_at(pt.x)*2))
		draw_colored_polygon(turf,Color(.39,.38,.27,.19) if game.chapter<2 else Color(.43,.46,.40,.17))
		draw_polyline(top,Color(.72,.70,.55,.22),1.0,true)
		draw_material_traces(p,start,finish)
		# Exposed banks retain the source's painted stones and organic cut.
		# Long synthetic root fans previously overwhelmed the bridge material.
		for i in range(int(start/43),int(finish/43)+1):
			var xx=i*43.0+noise_at(i*13)*17
			var yy=segment_y(p,xx)
			draw_line(Vector2(xx,yy+17+noise_at(xx)*36),Vector2(xx+12+noise_at(xx+5)*18,yy+20+noise_at(xx)*36),Color(.42,.45,.37,.18),1.5,true)
	else:
		var base=surface(x+w*.5,700)
		var kind=str(p.get("kind","rubble"))
		var scaffold=kind=="scaffold" or w>260
		if not scaffold:
			var asset="log" if kind=="log" else ("crate" if kind=="crate" else "rubble")
			paint_asset(self,asset,Vector2(x+w/2,base+8),w+14,maxf(38,base-y+12),Color(.57,.65,.61))
		if kind=="letter": draw_rect(Rect2(x+9,y+18,w-18,maxf(0,base-y-18)),Color(.13,.19,.22,.8))
		# A continuous painted tread makes the exact landing line readable.
		# Long scaffolds stay open underneath. Painted narrow boards repeat at
		# their real scale instead of stretching an entire rubble sprite 900px.
		if base-y>38 and kind!="letter":
			var columns=maxi(1,int(ceil(w/215.0)))
			for index in range(columns+1):
				var support=lerpf(x+18,x+w-19,float(index)/columns)
				var foot=maxf(y+28,surface(support,700)+3)
				paint_beam(Vector2(support,y+10),Vector2(support,foot),9,Color(.33,.41,.34,.78))
				if scaffold:
					var brace_end=minf(x+w-12,support+63)
					if brace_end>support+15: paint_beam(Vector2(support,y+57),Vector2(brace_end,y+12),7,Color(.34,.43,.34,.62))
		var board_count=maxi(1,int(ceil(w/117.0)))
		for index in range(board_count):
			var a=x+float(index)*w/board_count
			var b=x+float(index+1)*w/board_count
			paint_beam(Vector2(a,y+6),Vector2(b+.5,y+6),14,Color(.45+.02*(index%3),.51+.015*(index%3),.42))
			if scaffold:
				draw_line(Vector2(a+2,y+1),Vector2(a+2,y+10),Color(.12,.20,.16,.46),.8,true)
				draw_circle(Vector2(a+7,y+3),.65,Color(.66,.66,.48,.34))
		draw_line(Vector2(x+2,y+1),Vector2(x+w-2,y+1),Color(.49,.54,.45,.25),.8,true)
		if p.get("optional_route",false):
			# Worn treads and a knotted strip of cloth mark the higher route
			# through the environment, without filling the fork with UI arrows.
			for dx in [14,w-14]:
				draw_line(Vector2(x+dx-5,y+.5),Vector2(x+dx+5,y+.5),Color(.64,.65,.50,.34),1.1,true)
			if w>280:
				var wind=sin(game.clock*1.8+x*.02)*2
				draw_line(Vector2(x+22,y+9),Vector2(x+26+wind,y+27),Color(.43,.51,.46,.57),2.4,true)

func surface(x, fallback=700.0):
	return float(game.surface_y_at(x,fallback))

func exposed_bank(edge_x,direction):
	var beyond=edge_x+direction*2.0
	for other in game.level.ground:
		if beyond>=float(other.x) and beyond<=float(other.x)+float(other.w): return false
	return true

func segment_y(p, world_x):
	var profile=p.get("profile",[])
	if profile.size()<2: return float(p.y)
	var local=clampf(world_x-float(p.x),0,float(p.w))
	for i in range(1,profile.size()):
		if local<=float(profile[i][0]):
			var span=maxf(.001,float(profile[i][0])-float(profile[i-1][0]))
			return float(p.y)+lerpf(float(profile[i-1][1]),float(profile[i][1]),clampf((local-float(profile[i-1][0]))/span,0,1))
	return float(p.y)+float(profile[-1][1])

func noise_at(x):
	return fposmod(sin(x*12.9898+78.233)*43758.5453,1.0)

func zone_at(x):
	for zone in game.level.get("zones",[]):
		if x>=float(zone.x) and x<=float(zone.x)+float(zone.w): return str(zone.theme)
	return ["orchard","ridge","rail_yard","school_courtyard","ash_garden"][game.chapter]

func contact_shadow(canvas,at,width,strength=.24):
	# Small layered ellipses keep objects planted while retaining painted edges.
	canvas.draw_set_transform(at,0,Vector2(1,.18))
	for ring in range(4,0,-1): canvas.draw_circle(Vector2.ZERO,width*(.58+ring*.12),Color(.025,.045,.041,strength*.19))
	canvas.draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func draw_actor_contacts():
	for child in [game.player,game.boy]:
		if child==null: continue
		var floor_y=surface(child.position.x,child.position.y+1)
		var lift=maxf(0,floor_y-child.position.y)
		if lift<115 and game.ground_at(child.position.x):
			contact_shadow(self,Vector2(child.position.x,floor_y+2),18+lift*.045,.32*(1-lift/115))

func draw_material_traces(p,start,finish):
	# Sparse cropped paint, damp deposits and moss interrupt identical ground
	# texture without introducing another long, fragile polygon contour.
	for index in range(int(ceil((start+65)/229)),int((finish-65)/229)+1):
		var x=index*229.0
		var theme=zone_at(x)
		var y=segment_y(p,x)
		if theme in ["canal","drainage_tunnel","shattered_arcade","signal_yard"]:
			var bottom=maxf(segment_y(p,x-58),segment_y(p,x+58))+66
			paint_asset(self,"wall",Vector2(x,bottom),124,38,Color(.35,.40,.34,.36 if theme=="canal" else .25))
		if theme in ["canal","drainage_tunnel","rain_gully"]:
			for stain in range(3):
				var dx=(stain-1)*29+noise_at(index+stain)*13
				draw_set_transform(Vector2(x+dx,y+24+stain*9),0,Vector2(.36,1))
				draw_circle(Vector2.ZERO,11+noise_at(index*3+stain)*9,Color(.08,.18,.15,.10))
				draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
		elif theme=="terraced_garden" or theme=="orchard":
			for moss in range(2):
				var at=Vector2(x+moss*41,y+12+moss*7)
				draw_set_transform(at,0,Vector2(1,.24))
				draw_circle(Vector2.ZERO,19+noise_at(index+moss)*11,Color(.26,.31,.13,.13))
				draw_set_transform(Vector2.ZERO,0,Vector2.ONE)

func draw_route_details(left):
	for fork in game.level.get("branch_routes",[]):
		var entry=float(fork.get("entry_x",0))
		var exit_x=float(fork.get("exit_x",entry+900))
		if exit_x<left-150 or entry>left+1750: continue
		# A weathered handrail and pale wear marks give the upper choice an
		# authored silhouette. They never imply an additional collision surface.
		var high=float(fork.get("upper_y",540))
		var rise_x=entry+40
		var low=surface(rise_x,700)
		paint_beam(Vector2(rise_x,low+3),Vector2(rise_x-3,low-54),6,Color(.38,.44,.33,.72))
		var knot=Vector2(rise_x-3,low-47)
		draw_line(knot,knot+Vector2(17,sin(game.clock*1.4)*2),Color(.56,.58,.43,.50),2,true)
		# Sparse shafts underneath the raised walk differentiate sheltered
		# water below from the dry high route without a colored overlay.
		for i in range(3):
			var x=entry+240+i*minf(245,(exit_x-entry)/4)
			if x<left-80 or x>left+1680: continue
			var floor_y=surface(x,780)
			draw_line(Vector2(x,high+25),Vector2(x+29,floor_y-8),Color(.63,.72,.65,.025),16,true)

func draw_arch(center,radius,tint):
	# The arch opening is an occluded rear plane. Texture-bearing masonry
	# voussoirs give it a rounded painted rim rather than a flat gray ring.
	tint=material_tint(tint,.68)
	draw_circle(center,radius*.86,Color(.08,.105,.09,.82))
	for stone in range(13):
		var angle=PI+stone*PI/12.0
		var at=center+Vector2(cos(angle),sin(angle))*radius
		draw_set_transform(at,angle+PI*.5,Vector2.ONE)
		draw_texture_rect_region(prop_atlas,Rect2(-radius*.14,-15,radius*.28+2,30),Rect2(73,247,294,76),tint)
		draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	for dx in [-radius,radius]:
		paint_asset(self,"wall",center+Vector2(dx,21),38,46,tint)

func draw_surface_dressing(left):
	var length=float(game.level.width)
	for i in range(maxi(0,int((left-40)/23)),int(minf(length,left+1650)/23)+1):
		var x=i*23.0+noise_at(i+7)*16
		if not game.ground_at(x): continue
		var y=surface(x)
		var theme=zone_at(x)
		var height=3+noise_at(i*19)*9
		if theme in ["rail_yard","school_courtyard","shattered_arcade","signal_yard","drainage_tunnel"]: height*=.45
		if theme=="terraced_garden": height*=1.15
		var wind=sin(game.clock*1.4+x*.028)*2.4
		var green=Color(.13,.19,.15,.54) if game.chapter<2 else Color(.17,.22,.20,.48)
		for blade in range(3):
			var dx=blade*3.4
			var tip=Vector2(x+dx+wind+noise_at(i+blade)*8,y-height*(.6+blade*.19))
			draw_polyline(PackedVector2Array([Vector2(x+dx,y+2),Vector2(x+dx+wind*.35,y-height*.45),tip]),green,.8,true)
		if i%13==0:
			paint_asset(self,"rubble",Vector2(x,y+4),20+noise_at(i*8)*12,7+noise_at(i)*6,Color(.33,.39,.33,.62))

func draw_zone_dressing(left):
	# Large silhouettes are grounded in each zone, while their low contrast
	# places them behind the playable plane and leaves action silhouettes clear.
	var length=float(game.level.width)
	for zone in game.level.get("zones",[]):
		var theme=str(zone.theme)
		var zone_x=float(zone.x)
		var width=float(zone.w)
		if zone_x+width<left-320 or zone_x>left+1850: continue
		if theme=="rail_yard":
			var station_x=zone_x+200
			var station_w=minf(2540,width-180)
			art("Rail_Yard",station_x,surface(station_x+station_w*.5)+10,station_w,Color(.62,.69,.65,.91))
		elif theme=="canal" and textures.has("Canal") and not zone.get("interactive_mill",false):
			var painting_w=clampf(width*.96,1700,2580)
			art("Canal",zone_x+140,surface(zone_x+width*.5,780)+19,painting_w,Color(.52,.63,.59,.95))
		elif theme=="drainage_tunnel":
			var mouth_x=zone_x+width*.62
			var floor_y=surface(mouth_x)
			paint_asset(self,"wall",Vector2(mouth_x,floor_y+26),324,111,Color(.40,.46,.38,.84))
			draw_arch(Vector2(mouth_x,floor_y+2),96,Color(.41,.49,.41,.91))
			glow(Vector2(mouth_x-26,floor_y-37),Color(.59,.68,.52),58,.06)
		elif theme=="terraced_garden":
			var center=zone_x+width*.47
			var ground=surface(center)
			paint_asset(self,"wall",Vector2(center-71,ground+7),288,72,Color(.57,.60,.43,.77))
			paint_asset(self,"wall",Vector2(center+163,ground-30),239,62,Color(.45,.51,.35,.51))
			for stem in range(14):
				var x=center-175+stem*29
				var bottom=ground-42 if stem<8 else ground-74
				var tip=Vector2(x+sin(game.clock*.9+stem)*1.2,bottom-10-noise_at(stem+center)*15)
				draw_line(Vector2(x,bottom+2),tip,Color(.18,.28,.14,.57),1,true)
				if stem%3==0: draw_circle(tip,1.7,Color(.60,.58,.31,.43))
		elif theme=="shattered_arcade":
			var center=zone_x+width*.56
			var ground=surface(center)
			draw_arch(Vector2(center-142,ground+12),105,Color(.43,.47,.41,.62))
			draw_arch(Vector2(center+141,ground+16),97,Color(.39,.44,.39,.47))
			paint_asset(self,"rubble",Vector2(center+43,ground+16),182,73,Color(.46,.51,.44,.74))
		elif theme=="signal_yard":
			var center=zone_x+width*.58
			var ground=surface(center)
			paint_beam(Vector2(center,ground+3),Vector2(center-5,ground-222),12,Color(.37,.44,.35,.72))
			paint_beam(Vector2(center-68,ground-193),Vector2(center+55,ground-199),12,Color(.42,.47,.38,.69))
			for dx in [-42,34]:
				var at=Vector2(center+dx,ground-187)
				draw_line(at,at+Vector2(0,23),Color(.22,.29,.24,.76),1.1,true)
				glow(at+Vector2(0,26),Color(.87,.63,.30),33,.12)
				draw_circle(at+Vector2(0,26),3.3,Color(.65,.56,.33,.70))
	# The original paintings carry the broad forms. Sparse painted objects add
	# local depth without layering repeated geometric placeholders over them.
	for i in range(maxi(0,int((left-300)/790)),int(minf(length,left+1900)/790)+1):
		var x=i*790.0+noise_at(i*3)*170
		if not game.ground_at(x): continue
		var y=surface(x)+5
		var theme=zone_at(x)
		var ink=Color(.12,.18,.17,.23)
		match theme:
			"orchard":
				if i%3==0: paint_asset(self,"cart",Vector2(x,y+7),135,79,Color(.48,.54,.43,.55))
			"ridge", "rain_gully":
				paint_asset(self,"rubble",Vector2(x,y+10),118+noise_at(i)*81,44+noise_at(i+1)*34,Color(.40,.47,.42,.65))
				if i%3==0: paint_asset(self,"log",Vector2(x+86,y+6),99,33,Color(.34,.43,.37,.51))
			"rail_yard":
				if i%3==0:
					draw_line(Vector2(x,y),Vector2(x-5,y-268),ink,5,true)
					draw_line(Vector2(x-37,y-249),Vector2(x+35,y-254),ink,3,true)
					var wire=PackedVector2Array()
					for k in range(21): wire.append(Vector2(x+k*50,y-251+sin(k/20.0*PI)*29))
					draw_polyline(wire,ink,.7,true)
				elif i%2==0: paint_asset(self,"cart",Vector2(x,y+10),171,94,Color(.35,.43,.39,.54))
			"school_courtyard":
				if i%2==0: paint_asset(self,"wall",Vector2(x,y+7),112,69,Color(.41,.48,.44,.57))
				else:
					draw_line(Vector2(x-61,y),Vector2(x-65,y-147),ink,2.2,true)
					draw_line(Vector2(x+64,y),Vector2(x+64,y-147),ink,2.2,true)
					draw_line(Vector2(x-65,y-147),Vector2(x+64,y-147),ink,2.8,true)
					var swing=sin(game.clock*.8+i)*5
					draw_line(Vector2(x-26,y-147),Vector2(x-26+swing,y-38),ink,.7,true)
					draw_line(Vector2(x+15,y-147),Vector2(x+15+swing,y-38),ink,.7,true)
					draw_line(Vector2(x-32+swing,y-36),Vector2(x+21+swing,y-36),ink,2.2,true)
			"ash_garden":
				paint_asset(self,"log",Vector2(x,y+5),119,48,Color(.42,.48,.45,.57))
				if i%3==0:
					draw_line(Vector2(x+16,y),Vector2(x+20,y-82),ink,2,true)
					var flutter=sin(game.clock*1.7+i)*4
					draw_colored_polygon(PackedVector2Array([Vector2(x+20,y-75),Vector2(x+34,y-73),Vector2(x+37+flutter,y-52),Vector2(x+23+flutter,y-55)]),Color(.29,.34,.31,.24))
			"canal", "drainage_tunnel":
				paint_asset(self,"wall",Vector2(x,y+17),127,48,Color(.34,.44,.36,.60))
				if i%2==0:
					for reed in range(5):
						var sway=sin(game.clock*1.2+reed)*2
						draw_line(Vector2(x+reed*3,y+4),Vector2(x+reed*3+sway,y-15-reed%3*7),Color(.17,.27,.18,.42),.8,true)
			"terraced_garden":
				if i%2==0: paint_asset(self,"crate",Vector2(x,y+3),42,31,Color(.47,.53,.36,.71))
			"shattered_arcade":
				paint_asset(self,"rubble",Vector2(x,y+5),133,49,Color(.43,.48,.43,.66))
			"signal_yard":
				if i%2==0: paint_asset(self,"cart",Vector2(x,y+7),139,81,Color(.39,.45,.38,.58))

func draw_hazard(h):
	var x=float(h.x)
	var w=float(h.w)
	var left=float(game.camera.position.x)-850
	if x+w<left or x>left+1700: return
	var active=bool(game.hazard_active(h))
	var warning=bool(game.hazard_warning(h))
	var phase=float(game.playtime)+float(h.get("offset",0))
	var kind=str(h.get("kind","debris"))
	if kind=="listener":
		# A distant lit opening, listening figure and a faint damp reflection
		# communicate attention without painting a rectangular danger zone.
		var mid=x+w*.68
		var ground=surface(mid,780)
		paint_asset(self,"door",Vector2(mid,ground+5),97,154,Color(.31,.40,.34,.60))
		var window=Vector2(mid+1,ground-101)
		var strength=.21 if active else (.12 if warning else .035)
		glow(window,Color(.91,.65,.31),61,strength)
		draw_rect(Rect2(window+Vector2(-10,-15),Vector2(20,25)),Color(.83,.60,.29,.22 if active else .055))
		draw_line(window+Vector2(-11,-3),window+Vector2(11,-3),Color(.10,.17,.14,.78),1.5,true)
		draw_line(window+Vector2(0,-15),window+Vector2(0,10),Color(.10,.17,.14,.78),1.4,true)
		if active:
			draw_circle(window+Vector2(-3,3),4.3,Color(.04,.09,.08,.79))
			draw_line(window+Vector2(-4,8),window+Vector2(-4,17),Color(.04,.09,.08,.79),9,true)
		for i in range(4):
			var xx=mid-48+i*24
			var yy=surface(xx,780)-1
			draw_line(Vector2(xx,yy),Vector2(xx+13,yy),Color(.69,.58,.34,strength*.34),.8,true)
		return
	if kind=="wind":
		for i in range(22):
			var xx=x+fposmod(i*81.7+phase*(420 if active else 65),w)
			var yy=surface(xx)-18-i%7*29
			draw_line(Vector2(xx,yy),Vector2(minf(x+w,xx+34+(22 if active else 0)),yy-3),Color(.69,.76,.71,.21 if active else .055),1.2,true)
	elif kind=="debris":
		# A broken lintel and dangling sheet identify danger before it cycles.
		var mid=x+w*.5
		var ground=surface(mid)
		paint_beam(Vector2(x-23,surface(x-23)+3),Vector2(x-24,ground-250),13,Color(.32,.39,.34,.88))
		paint_beam(Vector2(x+w+17,surface(x+w+17)+3),Vector2(x+w+18,ground-256),13,Color(.32,.39,.34,.88))
		paint_beam(Vector2(x-24,ground-250),Vector2(x+w*.4,ground-263),17,Color(.31,.38,.33,.58))
		paint_beam(Vector2(x+w*.53,ground-241),Vector2(x+w+18,ground-256),15,Color(.31,.38,.33,.58))
		draw_line(Vector2(mid+31,ground-250),Vector2(mid+36+sin(phase*2)*6,ground-193),Color(.42,.49,.45,.7),2,true)
		for i in range(13 if active else 4):
			var xx=x+noise_at(i*19+int(phase)*3)*w
			var yy=surface(xx)-fposmod(i*43-phase*(350 if active else 42),280)
			draw_colored_polygon(PackedVector2Array([Vector2(xx,yy-4),Vector2(xx+5,yy-1),Vector2(xx+3,yy+5),Vector2(xx-3,yy+2)]),Color(.48,.51,.44,.62 if active else .17))
	else:
		var mid=x+w*.5+sin(phase*.76)*w*.4
		var sy=surface(mid)
		if active: draw_colored_polygon(PackedVector2Array([Vector2(mid-165,-120),Vector2(mid-64,sy),Vector2(mid+74,sy)]),Color(.78,.83,.67,.12))
	if active or warning:
		for i in range(int(w/30)):
			var xx=x+i*30
			var yy=surface(xx)
			draw_line(Vector2(xx,yy-2),Vector2(xx+14,yy-2),Color(.73,.63,.42,(.24 if active else .11)+sin(phase*7)*.06),2,true)

func paint_asset(canvas,key,bottom,width,height=0.0,tint=Color.WHITE):
	var region=prop_regions[key]
	if height<=0: height=width*region.size.y/region.size.x
	tint=material_tint(tint,.22 if key=="tent" else .75)
	canvas.draw_texture_rect_region(prop_atlas,Rect2(bottom-Vector2(width/2,height),Vector2(width,height)),region,tint)

func draw_bridge(bridge):
	if not game.flags.get(bridge.key,false):
		paint_asset(self,"log",Vector2(bridge.x-18,700),95,112,Color(.4,.48,.45))
		return
	for i in range(int(bridge.w/19)+1):
		var x=float(bridge.x)+i*19
		paint_beam(Vector2(x,bridge.y+7),Vector2(minf(x+18,float(bridge.x)+float(bridge.w)),bridge.y+7),14,Color(.69,.72,.57))
		draw_line(Vector2(x+2,bridge.y+1),Vector2(x+16,bridge.y+1),Color(.72,.70,.55,.29),.8,true)
	for y in [bridge.y-7,bridge.y+23]:draw_line(Vector2(bridge.x-24,y),Vector2(bridge.x+bridge.w+24,y+3),Color("323f3b"),2.4,true)

func draw_water(water):
	var y=float(water.top)+float(game.water_offsets.get(water.key,0))
	var left=float(game.camera.position.x)-850
	if float(water.x)+float(water.w)<left or float(water.x)>left+1700: return
	var floor_y=surface(float(water.x)+float(water.w)*.5,float(water.top)+30)
	if y>=floor_y+4: return
	var depth_size=maxf(4,floor_y-y+4)/8.0
	for depth in range(8):
		var alpha=.29+depth*.025
		draw_rect(Rect2(water.x,y+depth*depth_size,water.w,depth_size+.15),Color(.12,.25,.28,alpha))
	# Soft broken reflections make water read as a horizontal moving surface.
	for i in range(21):
		var xx=water.x+fposmod(i*73.7+game.clock*(9+i%3*2),water.w)
		var yy=y+2+i%6*minf(3,depth_size)
		var length=12+noise_at(i+water.x)*29
		draw_line(Vector2(xx,yy),Vector2(minf(xx+length,water.x+water.w),yy+sin(game.clock+i)*.5),Color(.40,.57,.55,.13-i%6*.013),.8,true)
	for bank in [float(water.x),float(water.x)+float(water.w)]:
		paint_asset(self,"rubble",Vector2(bank,y+31),65,29,Color(.31,.43,.36,.51))
		draw_line(Vector2(bank-8,y+2),Vector2(bank+11,y+2),Color(.52,.62,.52,.23),.8,true)

func glow(pos, color, radius, strength):
	for j in range(7,0,-1): draw_circle(pos,radius*j/7.0,Color(color,strength*(1.0-j/8.0)*.24))

func cover(c):
	var x = float(c.x)
	var w = float(c.w)
	var y = float(c.get("y",surface(x)))
	var col = Color("202a2b")
	contact_shadow(self,Vector2(x,y+3),minf(w*.43,117),.29)
	if c.kind == "tent":
		paint_asset(self,"tent",Vector2(x,y+4),w+34,148,Color(.68,.75,.72))
	elif c.kind == "tree":
		paint_beam(Vector2(x-45,y+4),Vector2(x-30,y-230),42,Color(.59,.65,.50))
		paint_beam(Vector2(x-30,y-180),Vector2(x+90,y-120),28,Color(.57,.64,.48))
	else:
		paint_asset(self,"wall",Vector2(x,y+5),w+20,82,Color(.56,.65,.63))
	# Universal readable shelter marker: three sloping strokes, no bright UI sign.
	draw_polyline(PackedVector2Array([Vector2(x-7,y-63),Vector2(x,y-68),Vector2(x+7,y-63)]),Color(.7,.75,.66,.5),1,true)

func prop(p):
	var x = float(p.x)
	var y = surface(x,float(p.get("y",700)))
	var ink = Color("26312f")
	contact_shadow(self,Vector2(x,y+2),38 if p.kind in ["cart","bench","well"] else 19,.18)
	match p.kind:
		"cart":
			paint_asset(self,"cart",Vector2(x,y+4),182,116,Color(.56,.65,.59))
		"sign":
			paint_beam(Vector2(x,y+2),Vector2(x-3,y-97),6,Color(.56,.61,.45))
			paint_beam(Vector2(x-51,y-80),Vector2(x+61,y-80),29,Color(.55,.58,.42))
			draw_string(font,Vector2(x-44,y-74),p.label,HORIZONTAL_ALIGNMENT_LEFT,-1,11,Color("9ba599"))
		"bench":
			paint_beam(Vector2(x-51,y-31),Vector2(x+51,y-31),9,Color(.59,.62,.46))
			for dx in [-39,39]: paint_beam(Vector2(x+dx,y-32),Vector2(x+dx+6,y),6,Color(.53,.59,.42))
			paint_beam(Vector2(x-51,y-58),Vector2(x+51,y-58),19,Color(.57,.61,.45))
		"washing":
			# Faded narrow laundry sits in the rear plane, with ample empty air.
			for dx in [-100,100]: paint_beam(Vector2(x+dx,y+2),Vector2(x+dx-2,y-119),5,Color(.28,.36,.29,.5))
			draw_line(Vector2(x-100,y-113),Vector2(x+100,y-108),Color(.16,.24,.19,.35),.7,true)
			for i in range(3):
				var px=x-64+i*54
				var sway=sin(game.clock*1.6+i)*2
				draw_colored_polygon(PackedVector2Array([Vector2(px,y-112),Vector2(px+16,y-111),Vector2(px+18+sway,y-86),Vector2(px+sway,y-85)]),Color(.26,.32,.25,.18))
		"well":
			paint_asset(self,"wall",Vector2(x,y+4),80,42,Color(.66,.70,.58))
			for dx in [-30,30]: paint_beam(Vector2(x+dx,y-30),Vector2(x+dx,y-119),5,Color(.54,.61,.44))
			paint_beam(Vector2(x-48,y-116),Vector2(x+48,y-116),7,Color(.62,.66,.48))
			draw_line(Vector2(x,y-116),Vector2(x,y-37),Color(.57,.54,.38,.72),1,true)
		"stump":
			paint_asset(self,"log",Vector2(x,y+5),83,51,Color(.61,.64,.44))
		"barricade":
			for i in range(5):
				paint_beam(Vector2(x+i*20,y),Vector2(x-24+i*24,y-97),8,Color(.58,.64,.47))
			paint_beam(Vector2(x-25,y-32),Vector2(x+115,y-45),6,Color(.62,.66,.49))

func interact_prop(p):
	var pos = Vector2(p.x,surface(float(p.x),float(p.get("y",700))))
	var used = game.flags.get(p.get("id",p.get("key","")),false)
	contact_shadow(self,pos+Vector2(0,2),32,.24)
	match p.kind:
		"cache":
			paint_asset(self,"crate",pos+Vector2(0,4),40,29,Color(.58,.61,.45) if not used else Color(.33,.41,.34))
			# A tiny tied linen edge catches the eye against worn painted wood.
			draw_line(pos+Vector2(-5,-15),pos+Vector2(8,-13),Color(.59,.60,.45,.57 if not used else .16),1.6,true)
			if not used: glow(pos+Vector2(0,-18),Color(.85,.75,.48),20,.11)
		"fire":
			paint_asset(self,"stove",pos+Vector2(0,5),108,114,Color(.74,.76,.68))
			for dx in [-10,0,10]: draw_line(pos+Vector2(dx-9,-2),pos+Vector2(dx+10,-7),Color("30342b"),4,true)
			glow(pos+Vector2(0,-19),Color(1,.59,.23),110,.3)
			for i in range(4):
				var flame=pos+Vector2(-7+i*4+sin(game.clock*5+i)*1.3,-14-i%2*4)
				draw_set_transform(flame,0,Vector2(.50,1))
				draw_circle(Vector2.ZERO,5+sin(game.clock*8+i)*.8,Color(.79,.39+i*.035,.12,.40))
				draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
			for ember in range(3):
				var age=fposmod(game.clock*.42+ember*.33,1.0)
				var at=pos+Vector2(22+sin(age*6+ember)*6,-81-age*37)
				draw_circle(at,.55,Color(.84,.55,.24,(1-age)*.30))
		"wheel", "latch", "bridge", "pump":
			paint_asset(self,"winch",pos+Vector2(0,4),93,114,Color(.54,.65,.59))
			if p.kind=="pump" and int(p.get("scrap_cost",0))>0:
				# The chain and lowered timber leaf identify the canal sluice
				# as distinct from an ordinary well or searchable supply box.
				var lift=46 if used else 0
				paint_beam(pos+Vector2(59,8),pos+Vector2(59,-104),9,Color(.37,.48,.37,.81))
				paint_beam(pos+Vector2(112,8),pos+Vector2(112,-108),9,Color(.37,.48,.37,.81))
				for plank in range(4): paint_beam(pos+Vector2(60,-12-plank*16-lift),pos+Vector2(112,-14-plank*16-lift),12,Color(.37,.49,.38,.77))
				draw_line(pos+Vector2(4,-72),pos+Vector2(85,-95),Color(.46,.52,.41,.59),1.3,true)
		"repair":
			paint_asset(self,"door",pos+Vector2(0,5),156,192,Color(.61,.69,.65))
		"roof":
			paint_asset(self,"tent",pos+Vector2(75,4),315,182,Color(.65,.71,.67))
		"relay":
			var identity=str(p.get("id",""))
			if "carriage" in identity:
				var slide=54.0 if used else 0.0
				paint_asset(self,"door",pos+Vector2(slide,5),151,174,Color(.52,.59,.54))
				# The dark recessed pull sits where the two children reach together.
				draw_line(pos+Vector2(26+slide,-65),pos+Vector2(41+slide,-65),Color(.13,.19,.17,.75),3,true)
				draw_line(pos+Vector2(28+slide,-67),pos+Vector2(40+slide,-67),Color(.56,.59,.47,.42),1,true)
			elif "branch" in identity:
				paint_asset(self,"log",pos+Vector2(84 if used else 0,6 if used else -12),201,39 if used else 63,Color(.47,.55,.47))
			else:
				paint_beam(pos+Vector2(-56,5),pos+Vector2(-57,-111),15,Color(.39,.47,.39))
				paint_beam(pos+Vector2(59,5),pos+Vector2(61,-118),15,Color(.39,.47,.39))
				var lift=52 if used else 0
				paint_beam(pos+Vector2(-63,-62-lift),pos+Vector2(69,-66-lift),18,Color(.53,.59,.47))
				for dx in [-30,27]: draw_line(pos+Vector2(dx,-63-lift),pos+Vector2(dx+7,-63-lift),Color(.58,.60,.47,.42),1.2,true)
			if not used: glow(pos+Vector2(15,-58),Color(.70,.68,.46),15,.07)
		"clear":
			# The wheel, broken axle and cloth bundle tell the obstruction apart
			# from a searchable crate. Cleared remains stay on the verge.
			var shift=Vector2(67,8) if used else Vector2.ZERO
			var origin=pos+shift
			paint_asset(self,"cart",origin+Vector2(0,4),188,111,Color(.53,.60,.52,.75 if used else 1.0))
			for plank in range(3):
				var base=origin+Vector2(-76+plank*65,0)
				paint_beam(base,base+Vector2(46,-35),9,Color(.37,.46,.36,.85))
			if not used: glow(pos+Vector2(15,-49),Color(.75,.73,.49),22,.11)
		"brace":
			# Painted wood replaces flat geometric support shapes. A slight lean
			# and splintered cap communicate the unstable roof before repair.
			paint_beam(pos+Vector2(-79,-153),pos+Vector2(77,-164),24,Color(.42,.50,.41))
			var lean=0.0 if used else 18.0
			paint_beam(pos+Vector2(13+lean,5),pos+Vector2(4,-151),18,Color(.47,.55,.43))
			paint_beam(pos+Vector2(23+lean,-1),pos+Vector2(58,-92),10,Color(.34,.43,.33))
			for dy in [-141,-137,-132]: draw_line(pos+Vector2(-1,dy),pos+Vector2(10,dy+1),Color(.50,.48,.35,.64),1,true)
			paint_asset(self,"rubble",pos+Vector2(-73,6),89,35,Color(.42,.49,.41))
			if used: paint_beam(pos+Vector2(6,-116),pos+Vector2(-35,-151),10,Color(.43,.51,.39))
			else: glow(pos+Vector2(13,-66),Color(.70,.68,.46),15,.07)
		"end":
			paint_asset(self,"door",pos+Vector2(0,5),212,257,Color(.58,.68,.67))
			glow(pos+Vector2(0,-110),Color(.82,.87,.8),190,.18)

func gate(g):
	var open = game.gate_open(g)
	var x = float(g.x)
	var ground_y=surface(x,float(g.y))
	var bottom = ground_y - (g.h-15 if open else 0)
	paint_asset(self,"door",Vector2(x,bottom),45,float(g.h),Color(.45,.53,.45))
	for dx in [-24,24]: paint_beam(Vector2(x+dx,ground_y+3),Vector2(x+dx,ground_y-g.h-23),10,Color(.39,.47,.38))
	paint_beam(Vector2(x-31,ground_y-g.h-23),Vector2(x+31,ground_y-g.h-23),9,Color(.53,.59,.44))
	if g.has("plate"):
		var px = float(g.plate)
		var py=surface(px)
		draw_rect(Rect2(px-40,py-4,80,4),Color("8e9b86") if open else Color("596c62"))
		for i in range(12):
			var line_x=px+40+i*22
			draw_line(Vector2(line_x,surface(line_x)-1),Vector2(line_x+11,surface(line_x+11)-1),Color(.55,.63,.53,.24),1,true)

func paint_beam(a,b,thickness,tint):
	var delta=b-a
	tint=material_tint(tint,.80)
	draw_set_transform(a,delta.angle(),Vector2.ONE)
	# The opaque bark interior avoids the transparent margin of the log sprite.
	draw_texture_rect_region(prop_atlas,Rect2(0,-thickness*.5,delta.length(),thickness),Rect2(555,296,300,52),tint)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
