extends Control

var game
var display_font=preload("res://assets/fonts/display.ttf")
var ui_font=preload("res://assets/fonts/interface.ttf")
var selected=0
var hover=-1
var buttons=[]
var palette=Color("e2e4d6")
var gold=Color("beb38c")
var dim=Color("93a29b")
var memory_page=0

func _ready(): mouse_filter=Control.MOUSE_FILTER_IGNORE
func _process(_dt): queue_redraw()

func text_at(text,pos,size=20,color=Color("e2e4d6"),serif=false):
	draw_string(display_font if serif else ui_font,pos,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func center(text,y,size=22,color=Color("e2e4d6"),serif=false):
	var f=display_font if serif else ui_font
	var width=f.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x
	draw_string(f,Vector2((1600-width)/2,y),text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func rule(x,y,w,col=Color("667873")): draw_line(Vector2(x,y),Vector2(x+w,y),col,1,true)

func paragraph(text,pos,width=530,size=18,color=Color("aab5ad")):
	var line=""; var y=pos.y
	for word in text.split(" "):
		if ui_font.get_string_size(line+word,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x>width:
			text_at(line,Vector2(pos.x,y),size,color); y+=size*1.6; line=""
		line+=word+" "
	text_at(line,Vector2(pos.x,y),size,color)
	return y

func button(label,rect,action,enabled=true):
	var index=buttons.size()
	buttons.append({"rect":rect,"action":action,"enabled":enabled})
	var active=(index==selected or index==hover) and enabled
	if active:
		draw_rect(rect,Color(.42,.48,.39,.14))
		draw_line(rect.position+Vector2(0,5),rect.position+Vector2(0,rect.size.y-5),gold,2,true)
	text_at(label,rect.position+Vector2(24,rect.size.y*.64),22,gold if active else (palette if enabled else Color("53625e")))
	if active: text_at("›",rect.position+Vector2(rect.size.x-32,rect.size.y*.65),24,gold)

func _draw():
	if game==null: return
	buttons.clear()
	var mode=game.mode
	# Subtle letterbox and edge falloff preserve a quiet cinematic frame.
	draw_rect(Rect2(0,0,1600,27),Color(.025,.04,.04,.9))
	draw_rect(Rect2(0,873,1600,27),Color(.025,.04,.04,.9))
	for i in range(18):
		var a=(18-i)*.0007
		draw_rect(Rect2(i*7,27,7,846),Color(0,0,0,a))
		draw_rect(Rect2(1600-i*7-7,27,7,846),Color(0,0,0,a))
	if mode=="menu": title_screen()
	elif mode=="pause": pause_screen()
	elif mode=="chapters": chapter_screen()
	elif mode=="settings": settings_screen()
	elif mode=="inventory": pack_screen()
	elif mode in ["stillness","ending"] and game.story.active: stillness_screen()
	elif mode=="ending": ending_screen()
	elif mode=="recovering":
		var alpha=sin(clampf(1-game.recovery_clock/1.4,0,1)*PI)*.92+.05
		draw_rect(Rect2(0,0,1600,900),Color(.025,.045,.052,alpha))
		center("Hold on to each other.",438,45,Color(palette,.8),true)
	else: playing_hud()

func title_screen():
	for i in range(38): draw_rect(Rect2(i*25,27,25,846),Color(.027,.055,.055,.94-i*.018))
	text_at("THE ROAD USED TO LEAD HOME",Vector2(119,158),13,gold)
	rule(120,185,64,gold)
	text_at("When the",Vector2(112,301),77,palette,true)
	text_at("Sky Clears",Vector2(112,385),103,palette,true)
	paragraph("A road you knew. A child who trusts you to find it again.",Vector2(120,438),450,20,Color("aebbad"))
	var y=527
	if game.save_exists:
		button("Continue the journey",Rect2(112,y,410,49),"continue"); y+=52
	button("Begin a new journey",Rect2(112,y,410,49),"new"); y+=52
	button("Freight crossing rehearsal",Rect2(112,y,410,49),"crossing"); y+=52
	button("Chapters",Rect2(112,y,410,49),"chapters"); y+=52
	button("Settings & controls",Rect2(112,y,410,49),"settings"); y+=52
	button("Leave",Rect2(112,y,410,49),"quit")
	text_at("A PAINTED STORY OF DISPLACEMENT",Vector2(119,844),11,dim)
	text_at("DEVELOPMENT  0.4.0",Vector2(1338,847),10,dim)
	text_at("Wait until he catches up.",Vector2(1138,816),19,Color(palette,.75),true)

func playing_hud():
	var presence=game.story.hud_presence
	if presence>.02:
		text_at("%02d"%(game.chapter+1),Vector2(63,78),20,Color(gold,presence),true)
		rule(103,70,36,Color(gold,presence*.5))
		text_at(game.level.subtitle,Vector2(156,77),12,Color(palette,presence))
		# Healthy stretches leave room for the painting. A low resource or a
		# real hazard restores these meters before the critical thresholds.
		draw_rect(Rect2(48,795,448,51),Color(.025,.05,.055,.35*presence))
		bar("STRENGTH",game.health,Vector2(64,813),96,Color("b6b598"),presence)
		bar("WARMTH",game.warmth,Vector2(188,813),96,Color("9baaa4"),presence)
		bar("FOOD",game.food,Vector2(312,813),96,Color("a4b495"),presence)
	text_at("TAB  PACK",Vector2(64,857),10,dim)
	var waiting=not game.boy.following
	text_at("Q  "+("COME WITH ME" if waiting else "WAIT HERE"),Vector2(1320,77),11,gold if waiting else dim)
	if absf(game.player.position.x-game.boy.position.x)>280:
		text_at("HE IS BEHIND YOU" if game.player.position.x>game.boy.position.x else "HE IS AHEAD",Vector2(1270,105),12,palette)
	if game.stamina<93: bar("",game.stamina,Vector2(64,867),344,Color(.7,.76,.65,.75))
	if game.listening_near:
		draw_rect(Rect2(1040,756,380,54),Color(.025,.05,.055,.72))
		bar("SOUND",game.noise_level*100,Vector2(1064,774),130,Color("c8b58d"))
		bar("HEARD",game.heard_level*100,Vector2(1228,774),130,Color("c99078"))
	if game.wetness>.12: text_at("WET CLOTHES",Vector2(64,784),11,Color("8eb2bd"))
	if game.in_water(game.boy.position.x,game.boy.position.y) and not game.in_water(game.player.position.x,game.player.position.y):
		text_at("HE IS STILL IN THE WATER",Vector2(64,762),11,Color("b8c9bd"))
	var warning=game.lane_warning
	if game.shell_warning>0: warning="TAKE COVER  ·  HOLD S  ·  KEEP HIM CLOSE"
	if game.exposure>.1: warning="SEEN  ·  REACH COVER TOGETHER"
	if warning!="":
		var width=ui_font.get_string_size(warning,HORIZONTAL_ALIGNMENT_LEFT,-1,12).x
		draw_rect(Rect2(1536-width-18,823,width+36,37),Color(.025,.05,.055,.85))
		text_at(warning,Vector2(1536-width,847),12,Color("e1c69c"))
	elif game.sheltered and presence>.05:
		text_at("SHELTERED TOGETHER",Vector2(1290,847),11,Color(Color("b5c9ad"),presence))
	if not game.pending_action.is_empty():
		var progress=clampf(game.action_progress/maxf(.01,game.action_duration),0,1)
		var point=game.get_viewport().get_canvas_transform()*game.player.global_position+Vector2(0,-151)
		draw_arc(point,16,-PI/2,TAU-PI/2,40,Color(.5,.6,.55,.35),2,true)
		draw_arc(point,16,-PI/2,-PI/2+progress*TAU,40,gold,2.5,true)
		text_at("E",point+Vector2(-4,5),12,palette)
	if game.prompt!="":
		var w=ui_font.get_string_size(game.prompt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
		draw_rect(Rect2((1600-w)/2-24,727,w+48,41),Color(.035,.07,.075,.85))
		center(game.prompt,753,15,palette)
	# Warnings stay legible during chapter cards. Other notices take turns.
	if game.message_time>0 and game.chapter_card<=0:
		var fade=minf(1,game.message_time)
		var notice_width=minf(1240,display_font.get_string_size(game.message,HORIZONTAL_ALIGNMENT_LEFT,-1,22).x+52)
		draw_style_box(notice_backplate(fade),Rect2((1600-notice_width)*.5,111,notice_width,52))
		center(game.message,145,22,Color(palette,fade),true)
	if game.chapter_card>0:
		var alpha=minf(1,game.chapter_card/1.3)*minf(1,(5.5-game.chapter_card)*1.3)
		center(game.level.title,280,58,Color(palette,alpha),true)
		center(game.level.epigraph,325,22,Color(palette,alpha*.8),true)

func bar(label,value,pos,width,color,alpha=1.0):
	if label!="": text_at(label,pos,9,Color(dim,alpha))
	draw_rect(Rect2(pos+Vector2(0,13),Vector2(width,3)),Color(.5,.58,.53,.2*alpha))
	draw_rect(Rect2(pos+Vector2(0,13),Vector2(width*clampf(value/100,0,1),3)),Color(color if value>20 else Color("c0947c"),alpha))

func notice_backplate(alpha):
	var plate=StyleBoxFlat.new()
	plate.bg_color=Color(.045,.065,.06,.48*alpha)
	plate.corner_radius_top_left=5; plate.corner_radius_top_right=5
	plate.corner_radius_bottom_left=5; plate.corner_radius_bottom_right=5
	return plate

func stillness_screen():
	# The world stays visible. A broad, quiet lower matte carries one line.
	for i in range(24):
		draw_rect(Rect2(0,612+i*11,1600,11),Color(.025,.045,.05,.012+i*.014))
	var line=game.story.visible_line()
	var local_time=game.story.elapsed-(1.1 if line==str(game.story.current.lines[0]) else (6.8 if game.story.final_moment else 4.8))
	var alpha=clampf(local_time/1.2,0,1)
	center(line,731,32,Color(palette,alpha),true)
	if game.story.elapsed>1.0:
		button("Continue" if game.story.final_moment else "Return to the road",Rect2(604,794,392,48),"leave_moment")
	text_at("You can stay here.",Vector2(65,848),13,dim,true)

func overlay(): draw_rect(Rect2(0,0,1600,900),Color(.025,.05,.055,.9))

func pause_screen():
	overlay(); text_at("A MOMENT TO BREATHE",Vector2(155,204),13,gold)
	text_at("Stay with me.",Vector2(149,300),76,palette,true)
	text_at(game.level.title,Vector2(155,348),22,dim,true)
	button("Return to the road",Rect2(145,408,440,56),"resume")
	button("Return to the last shelter",Rect2(145,470,440,56),"restart")
	button("Open the pack",Rect2(145,532,440,56),"pack")
	button("Settings & controls",Rect2(145,594,440,56),"settings")
	button("Save & return to title",Rect2(145,656,440,56),"menu")
	rule(930,304,390,Color(gold,.35))
	paragraph(game.level.epigraph,Vector2(930,349),390,24,palette)
	paragraph("Progress saves at lanterns, shelters and chapter crossings. Supplies and remembered things stay with you.",Vector2(930,489),390,17,dim)
	text_at("ESC  RETURN",Vector2(155,810),12,dim)

func chapter_screen():
	overlay(); text_at("THE ROAD AHEAD",Vector2(148,163),13,gold)
	text_at("Five chapters. One journey.",Vector2(142,238),60,palette,true)
	for i in range(5):
		var l=game.levels[i]
		var unlocked=i<=game.unlocked
		button("%02d    %s"%[i+1,l.title],Rect2(140,295+i*82,700,64),"chapter_"+str(i),unlocked)
		text_at(l.subtitle if unlocked else "Continue the journey to reach this place.",Vector2(893,336+i*82),12,dim)
	button("Back",Rect2(140,740,320,55),"back")

func settings_screen():
	overlay(); text_at("MAKE ROOM FOR THE JOURNEY",Vector2(142,140),12,gold)
	text_at("Settings & controls",Vector2(136,216),62,palette,true)
	text_at("Sound",Vector2(143,298),21,palette)
	button("−",Rect2(140,325,85,48),"quieter")
	button("+",Rect2(415,325,85,48),"louder")
	text_at(str(roundi(game.volume*100))+"%",Vector2(292,357),22,gold)
	button("Sound: "+("muted" if game.muted else "on"),Rect2(140,398,440,50),"mute")
	button("Motion: "+("reduced" if game.reduced_motion else "full"),Rect2(140,461,440,50),"motion")
	button("Toggle fullscreen",Rect2(140,524,440,50),"fullscreen")
	button("Survival HUD: "+("always visible" if game.always_show_hud else "when needed"),Rect2(140,587,510,50),"hud_visibility")
	button("Back",Rect2(140,691,440,52),"back")
	text_at("ON THE ROAD",Vector2(840,295),12,gold)
	var controls=[["A / D or ← / →","Move"],["SPACE / W / ↑","Jump · release early for a short jump"],["SHIFT","Run · uses stamina"],["S / ↓","Crouch · shelter behind cover"],["HOLD E","Search · work · rest / push + A/D"],["Q","Ask him to wait / call him"],["H","Use one medicine"],["TAB","Open the pack"],["R / ESC","Last checkpoint / pause"],["F11 / M","Fullscreen / mute"]]
	for i in range(controls.size()):
		text_at(controls[i][0],Vector2(842,336+i*34),14,palette)
		text_at(controls[i][1],Vector2(1030,336+i*34),14,dim)
	paragraph("Controller: left stick / D-pad move · A jump · B crouch · X interact · Y wait/call · RB run · Back pack · Start pause.",Vector2(841,725),580,14,dim)

func pack_screen():
	overlay(); text_at("WHAT WE CARRY",Vector2(139,148),12,gold)
	text_at("A little, shared.",Vector2(132,230),67,palette,true)
	var supplies=[[str(game.rations)+"/4","RATIONS","At a fire, share one to restore nourishment, warmth and strength. The pack has room for four."],[str(game.scrap)+"/3","SALVAGE","Three useful pieces fit in the pack. Drain a cold crossing, secure a high route, or save them for the next roof. Extra supplies stay where you found them."],[str(game.medicine)+"/2","MEDICINE","Press H to use one dressing. Carry at most two. A child left exposed can cost you both the journey."]]
	for i in range(3):
		var y=324+i*139
		text_at(supplies[i][0],Vector2(142,y),56,gold,true)
		text_at(supplies[i][1],Vector2(232,y-24),12,palette)
		paragraph(supplies[i][2],Vector2(232,y+9),390,15,dim)
	rule(786,273,1,dim)
	text_at("THE THINGS WE REMEMBER",Vector2(856,286),12,gold)
	var pages=game.story.kept_pages()
	var page_count=maxi(1,ceili(pages.size()/4.0))
	memory_page=clampi(memory_page,0,page_count-1)
	var y=334
	if pages.is_empty():
		paragraph("There is room for the little things. What you notice. Where you stop together.",Vector2(856,y),520,20,dim)
	else:
		for line in pages.slice(memory_page*4,mini(pages.size(),memory_page*4+4)):
			y=paragraph(line,Vector2(856,y),520,17,palette)+34
	if page_count>1:
		button("Previous",Rect2(841,686,180,44),"page_previous",memory_page>0)
		text_at("%d / %d"%[memory_page+1,page_count],Vector2(1085,714),13,dim)
		button("Next",Rect2(1200,686,180,44),"page_next",memory_page<page_count-1)
	bar("STRENGTH",game.health,Vector2(142,708),126,Color("b6b598"))
	bar("WARMTH",game.warmth,Vector2(312,708),126,Color("9baaa4"))
	bar("FOOD",game.food,Vector2(482,708),126,Color("a4b495"))
	text_at("NEXT",Vector2(142,747),11,gold)
	text_at(game.current_objective(),Vector2(142,779),19,palette,true)
	button("Return to the road",Rect2(1140,786,320,48),"resume")

func ending_screen():
	draw_rect(Rect2(0,0,1600,900),Color(.04,.075,.085,.89))
	center("A LITTLE FURTHER, TOGETHER",197,12,gold)
	center("When the Sky Clears",324,88,palette,true)
	center("The road has not given them back what it took.",410,30,palette,true)
	center("For now, there is a hand to hold.",453,30,palette,true)
	rule(720,505,160,Color(gold,.5))
	center("You can rest here.",553,21,dim,true)
	center("An original game adaptation of Conrad Weeden’s story.",624,16,dim)
	center("Original project paintings · drawn children · painted props · Kenney footstep sounds",657,13,dim)
	button("Walk the road again",Rect2(603,719,394,52),"new")
	button("Return to title",Rect2(603,777,394,52),"menu")

func _input(event):
	if game==null or game.mode in ["playing","recovering"]: return
	if event is InputEventMouseMotion:
		hover=-1
		for i in range(buttons.size()):
			if buttons[i].rect.has_point(event.position): hover=i; selected=i; break
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT:
		for b in buttons:
			if b.rect.has_point(event.position) and b.enabled:
				activate(b.action); get_viewport().set_input_as_handled(); return
	if event.is_action_pressed("ui_down"):
		selected=posmod(selected+1,maxi(1,buttons.size()))
	if event.is_action_pressed("ui_up"):
		selected=posmod(selected-1,maxi(1,buttons.size()))
	if event.is_action_pressed("ui_accept") and not buttons.is_empty():
		var b=buttons[clampi(selected,0,buttons.size()-1)]
		if b.enabled:
			activate(b.action); get_viewport().set_input_as_handled()

func activate(action):
	match action:
		"crossing": game.start_crossing()
		"new": game.new_journey()
		"continue": game.continue_journey()
		"resume": game.resume_journey()
		"leave_moment": game.story.finish()
		"page_previous": memory_page=maxi(0,memory_page-1)
		"page_next": memory_page+=1
		"restart": game.mode="playing"; game.recover(false)
		"pack": game.mode="inventory"
		"chapters": game.settings_return="menu"; game.mode="chapters"
		"settings": game.settings_return=game.mode; game.mode="settings"
		"back": game.mode=game.settings_return
		"menu": game.story.reset(); game.write_save(); game.mode="menu"
		"quit": game.quit_game()
		"mute": game.muted=not game.muted; game.apply_volume(); game.write_save()
		"motion": game.reduced_motion=not game.reduced_motion; game.write_save()
		"hud_visibility": game.always_show_hud=not game.always_show_hud; game.write_save()
		"louder": game.volume=minf(1,game.volume+.1); game.apply_volume(); game.write_save()
		"quieter": game.volume=maxf(0,game.volume-.1); game.apply_volume(); game.write_save()
		"fullscreen": DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode()==DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
	if action.begins_with("chapter_"):
		var idx=int(action.trim_prefix("chapter_"))
		if idx<=game.unlocked:
			if game.save_exists: game.load_save(true)
			game.journey_active=true; game.load_chapter(idx); game.mode="playing"; game.write_save()
	selected=0; hover=-1

