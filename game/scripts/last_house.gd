extends RefCounted
var g
var data
var stage="idle"
var lift=0.0
var relief_clock=0.0
var exposure={"Girl":0.0,"Boy":0.0}
var last_warning=-20.0
var unavailable=""
var beat=""
var beat_clock=0.0
var beat_duration=0.0
var bag_at=Vector2(8318,700)
var footfalls=[]
var house_texture=preload("res://assets/environments/LastHouse_v050.png")
func _init(game):
	g=game
	data=JSON.parse_string(FileAccess.get_file_as_string("res://levels/last_house.json"))
func start(resume=true):
	g.slice_active=true;g.section_preview=true;g.save_path=g.last_house_save_path
	stage="idle";exposure={"Girl":0.0,"Boy":0.0};relief_clock=0;unavailable="";last_warning=-20;beat="";beat_clock=0;bag_at=Vector2(8318,700);footfalls.clear()
	if resume and g.load_save(true):
		g.mode="playing";return
	g.flags={};g.memories={};g.cache_remaining={};g.journey_active=true;g.journey_completed=false
	g.rations=1;g.scrap=0;g.medicine=1;g.health=100;g.warmth=62;g.food=72;g.stamina=100;g.wetness=.15;g.playtime=0;g.clock=0;g.death_count=0
	g.load_chapter(2,false);g.mode="playing";g.checkpoint_x=180;g.respawn(false)
	g.announce_message("A dry window beyond the railway. There may still be a way through the house.",7);g.write_save()
func reset_after_recovery():
	stage="idle";exposure={"Girl":0.0,"Boy":0.0};g.boy.following=true;beat=""
func beam_x():return 6200+sin(g.clock*.34)*650
func shop_beam_x():return 2600+sin(g.clock*.42+.8)*430
func label_for(p):
	if p.kind=="brace" and p.id=="rail_awning":return "Spend 1 salvage: shelter the first crossing wall"
	if p.kind=="reciprocal":
		if stage=="boy_holds":return "He has the support. Walk through to him."
		if stage in ["align","girl_holds"]:return "Keep the support steady while he crosses"
	if p.kind=="share" and not g.flags.get("bag_down",false):return "Set the bag down beside the door first"
	if p.kind=="quiet" and not g.flags.get("shared_meal",false):return "Share a little warmth together first"
	return p.label
func prompt_for(p):
	if p.kind=="reciprocal" and stage=="boy_holds":return "WALK RIGHT   He has the support. Join him."
	if p.kind=="reciprocal" and stage=="returning":return "Give him room to return, then try again"
	if p.kind=="share" and not g.flags.get("bag_down",false):return label_for(p)
	if p.kind=="quiet" and not g.flags.get("shared_meal",false):return label_for(p)
	if p.kind=="brace" and g.scrap<1:return "1 SALVAGE NEEDED   Search the exposed shop shelf"
	return ("HOLD " if p.kind in ["cache","brace","reciprocal"] else "")+g.access.label("interact")+"   "+label_for(p)
func try_interact(p):
	unavailable=""
	match p.kind:
		"inspect":
			if not g.flags.get(p.id,false):
				g.flags[p.id]=true;g.memories[p.id]="Two chairs turned towards the window. A child had drawn the same house on the back of the photograph."
				g.announce_message(g.memories[p.id],8);g.play_sfx("collect",-20);g.write_save()
			return true
		"reciprocal":
			if g.flags.get("passage_complete",false):return true
			if stage=="idle":
				stage="align";g.boy.following=true
				g.announce_message("She steadies the support. He can reach the catch on the other side.",5)
			return true
		"bag":
			if absf(g.player.position.x-g.boy.position.x)>140:return refuse("Bring him inside before setting the bag down.")
			beat="bag";beat_clock=0;beat_duration=.6;bag_at=Vector2(g.player.position.x+g.player.facing*24,700)
			g.play_sfx("cloth",-10,bag_at,"BAG SET DOWN")
			g.flags["bag_down"]=true;g.player.action_time=.6;g.boy.action_time=.6;g.checkpoint_x=maxf(8100,g.player.position.x)
			g.announce_message("The bag lands softly. For the first time, there is no need to hurry.",6);g.write_save();return true
		"share":
			if not g.flags.get("bag_down",false):return refuse("Set the bag down beside the door first.")
			if absf(g.player.position.x-g.boy.position.x)>120:return refuse("Wait for him before sharing.")
			if not g.flags.get("shared_meal",false):
				beat="meal";beat_clock=0;beat_duration=1.0;g.play_sfx("bread",-10,g.player.position,"SHARING FOOD")
				if g.rations>0:g.rations-=1;g.food=minf(100,g.food+36)
				else:
					g.flags["emergency_bowl"]=true;g.food=maxf(35,g.food)
				g.flags["shared_meal"]=true;g.health=minf(100,g.health+22);g.warmth=95;g.wetness=maxf(0,g.wetness-.7);relief_clock=0
				g.player.action_time=1;g.boy.action_time=1;g.announce_message("They share what is left. Rain taps at the glass, outside.",7);g.write_save()
			return true
		"quiet":
			if not g.flags.get("shared_meal",false):return refuse("Share a little warmth together first.")
			if absf(g.player.position.x-g.boy.position.x)>130:return refuse("There is room for both of you by the window.")
			if beat=="meal":return refuse("Finish sharing, then come to the window together.")
			g.flags["last_house_complete"]=true;g.flags[p.id]=true;g.journey_completed=true;g.player.action_time=.8;g.boy.action_time=.8
			g.announce_message("For a little while, the rain can wait.",9);g.write_save();return true
	return false
func refuse(reason):unavailable=reason;g.announce_message(reason,4);return true
func alignment_axis():
	if stage!="align":return null
	return clampf((3900-g.player.position.x)/12.0,-1,1)
func companion_override():
	if stage in ["girl_holds","returning"]:
		var target=4190.0 if stage=="girl_holds" else 3830.0
		g.boy.following=false;g.boy.forced_crouch=false;g.boy.ai_axis=clampf((target-g.boy.position.x)/20.0,-1,1)
		return true
	if stage=="boy_holds":
		g.boy.following=false;g.boy.forced_crouch=false;g.boy.ai_axis=0;g.boy.action_time=.12;g.boy.facing=-1
		return true
	return false
func gate_held():return stage in ["girl_holds","returning","boy_holds"] or g.flags.get("passage_braced",false)
func is_helping():return stage in ["align","girl_holds","returning","boy_holds"]
func warm_light_at(at):
	return (.45+.55*clampf(1-absf(at.x-8710)/620,0,1))*clampf((at.x-7900)/450,0,1) if g.in_safe_zone(at.x,at.y) else 0.0
func bag_grip():
	var u=clampf(beat_clock/maxf(.01,beat_duration*.75),0,1) if beat=="bag" else 1.0
	u=u*u*(3-2*u)
	return bag_at+Vector2(0,lerpf(-48,-25,u))
func pose_for(child):
	var f=child.facing
	if (stage=="girl_holds" and child==g.player) or (stage=="boy_holds" and child==g.boy):
		var x=3930.0 if child==g.player else 4160.0
		f=1.0 if child==g.player else -1.0
		return {"mode":"support","facing":f,"hip":Vector2(f*3,-44),"shoulder":Vector2(f*10,-68),"near_hand":Vector2(x,650),"far_hand":Vector2(x-f*6,650),"tilt":f*.035}
	if beat=="bag":
		var u=clampf(beat_clock/beat_duration,0,1)
		if child==g.player:
			var down=clampf(u/.75,0,1);down=down*down*(3-2*down)
			var release=clampf((u-.75)/.25,0,1)
			var pose={"mode":"bag","facing":f,"hip":Vector2(-f,-47+down*15),"shoulder":Vector2(f*8,-75+down*23),"tilt":f*down*.10,"weight":1-release}
			if u<.77:pose.near_hand=bag_grip();pose.far_hand=bag_grip()+Vector2(-f*6,1)
			return pose
		return {"mode":"attend_bag","hip":Vector2(0,-46),"shoulder":Vector2(f*3,-73),"tilt":f*.035}
	if beat=="meal":
		var u=clampf(beat_clock/beat_duration,0,1)
		var midpoint=(g.player.position.x+g.boy.position.x)*.5
		f=1.0 if midpoint>child.position.x else -1.0
		var offer=Vector2(clampf(midpoint-child.position.x,-28,28),-50)
		var taste=clampf((u-.25)/.5,0,1);taste=taste*taste*(3-2*taste)
		return {"mode":"meal","facing":f,"hip":Vector2(-f,-42),"shoulder":Vector2(f*7,-66),"near_hand":child.position+offer.lerp(Vector2(f*9,-70),taste),"far_hand":child.position+Vector2(f*8,-48),"tilt":f*.08}
	if child.crouching and child.is_on_floor() and absf(child.velocity.x)<10 and child.position.x>5200 and child.position.x<7300:
		f=signf(beam_x()-child.position.x)
		return {"mode":"cover","facing":f,"hip":Vector2(-f*2,-31),"shoulder":Vector2(f*4,-47),"near_hand":child.position+Vector2(f*10,-27),"far_hand":child.position+Vector2(-f*8,-29),"tilt":-f*.035}
	if g.flags.get("shared_meal",false) and beat!="meal" and child.position.x>8450 and absf(child.velocity.x)<10:
		var other=g.boy if child==g.player else g.player
		f=signf(other.position.x-child.position.x) if absf(other.position.x-child.position.x)>6 else f
		return {"mode":"quiet","facing":f,"hip":Vector2(-f*2,-43),"shoulder":Vector2(f*2,-67),"near_hand":child.position+Vector2(f*10,-43),"far_hand":child.position+Vector2(-f*3,-42),"tilt":f*.07}
	return {}
func tick(dt):
	for step in footfalls:step.age+=dt
	footfalls=footfalls.filter(func(step):return step.age<.65)
	if beat!="":
		beat_clock+=dt
		if beat_clock>=beat_duration:beat=""
	if stage=="idle" and g.flags.get("passage_braced",false) and not g.flags.get("passage_complete",false) and g.player.position.x>4270:
		g.flags["passage_complete"]=true;g.flags["damaged_passage"]=true
	if stage=="align":
		if not Input.is_action_pressed("interact"):stage="idle"
		elif absf(g.player.position.x-3900)<6:stage="girl_holds"
	elif stage=="girl_holds":
		g.player.action_time=.12
		if absf(g.boy.position.x-4190)<12:
			stage="boy_holds";g.flags["passage_braced"]=true;g.player.action_time=0
			g.announce_message("He catches the support. Now she can pass.",5);g.play_sfx("wheel",-12,Vector2(4160,650),"SUPPORT SECURED - JOIN HIM");g.write_save()
		elif not Input.is_action_pressed("interact"):
			stage="returning";g.player.action_time=0;g.announce_message("The support slips. Give him room to come back, then try again.",4)
	elif stage=="returning":
		if g.boy.position.x<3850:stage="idle";g.boy.following=true
	elif stage=="boy_holds" and g.player.position.x>4270:
		stage="complete";g.flags["passage_complete"]=true;g.flags["damaged_passage"]=true;g.boy.following=true;g.boy.action_time=0
		g.announce_message("She waits until he is beside her again.",4);g.write_save()
	lift=lerpf(lift,1.0 if gate_held() else 0.0,1-exp(-dt*7))
	if g.flags.get("shared_meal",false) and g.in_safe_zone(g.player.position.x,g.player.position.y) and g.player.position.x>7900:
		relief_clock+=dt;g.wetness=maxf(0,g.wetness-dt*.035);g.warmth=minf(100,g.warmth+dt*.6)
	elif not g.in_safe_zone(g.player.position.x,g.player.position.y):g.wetness=minf(1,g.wetness+dt*.035)
	var caught=[]
	for child in [g.player,g.boy]:
		var key=str(child.name)
		var x=child.position.x
		var in_light=(x>5540 and x<7080 and absf(x-beam_x())<100) or (x>2000 and x<3220 and child.position.y<650 and absf(x-shop_beam_x())<95)
		var at_risk=in_light and not g.is_covered(child)
		exposure[key]=clampf(float(exposure[key])+dt*(1.0 if at_risk else -2.2),0,1.7)
		g.child_detection[key]=exposure[key]
		if at_risk:caught.append(child)
	g.exposure=maxf(float(exposure.Girl),float(exposure.Boy))
	if g.exposure>.3 and g.playtime-last_warning>4:
		g.play_sfx("warning",-12,Vector2(shop_beam_x() if g.player.position.x<3450 else beam_x(),650),"SEEN - REACH COVER TOGETHER");last_warning=g.playtime
	if g.exposure>=1.5:
		var who=" and ".join(caught.map(func(c):return str(c.name).to_lower()))
		g.hurt(28,"The light caught "+who+". Reach the next wall together.",caught)
		exposure={"Girl":0.0,"Boy":0.0}
func objective():
	if g.flags.get("last_house_complete",false):return "A room out of the rain. Stay as long as you need."
	if g.player.position.x<1600:return "Explore the house, then choose the shop shelf or the sheltered arcade."
	if g.player.position.x<3450:return "The exposed shelf has supplies. The lower arcade is safer; keep low beneath its floor."
	if not g.flags.get("passage_complete",false):return "Help him through the damaged passage. Let him secure the support for her."
	if g.player.position.x<7400:return "Watch the light. Each wall has room for both of you."
	if not g.flags.get("bag_down",false):return "Bring the bag into the dry room and set it down."
	if not g.flags.get("shared_meal",false):return "Share what you carried."
	return "Spend a quiet moment by the window together."
func paint_house(canvas,center,floor_y,width,tint):
	var scale=width/1774.0
	canvas.draw_texture_rect(house_texture,Rect2(center-width*.5,floor_y-755*scale,width,887*scale),false,tint)
func draw_backdrop(w):
	var cx=g.camera.position.x;var left=cx-800
	w.draw_rect(Rect2(left-100,-350,1800,1500),Color("8c9b9d"))
	w.draw_texture_rect(w.textures.Sky_Painted,Rect2(left-100,-180,1800,1050),false,Color(.60,.73,.76,.75))
	w.scenery("Distant_Hills",.12,2400,650,Color(.56,.66,.66,.62))
	w.scenery("Village_Empty",.27,2600,670,Color(.47,.56,.59,.24))
	# A distant warm window is visible from the first room; its projection
	# hands off to the actual shelter as the pair approaches.
	if cx<7200:
		var far_x=cx+(8500-cx)*.075
		paint_house(w,far_x,650,250,Color(.55,.65,.65,.24))
		w.glow(Vector2(far_x+25,620),Color(.95,.72,.37),16,.12)
	if left<1900:paint_house(w,880,700,1580,Color(.78,.84,.83))
	if left<4600 and left+1700>3350:paint_house(w,3970,700,1180,Color(.64,.73,.72))
	if left+1700>7400:paint_house(w,8550,700,1800,Color(.93,.89,.73))
	# Quiet street and railway planes keep the playable strip distinct.
	# Broken wet strokes sit on the actual ground instead of a translucent
	# screen-wide strip cutting through every pair of legs and room interior.
	for i in range(int(left/43),int((left+1600)/43)+1):
		var x=i*43.0+w.noise_at(i)*18
		if not g.ground_at(x):continue
		w.draw_line(Vector2(x,697),Vector2(x+18+w.noise_at(i+4)*17,696),Color(.48,.58,.56,.13),1.2,true)
	if left+1700>7900:
		w.draw_colored_polygon(PackedVector2Array([Vector2(8730,505),Vector2(8690,700),Vector2(8885,700),Vector2(8790,505)]),Color(.91,.72,.40,.055))
	for rail in [672,682]:w.draw_line(Vector2(4500,rail),Vector2(7330,rail),Color(.47,.51,.47,.65),3,true)
	for x in range(4550,7330,65):w.draw_line(Vector2(x,670),Vector2(x+12,689),Color(.23,.30,.29,.72),6,true)
	for x in [5480,6120,6880]:
		w.draw_line(Vector2(x+100,700),Vector2(x+100,410),Color(.28,.36,.35),8,true)
		w.draw_line(Vector2(x+100,412),Vector2(x+148,421),Color(.33,.41,.38),6,true)
	for beam in [beam_x(),shop_beam_x()]:
		w.draw_colored_polygon(PackedVector2Array([Vector2(beam-220,50),Vector2(beam-100,708),Vector2(beam+100,708)]),Color(.88,.89,.69,.14))
	if g.flags.get("rail_awning",false):w.paint_asset(w,"tent",Vector2(5550,704),520,174,Color(.63,.68,.59))
	w.draw_rect(Rect2(left,700,1600,700),Color("263335"))
func draw_interaction(w,p):
	var pos=Vector2(p.x,p.y)
	match p.kind:
		"inspect":
			w.draw_rect(Rect2(pos+Vector2(-12,-66),Vector2(25,19)),Color("8d8066"));w.draw_rect(Rect2(pos+Vector2(-9,-63),Vector2(19,13)),Color("b0b09b"))
			w.draw_line(pos+Vector2(-19,-44),pos+Vector2(30,-44),Color("4c5143"),7,true)
		"reciprocal":
			var y=620-lift*86
			for x in [3895,4180]:w.paint_beam(Vector2(x,702),Vector2(x,530),18,Color(.49,.52,.40))
			w.paint_beam(Vector2(3880,y),Vector2(4200,y-4),25,Color(.62,.61,.45))
			for x in [3930,4160]:
				w.draw_line(Vector2(x,650),Vector2(x,y-2),Color(.45,.48,.38),3,true)
				w.draw_line(Vector2(x-13,650),Vector2(x+14,650),Color(.67,.65,.48),7,true)
		"bag":
			if g.flags.get("bag_down",false):
				var grip=bag_grip();var b=grip+Vector2(0,17)
				w.draw_colored_polygon(PackedVector2Array([b+Vector2(-16,-12),b+Vector2(13,-13),b+Vector2(18,9),b+Vector2(13,13),b+Vector2(-15,12),b+Vector2(-19,5)]),Color("60634b"))
				w.draw_polyline(PackedVector2Array([b+Vector2(-16,-11),b+Vector2(-2,-4),b+Vector2(14,-11)]),Color(.67,.65,.46,.7),2,true)
				w.draw_arc(grip+Vector2(0,6),7,PI,TAU,12,Color("8a8260"),2.2,true)
				w.draw_line(b+Vector2(-12,1),b+Vector2(-12,10),Color(.25,.31,.25,.6),1,true)
		"share":
			w.paint_asset(w,"stove",pos+Vector2(0,4),104,114,Color(.86,.84,.66));w.glow(pos+Vector2(0,-35),Color(1,.64,.27),185,.24)
			if g.flags.get("shared_meal",false):w.draw_arc(pos+Vector2(40,-24),10,0,PI,16,Color(.65,.64,.48),3,true)
			if beat=="meal" and absf(g.player.position.x-g.boy.position.x)<86:
				var center=(g.player.position+g.boy.position)*.5+Vector2(0,-47)
				w.draw_colored_polygon(PackedVector2Array([center+Vector2(-13,0),center+Vector2(10,-2),center+Vector2(16,5),center+Vector2(-11,7)]),Color("aaa383"))
		"quiet":
			w.glow(pos+Vector2(0,-90),Color(1,.78,.47),130,.12)
		_ :return false
	return true
func draw_weather(canvas):
	var left=g.camera.position.x-800
	for i in range(75):
		var x=left+fposmod(i*83.7-g.clock*84,1700)-50
		var y=fposmod(i*151.7+g.clock*550,760)-30
		if y>230 and g.in_safe_zone(x,700):continue
		canvas.draw_line(Vector2(x,y),Vector2(x-5,y+16),Color(.73,.82,.81,.15),1,true)
	# A few roof-edge drips and foot-level splashes make rain respond to the
	# occupied place. They stay below/behind hands and interaction silhouettes.
	for edge in [[330,535],[1510,580],[3600,578],[4320,600],[7905,525],[9335,565]]:
		var x=float(edge[0]);var roof=float(edge[1])
		if x<left-40 or x>left+1640:continue
		for drop in range(3):
			var y=roof+fposmod(g.clock*470+drop*61+x,700-roof)
			canvas.draw_line(Vector2(x,y),Vector2(x-1,y+7),Color(.66,.78,.77,.22),1,true)
	for child in [g.player,g.boy]:
		if not child.is_on_floor() or g.in_safe_zone(child.position.x,child.position.y):continue
		var phase=fposmod(child.phase*2,1)
		if absf(child.velocity.x)>40 and phase<.28:
			for i in range(3):
				var origin=child.position+Vector2(-child.facing*(3+i*3),-1)
				canvas.draw_line(origin,origin+Vector2(-child.facing*(3+i*2),-3-i*2),Color(.62,.76,.74,(.28-phase)*.9),1,true)

func room_floor(x):return (x>260 and x<1490) or (x>3510 and x<4410) or (x>7860 and x<9370)
func draw_platform(w,p):
	var x=float(p.x);var y=float(p.y);var width=float(p.w)
	# Keep the painted rubble and timber. Sparse joinery sits on its exact tread.
	for joint in range(int(width/86)+1):
		var xx=x+joint*86
		if xx>x+width-8:continue
		w.draw_line(Vector2(xx,y+2),Vector2(xx+3,y+11),Color(.12,.19,.17,.45),1.1,true)
		w.draw_line(Vector2(xx+8,y+2),Vector2(minf(xx+67,x+width),y+2),Color(.58,.61,.49,.23),.9,true)
		w.draw_circle(Vector2(xx+5,y+6),1,Color(.15,.21,.19,.5))
func note_step(child,side):
	if not g.in_safe_zone(child.position.x,child.position.y) and child.is_on_floor():
		footfalls.append({"at":child.foot_lock[side],"age":0.0})
		if footfalls.size()>24:footfalls.pop_front()
func draw_contacts(w):
	var left=g.camera.position.x-800
	# Sparse floorboard seams, rather than a full-width strip across legs.
	for i in range(maxi(0,int(left/81)),int((left+1600)/81)+1):
		var x=i*81.0
		if room_floor(x):
			w.draw_colored_polygon(PackedVector2Array([Vector2(x,700),Vector2(x+79,700),Vector2(x+82,706),Vector2(x-1,706)]),Color(.26,.28,.22,.7))
			w.draw_line(Vector2(x+2,701),Vector2(x+76,701),Color(.61,.55,.38,.25),1,true)
	for patch in [[1650,88],[3420,120],[4760,125],[5070,86],[5950,92],[7130,116],[7650,95]]:
		var x=float(patch[0]);var width=float(patch[1])
		if x<left-160 or x>left+1760 or not g.ground_at(x):continue
		w.draw_colored_polygon(PackedVector2Array([Vector2(x-width*.5,702),Vector2(x-width*.25,699.5),Vector2(x+width*.46,700),Vector2(x+width*.55,704),Vector2(x+width*.1,708),Vector2(x-width*.48,707)]),Color(.47,.59,.58,.16))
		w.draw_line(Vector2(x-width*.4,701),Vector2(x+width*.3,701),Color(.67,.74,.67,.18),.9,true)
	for step in footfalls:
		var ring=PackedVector2Array();var radius=2+step.age*22
		for i in range(15):ring.append(step.at+Vector2(cos(i*TAU/14)*radius,2+sin(i*TAU/14)*radius*.2))
		w.draw_polyline(ring,Color(.59,.70,.65,(.65-step.age)*.3),.9,true)
