extends SceneTree

# Run with the project engine:
# --headless --path game --script res://tools/audit_terrain_polygons.gd
# This duplicates only world.gd's current terrain polygon construction. It
# neither loads game state nor modifies levels, scripts, or player saves.
var tests=0
var failures=[]
var counts={}
var max_records=48
var summary=[]
var current_ground=[]

func _initialize():
	var started=Time.get_ticks_msec()
	var args=OS.get_cmdline_user_args()
	var mode="old12" if "--old12" in args else "current"
	var step=19.3 if mode=="old12" and not "--dense" in args else 2.3
	var levels=[]
	for chapter in range(1,6):
		var data=JSON.parse_string(FileAccess.get_file_as_string("res://levels/0%d.json"%chapter))
		current_ground=data.ground
		levels.append(data)
		var before=tests
		var before_fail=total_failures()
		var camera_x=.137
		while camera_x<float(data.width)+1:
			for index in range(data.ground.size()): audit_segment(data.ground[index],camera_x,chapter,index,mode)
			camera_x+=step
		# Exact contour-knot clipping and 32-bit rounding thresholds also matter.
		for index in range(data.ground.size()):
			var p=data.ground[index]
			for knot in p.get("profile",[]):
				var wx=float(p.x)+float(knot[0])
				for delta in [-1.001,-.1,-.0001,0,.0001,.1,1.001]:
					for clip in [-960,960]: audit_segment(p,wx+clip+delta,chapter,index,mode)
		var row={"chapter":chapter,"polygon_checks":tests-before,"failed_polygons":total_failures()-before_fail}
		summary.append(row)
		print("TERRAIN_AUDIT_CHAPTER ",JSON.stringify(row))
	var report={"mode":mode,"camera_step_pixels":step,"all_passed":total_failures()==0,"checks":tests,"failed_polygons":total_failures(),"failure_counts":counts,"first_failures":failures,"chapters":summary,"elapsed_ms":Time.get_ticks_msec()-started,"method":"Offline Geometry2D.triangulate_polygon audit of current world.gd earth, 7 soil bands and turf over 5 actual JSON chapters; dense camera samples plus exact profile-knot clipping probes. No game state changes."}
	var folder="res://evidence/v040"
	DirAccess.make_dir_recursive_absolute(folder)
	var path=folder.path_join("terrain_polygon_audit_"+mode+".json")
	var file=FileAccess.open(path,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")); file.close()
	print("TERRAIN_AUDIT_RESULT ",JSON.stringify(report))
	quit(0 if total_failures()==0 else 1)

func total_failures():
	var total=0
	for count in counts.values(): total+=int(count)
	return total

func segment_y(p,world_x):
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

func exposed_bank(edge_x,direction):
	var beyond=edge_x+direction*2.0
	for other in current_ground:
		if beyond>=float(other.x) and beyond<=float(other.x)+float(other.w): return false
	return true

func audit_segment(p,camera_x,chapter,index,mode):
	var x=float(p.x)
	var w=float(p.w)
	var left=camera_x-900
	if x+w<left or x>left+1800: return
	var top=PackedVector2Array()
	var start=maxf(x,left-60)
	var finish=minf(x+w,left+1860)
	var samples=[start,finish]
	if mode=="old12":
		for i in range(int(ceil((finish-start)/12.0))): samples.append(minf(finish,start+(i+1)*12))
	for knot in p.get("profile",[]):
		var xx=x+float(knot[0])
		if xx>start and xx<finish: samples.append(xx)
	samples.sort()
	var epsilon=.01 if mode=="old12" else 1.0
	for xx in samples:
		if top.is_empty() or absf(top[-1].x-xx)>epsilon: top.append(Vector2(xx,segment_y(p,xx)))
	var polygon=top.duplicate()
	var right_y=segment_y(p,finish)
	var left_y=segment_y(p,start)
	var right_exposed=finish>=x+w-1 and (mode=="old12" or exposed_bank(x+w,1))
	var left_exposed=start<=x+1 and (mode=="old12" or exposed_bank(x,-1))
	for depth in range(1,17):
		var notch=sin(depth*8.37+x)*11+sin(depth*3.17)*7
		polygon.append(Vector2(finish+notch*(1.0 if right_exposed else 0.0),right_y+depth*34))
	polygon.append(Vector2(start,left_y+570))
	for depth in range(16,0,-1):
		var notch=sin(depth*4.57+x)*12+cos(depth*2.4)*8
		polygon.append(Vector2(start+notch*(1.0 if left_exposed else 0.0),left_y+depth*34))
	check(polygon,"earth",camera_x,chapter,index,top)
	for layer in range(7):
		var band=PackedVector2Array()
		for pt in top: band.append(pt+Vector2(0,18+layer*36+sin(pt.x*.018+layer*3)*5))
		for i in range(top.size()-1,-1,-1):
			var pt=top[i]
			band.append(pt+Vector2(0,60+layer*40+sin(pt.x*.014+layer)*7))
		check(band,"soil_"+str(layer),camera_x,chapter,index,top)
	var turf=PackedVector2Array()
	for pt in top: turf.append(pt+Vector2(0,2))
	for i in range(top.size()-1,-1,-1):
		var pt=top[i]
		# Current renderer guarantees 2 pixels of positive thickness. The
		# historical --old12 comparison preserves the zero-minimum turf too.
		var base=2.0 if mode=="old12" else 4.0
		turf.append(pt+Vector2(0,base+noise_at(pt.x)*2))
	check(turf,"turf",camera_x,chapter,index,top)

func check(polygon,label,camera_x,chapter,index,top):
	tests+=1
	if not Geometry2D.triangulate_polygon(polygon).is_empty(): return
	var key="chapter_%d_%s"%[chapter,label]
	counts[key]=int(counts.get(key,0))+1
	if failures.size()>=max_records: return
	var local=PackedVector2Array()
	for pt in polygon: local.append(pt-Vector2(camera_x,0))
	var record={"chapter":chapter,"segment_index":index,"camera_x":camera_x,"kind":label,"top_points":top.size(),"points":[],"translation_to_camera_fixes":not Geometry2D.triangulate_polygon(local).is_empty()}
	for pt in polygon: record.points.append([pt.x,pt.y])
	failures.append(record)
