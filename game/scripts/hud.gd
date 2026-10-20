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

func _ready(): mouse_filter=Control.MOUSE_FILTER_IGNORE
func _process(_dt): queue_redraw()

func ui_size(size):return roundi(size*game.access.text_scale) if size<=28 else size
func text_at(text,pos,size=20,color=Color("e2e4d6"),serif=false):
	draw_string(display_font if serif else ui_font,pos,text,HORIZONTAL_ALIGNMENT_LEFT,-1,ui_size(size),color)
func center(text,y,size=22,color=Color("e2e4d6"),serif=false):
	var f=display_font if serif else ui_font
	var actual=ui_size(size);var line="";var lines=[]
	for word in text.split(" "):
		if f.get_string_size(line+word,HORIZONTAL_ALIGNMENT_LEFT,-1,actual).x>1420 and line!="":lines.append(line.strip_edges());line=""
		line+=word+" "
	lines.append(line.strip_edges())
	for i in range(lines.size()):
		var width=f.get_string_size(lines[i],HORIZONTAL_ALIGNMENT_LEFT,-1,actual).x
		draw_string(f,Vector2((1600-width)/2,y+i*actual*1.2),lines[i],HORIZONTAL_ALIGNMENT_LEFT,-1,actual,color)

func rule(x,y,w,col=Color("667873")): draw_line(Vector2(x,y),Vector2(x+w,y),col,1,true)

func paragraph(text,pos,width=530,size=18,color=Color("aab5ad")):
	var line="";var y=pos.y;var actual=ui_size(size)
	for word in text.split(" "):
		if ui_font.get_string_size(line+word,HORIZONTAL_ALIGNMENT_LEFT,-1,actual).x>width and line!="":
			text_at(line,Vector2(pos.x,y),size,color);y+=actual*1.4;line=""
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
	var size=ui_size(20)
	while size>16 and ui_font.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x>rect.size.x-66:size-=1
	draw_string(ui_font,rect.position+Vector2(22,rect.size.y*.65),label,HORIZONTAL_ALIGNMENT_LEFT,-1,size,gold if active else (palette if enabled else Color("53625e")))
	if active: text_at("›",rect.position+Vector2(rect.size.x-32,rect.size.y*.65),24,gold)

func _draw():
	if game==null: return
	buttons.clear()
	var mode=game.mode
	# Subtle letterbox and edge falloff preserve a quiet cinematic frame.
	draw_rect(Rect2(0,0,1600,27),Color(.025,.04,.04,.9))
	draw_rect(Rect2(0,873,1600,27),Color(.025,.04,.04,.9))
	for i in range(18):
		var a=(18-i)*.0016
		draw_rect(Rect2(i*7,27,7,846),Color(0,0,0,a))
		draw_rect(Rect2(1600-i*7-7,27,7,846),Color(0,0,0,a))
	if mode=="menu": title_screen()
	elif mode=="pause": pause_screen()
	elif mode=="chapters": chapter_screen()
	elif mode=="settings": settings_screen()
	elif mode=="inventory": pack_screen()
	elif mode=="ending": ending_screen()
	elif mode=="recovering":
		var alpha=sin(clampf(1-game.recovery_clock/1.4,0,1)*PI)*.92+.05
		draw_rect(Rect2(0,0,1600,900),Color(.025,.045,.052,alpha))
		center("Hold on to each other.",438,45,Color(palette,.8),true)
	else: playing_hud()

func title_screen():
	for i in range(38): draw_rect(Rect2(i*25,27,25,846),Color(.027,.055,.055,.94-i*.018))
	text_at("A STORY OF WHAT WE CARRY",Vector2(119,158),13,gold)
	rule(120,185,64,gold)
	text_at("When the",Vector2(112,301),77,palette,true)
	text_at("Sky Clears",Vector2(112,385),103,palette,true)
	paragraph("Two children. A road through a world coming apart. Keep moving. Keep each other.",Vector2(120,438),460,18,Color("aebbad"))
	var y=501
	if game.save_exists:
		button("Continue the journey",Rect2(112,y,560,42),"continue"); y+=44
	button("Begin a new journey",Rect2(112,y,560,42),"new"); y+=44
	button("Last House before the Crossing",Rect2(112,y,560,42),"last_house"); y+=44
	button("Freight crossing rehearsal",Rect2(112,y,560,42),"crossing"); y+=44
	button("Chapters",Rect2(112,y,560,42),"chapters"); y+=44
	button("Settings & controls",Rect2(112,y,560,42),"settings"); y+=44
	button("Leave",Rect2(112,y,560,42),"quit")
	text_at("AN ORIGINAL SURVIVAL JOURNEY",Vector2(119,844),11,dim)
	if not game.save_notice.is_empty(): paragraph(game.save_notice,Vector2(920,716),580,15,gold)
	text_at("DEVELOPMENT  0.5.3",Vector2(1338,847),10,dim)
	text_at("Move with care. There is someone behind you.",Vector2(1015,816),17,Color(palette,.65),true)

func playing_hud():
	text_at("%02d"%(game.chapter+1),Vector2(63,78),20,gold,true)
	rule(103,70,36,Color(gold,.5))
	text_at(game.level.subtitle,Vector2(156,77),12,palette)
	for sector in game.level.get("zones",[]):
		if game.player.position.x>=sector.x and game.player.position.x<sector.x+sector.w:
			text_at(sector.get("name",str(sector.theme).replace("_"," ").to_upper()),Vector2(156,99),10,dim)
	var helping=game.slice_active and game.last_house.is_helping()
	text_at("HELPING EACH OTHER" if helping else game.access.label("companion")+"  "+("STAY CLOSE" if game.boy.following else "WAITING"),Vector2(1170,77),11,gold if helping or not game.boy.following else dim)
	for info in [[game.player,1010],[game.boy,1250]]:
		var state=game.child_status(info[0]);var color=Color("e2b979") if state in ["SEEN","HURT"] else Color("bdcdb5")
		text_at(str(info[0].name).to_upper()+" / "+state,Vector2(info[1],103),12,color)
	# Compact survival indicators, always readable against any painted zone.
	draw_rect(Rect2(48,795,448,51),Color(.025,.05,.055,.49))
	bar("STRENGTH",game.health,Vector2(64,813),96,Color("b6b598"))
	bar("WARMTH",game.warmth,Vector2(188,813),96,Color("9baaa4"))
	bar("FOOD",game.food,Vector2(312,813),96,Color("a4b495"))
	text_at(game.access.label("pack"),Vector2(445,829),10,dim)
	if game.stamina<93: bar("",game.stamina,Vector2(64,843),344,Color(.7,.76,.65,.55))
	if game.wetness>.12: text_at("WET CLOTHES",Vector2(64,784),10,Color("8eb2bd"))
	if game.lane_warning!="":
		text_at(game.lane_warning,Vector2(1010,842),10,Color("d8ba87"))
	if game.sheltered:
		text_at("SHELTERED TOGETHER",Vector2(1238,817),11,Color("b5c9ad"))
	elif game.exposure>.1:
		text_at("SEEN  ·  REACH COVER",Vector2(1240,817),12,Color("d2b78c"))
	elif game.shell_warning>0:
		text_at("TAKE COVER - "+game.access.label("crouch"),Vector2(1236,817),12,Color("d8ba87"))
	else: text_at(game.access.label("interact")+" INTERACT / HOLD WHEN SHOWN",Vector2(1178,817),10,dim)
	if not game.pending_action.is_empty():
		var progress=clampf(game.action_progress/maxf(.01,game.action_duration),0,1)
		var point=game.get_viewport().get_canvas_transform()*game.player.global_position+Vector2(0,-151)
		draw_arc(point,16,-PI/2,TAU-PI/2,40,Color(.5,.6,.55,.35),2,true)
		draw_arc(point,16,-PI/2,-PI/2+progress*TAU,40,gold,2.5,true)
		text_at(game.access.label("interact"),point+Vector2(-8,5),10,palette)
	if game.prompt!="":
		var w=minf(1430,ui_font.get_string_size(game.prompt,HORIZONTAL_ALIGNMENT_LEFT,-1,ui_size(15)).x)
		draw_rect(Rect2((1600-w)/2-24,727,w+48,41),Color(.035,.07,.075,.74))
		center(game.prompt,753,15,palette)
	if game.message_time>0:
		var fade=minf(1,game.message_time)
		center(game.control_text(game.message),142,25,Color(palette,fade),true)
	if game.soundscape.caption_time>0:
		draw_rect(Rect2(320,206,960,45),Color(.025,.045,.05,.88));center(game.soundscape.caption,237,17,gold)
	if game.slice_active and game.player.position.x>1600 and game.player.position.x<2400 and game.pending_action.is_empty() and game.chapter_card<=0:
		draw_rect(Rect2(430,263,740,67),Color(.025,.045,.05,.75))
		center("UPPER SHELF: supplies, exposed to the light",288,15,gold)
		center("LOWER ARCADE: sheltered, fewer supplies",314,15,palette)
	if game.slice_active and game.player.crouching and game.player.position.x>5200 and game.player.position.x<7300:
		text_at("BOTH COVERED - WATCH THE LIGHT" if game.sheltered else "WAIT FOR BOTH TO REACH COVER",Vector2(1010,176),12,gold)
	if game.chapter_card>0:
		var alpha=minf(1,game.chapter_card/1.3)*minf(1,(5.5-game.chapter_card)*1.3)
		center(game.level.title,280,58,Color(palette,alpha),true)
		center(game.level.epigraph,325,22,Color(palette,alpha*.8),true)

func bar(label,value,pos,width,color):
	if label!="": text_at(label,pos,9,dim)
	draw_rect(Rect2(pos+Vector2(0,13),Vector2(width,3)),Color(.5,.58,.53,.2))
	draw_rect(Rect2(pos+Vector2(0,13),Vector2(width*clampf(value/100,0,1),3)),color if value>20 else Color("c0947c"))

func overlay(): draw_rect(Rect2(0,0,1600,900),Color(.025,.05,.055,.9))

func pause_screen():
	overlay(); text_at("A MOMENT TO BREATHE",Vector2(155,204),13,gold)
	text_at("Stay with me.",Vector2(149,300),76,palette,true)
	text_at(game.level.title,Vector2(155,348),22,dim,true)
	button("Return to the road",Rect2(145,408,600,56),"resume")
	button("Return to the last shelter",Rect2(145,470,600,56),"restart")
	button("Open the pack",Rect2(145,532,600,56),"pack")
	button("Settings & controls",Rect2(145,594,600,56),"settings")
	button("Save & return to title",Rect2(145,656,600,56),"menu")
	if game.slice_active: button("Begin Last House again",Rect2(145,718,600,56),"last_house_new")
	rule(930,304,390,Color(gold,.35))
	paragraph(game.level.epigraph,Vector2(930,349),530,24,palette)
	paragraph("Progress saves at lanterns, shelters and chapter crossings. Supplies and remembered things stay with you.",Vector2(930,565),530,17,dim)
	text_at("Esc / Start / B: return",Vector2(155,810),12,dim)

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
	overlay();text_at("MAKE ROOM FOR THE JOURNEY",Vector2(142,95),12,gold)
	text_at("Settings & controls",Vector2(136,163),54,palette,true)
	var a=game.access
	for tab in [["Sound","sound",140],["Access","access",540],["Bindings","bindings",940]]:
		button(tab[0]+(" *" if a.page==tab[1] else ""),Rect2(tab[2],200,360,48),"tab_"+tab[1])
	if a.page=="sound":
		var rows=[["Master",game.volume],["Music",a.mix.Music],["Weather",a.mix.Weather],["Actions",a.mix.Actions],["Threat",a.mix.Threat]]
		for i in range(rows.size()):
			var y=285+i*68
			text_at(rows[i][0]+"  "+str(roundi(float(rows[i][1])*100))+"%",Vector2(155,y+30),20,palette)
			button("-",Rect2(500,y,100,48),"vol_"+rows[i][0]+"_-1")
			button("+",Rect2(620,y,100,48),"vol_"+rows[i][0]+"_1")
		button("Sound: "+("muted" if game.muted else "on"),Rect2(840,285,600,54),"mute")
		button("Preview action + threat cues",Rect2(840,355,600,54),"preview_audio")
		paragraph("Threats lower rain and music briefly. Critical events also use text and each child's state label. Master zero is silent.",Vector2(855,466),560,18,dim)
	elif a.page=="access":
		button("Text size: "+str(roundi(a.text_scale*100))+"%",Rect2(140,290,620,58),"text_scale")
		button("Crouch: "+("toggle" if a.crouch_toggle else "hold (default)"),Rect2(140,364,620,58),"crouch_toggle")
		button("Motion: "+("reduced" if game.reduced_motion else "full"),Rect2(140,438,620,58),"motion")
		button("Toggle fullscreen",Rect2(140,512,620,58),"fullscreen")
		button("Reset settings & controls...",Rect2(140,586,620,58),"reset_confirm")
		paragraph("Text size changes interface and prompt text. Large display titles stay fixed; long button labels fit their available width. Toggle crouch stays low until pressed again; overhead clearance still prevents standing.",Vector2(855,321),570,18,dim)
	elif a.page=="bindings":
		button("Edit: "+a.bind_device,Rect2(140,272,620,50),"bind_device")
		text_at("Left stick always moves. Menu: arrows / D-pad, Enter / A, Esc / B / Start.",Vector2(140,358),14,dim)
		for i in range(a.ACTIONS.size()):
			var action=a.ACTIONS[i];var col=i/5;var row=i%5
			button(a.NAMES[action]+": "+a.label(action,a.bind_device),Rect2(140+col*680,390+row*58,650,50),"bind_"+action)
		paragraph(a.notice if a.notice!="" else "Choose an action, then press its new input. Conflicts are rejected. Esc / Start cancels capture.",Vector2(150,725),1280,16,gold)
	elif a.page=="reset":
		paragraph("Restore default sound, text, motion, crouch and gameplay bindings? Journey and section saves are kept.",Vector2(160,340),1200,24,palette)
		button("Restore defaults",Rect2(150,500,600,65),"confirm_reset")
		button("Keep my settings",Rect2(830,500,600,65),"tab_access")
	if a.page!="bindings" and a.notice!="":paragraph(a.notice,Vector2(150,735),1270,15,gold)
	if a.rebind_action!="":
		draw_rect(Rect2(170,405,1260,165),Color(.025,.05,.055,.98));center("Binding: "+a.NAMES[a.rebind_action],455,26,gold)
		center(a.notice,512,18,palette)
	button("Back",Rect2(140,806,620,54),"back")
	text_at("Arrows / D-pad: choose    Enter / A: select    Esc / B: back",Vector2(825,840),13,dim)

func pack_screen():
	overlay(); text_at("WHAT WE CARRY",Vector2(139,148),12,gold)
	text_at("A little, shared.",Vector2(132,230),67,palette,true)
	var supplies=[[str(game.rations)+"/4","RATIONS","At a fire, share one to restore nourishment, warmth and strength. The pack has room for four."],[str(game.scrap)+"/6","SALVAGE","Tools, wire, useful fragments. Some doors can be made safe. Extra supplies stay where you found them."],[str(game.medicine)+"/2","MEDICINE","Use "+game.access.label("heal")+" for one dressing. Carry at most two. A child left exposed can cost you both the journey."]]
	for i in range(3):
		var y=324+i*139
		text_at(supplies[i][0],Vector2(142,y),56,gold,true)
		text_at(supplies[i][1],Vector2(232,y-24),12,palette)
		paragraph(supplies[i][2],Vector2(232,y+9),390,15,dim)
	rule(786,273,1,dim)
	text_at("THE THINGS WE REMEMBER",Vector2(856,286),12,gold)
	var total_memories=0
	for l in game.levels: total_memories+=l.memories.size()
	text_at("%d / %d"%[game.memories.size(),total_memories],Vector2(1300,288),21,palette,true)
	var y=334
	if game.memories.is_empty():
		paragraph("Look for small scraps of paper off the main road. Some things are worth keeping, even now.",Vector2(856,y),520,19,dim)
	else:
		for key in game.memories:
			y=paragraph(game.memories[key],Vector2(856,y),520,15,palette)+37
			if y>740: break
	text_at("NEXT",Vector2(142,747),11,gold)
	paragraph(game.current_objective(),Vector2(142,779),900,17,palette)
	button("Return to the road",Rect2(1140,786,320,48),"resume")

func ending_screen():
	draw_rect(Rect2(0,0,1600,900),Color(.04,.075,.085,.89))
	center("THE HAND THAT STAYED",197,12,gold)
	center("When the Sky Clears",324,88,palette,true)
	center("They had very little left.",410,30,palette,true)
	center("They still had each other.",453,30,palette,true)
	rule(720,505,160,Color(gold,.5))
	center("%d things remembered  ·  %d minutes on the road"%[game.memories.size(),maxi(1,int(game.playtime/60))],553,15,dim)
	center("An original game adaptation of Conrad Weeden’s story.",624,16,dim)
	center("Original project paintings · drawn children · painted props · Kenney footstep sounds",657,13,dim)
	button("Walk the road again",Rect2(603,719,394,52),"new")
	button("Return to title",Rect2(603,777,394,52),"menu")

func _input(event):
	if game==null or game.mode in ["playing","recovering"]: return
	if game.access.observe(event):get_viewport().set_input_as_handled();return
	if event is InputEventKey and event.echo:return
	var pad_pressed=event is InputEventJoypadButton and event.pressed
	var cancel=event.is_action_pressed("ui_cancel") or (pad_pressed and event.button_index==JOY_BUTTON_B)
	if cancel and game.mode in ["settings","chapters","pause","inventory"]:
		if game.mode=="settings" and game.access.page!="sound":game.access.page="sound"
		elif game.mode in ["pause","inventory"]:game.mode="playing"
		else:game.mode=game.settings_return
		selected=0;get_viewport().set_input_as_handled();return
	if event is InputEventMouseMotion:
		hover=-1
		for i in range(buttons.size()):
			if buttons[i].rect.has_point(event.position): hover=i; selected=i; break
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT:
		for b in buttons:
			if b.rect.has_point(event.position) and b.enabled: activate(b.action); return
	if event.is_action_pressed("ui_down") or (pad_pressed and event.button_index==JOY_BUTTON_DPAD_DOWN):
		selected=posmod(selected+1,maxi(1,buttons.size()))
	if event.is_action_pressed("ui_up") or (pad_pressed and event.button_index==JOY_BUTTON_DPAD_UP):
		selected=posmod(selected-1,maxi(1,buttons.size()))
	if (event.is_action_pressed("ui_accept") or (pad_pressed and event.button_index==JOY_BUTTON_A)) and not buttons.is_empty():
		var b=buttons[clampi(selected,0,buttons.size()-1)]
		if b.enabled:activate(b.action);get_viewport().set_input_as_handled()

func activate(action):
	var a=game.access
	if action.begins_with("tab_"):a.page=action.trim_prefix("tab_")
	elif action.begins_with("vol_"):
		var parts=action.split("_");var amount=float(parts[2])*.1
		if parts[1]=="Master":game.volume=clampf(game.volume+amount,0,1)
		else:a.mix[parts[1]]=clampf(float(a.mix[parts[1]])+amount,0,1)
		game.apply_volume();a.save_settings()
	elif action.begins_with("bind_") and action!="bind_device":a.begin_bind(action.trim_prefix("bind_"))
	match action:
		"new": game.new_journey()
		"crossing": game.start_crossing()
		"last_house": game.last_house.start(true)
		"last_house_new": game.last_house.start(false)
		"continue": game.continue_journey()
		"resume": game.mode="playing"
		"restart": game.mode="playing"; game.recover(false)
		"pack": game.mode="inventory"
		"chapters": game.open_chapters()
		"settings": game.settings_return=game.mode;game.mode="settings";a.page="sound"
		"back":game.mode=game.settings_return;a.rebind_action=""
		"menu": game.return_to_title()
		"quit": game.quit_game()
		"mute": game.muted=not game.muted; game.apply_volume(); game.write_save()
		"motion": game.reduced_motion=not game.reduced_motion; game.write_save()
		"louder": game.volume=minf(1,game.volume+.1); game.apply_volume(); game.write_save()
		"quieter": game.volume=maxf(0,game.volume-.1); game.apply_volume(); game.write_save()
		"bind_device":a.bind_device="controller" if a.bind_device=="keyboard" else "keyboard";a.notice=""
		"text_scale":a.text_scale=1.0 if a.text_scale>1.3 else a.text_scale+.2;a.save_settings()
		"crouch_toggle":a.crouch_toggle=not a.crouch_toggle;a.crouch_latched=false;a.save_settings()
		"reset_confirm":a.page="reset"
		"confirm_reset":a.reset();a.page="access"
		"preview_audio":
			game.soundscape.audit_enabled=true;game.play_sfx("cloth",-10,null,"ACTION CUE PREVIEW");game.play_sfx("warning",-14,null,"THREAT CUE PREVIEW")
		"fullscreen": DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode()==DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
	if action.begins_with("chapter_"): game.choose_chapter(int(action.trim_prefix("chapter_")))
	selected=0; hover=-1

