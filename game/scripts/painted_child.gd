extends RefCounted
# Retained, authored atlas paint is deformed as continuous strips. No new
# bitmap, generated noise, asset dependency or baked animation is introduced.
static func quad(c,points,uv,texture,tint):
	# Folded arms can turn a strip quad concave. Submit the two UV triangles
	# explicitly; reject only zero-area triangles at an exactly folded row.
	for indices in [[0,1,2],[0,2,3]]:
		var a=points[indices[0]];var b=points[indices[1]];var end=points[indices[2]]
		if absf((b-a).cross(end-a))<.001:continue
		c.draw_polygon(PackedVector2Array([a,b,end]),PackedColorArray([tint]),PackedVector2Array([uv[indices[0]],uv[indices[1]],uv[indices[2]]]),texture)

static func limb(c,a,b,end,width_a,width_b,width_end,material,depth):
	var sleeve=material=="sleeve"
	var rows=10
	var previous=[]
	var previous_uv=[]
	var tint=Color(.78,.82,.76) if sleeve else Color(.67,.70,.60)
	if c.is_girl:
		tint=Color(.65,.76,.77) if sleeve else Color(.36,.43,.43)
	var warm=c.game.last_house.warm_light_at(c.position)
	tint=tint.lerp(Color(tint.r*1.13,tint.g*1.04,tint.b*.88),warm*.5)
	tint=tint.darkened(c.game.wetness*.10)*(depth if depth<1 else 1.0)
	tint.a=1.0
	for i in range(rows+1):
		var u=float(i)/rows
		var split=(b-a).length()/maxf(.01,(b-a).length()+(end-b).length())
		var first=u<=split
		var t=clampf(u/maxf(.01,split),0,1) if first else clampf((u-split)/maxf(.01,1-split),0,1)
		var center=a.lerp(b,t) if first else b.lerp(end,t)
		var tangent=(b-a).normalized() if first else (end-b).normalized()
		# Blend the elbow normal through the middle rows, so the painted fold
		# closes around a bent joint instead of revealing separate cylinders.
		if absf(u-split)<.17:
			tangent=(b-a).normalized().lerp((end-b).normalized(),clampf((u-split+.17)/.34,0,1)).normalized()
		var across=Vector2(-tangent.y,tangent.x)
		var width=lerpf(width_a,width_b,t) if first else lerpf(width_b,width_end,t)
		var points=[center+across*width*1.18,center-across*width*1.18]
		var source_y=lerpf(36,555,u) if sleeve else lerpf(616,1225,u)
		var source_x=1080.0-24*sin(u*PI) if sleeve else 633.0-8*sin(u*PI)
		var source_width=103.0 if sleeve else 91.0
		var uv=[Vector2(source_x-source_width,source_y)/Vector2(c.head_atlas.get_size()),Vector2(source_x+source_width,source_y)/Vector2(c.head_atlas.get_size())]
		if i>0:quad(c,[previous[0],previous[1],points[1],points[0]],[previous_uv[0],previous_uv[1],uv[1],uv[0]],c.head_atlas,tint)
		previous=points;previous_uv=uv

static func coat(c,shoulder,hip,hem,wind,face,skirt_only=false):
	var rows=8
	var start=hip+Vector2(0,-3) if skirt_only else shoulder+Vector2(0,-5)
	var bottom=Vector2(hip.x*.25+wind,hem+1)
	var tint=Color(.69,.77,.75) if c.is_girl else Color(.80,.82,.74)
	var warm=c.game.last_house.warm_light_at(c.position)
	tint=tint.lerp(Color(tint.r*1.12,tint.g*1.04,tint.b*.88),warm*.5).darkened(c.game.wetness*.08)
	var previous=[];var previous_uv=[]
	for i in range(rows+1):
		var u=float(i)/rows
		var center=start.lerp(bottom,u)
		if not skirt_only:
			var pelvis_u=clampf((center.y-shoulder.y)/maxf(1,hip.y-shoulder.y),0,1)
			center.x=lerpf(shoulder.x,hip.x,pelvis_u)+wind*pow(u,3)*.65
		var width=lerpf(12.2,18.5,u) if skirt_only else (lerpf(16,13,u/.65) if u<.65 else lerpf(13,18.5,(u-.65)/.35))
		var points=[center+Vector2(-width,0),center+Vector2(width,0)]
		var source_y=lerpf(340,575,u) if skirt_only else lerpf(8,575,u)
		var uv=[Vector2(510 if face>0 else 830,source_y)/Vector2(c.head_atlas.get_size()),Vector2(830 if face>0 else 510,source_y)/Vector2(c.head_atlas.get_size())]
		if i>0:quad(c,[previous[0],previous[1],points[1],points[0]],[previous_uv[0],previous_uv[1],uv[1],uv[0]],c.head_atlas,tint)
		previous=points;previous_uv=uv
	if c.is_girl and skirt_only:
		# A quiet waist seam joins the long coat and skirt; the original blue
		# ribbon and profile remain the girl's identity cues.
		c.draw_line(hip+Vector2(-8,-1),hip+Vector2(8,-1),Color(.20,.29,.29,.65),1.3,true)

static func boot(c,ankle,face,depth=1.0):
	c.draw_set_transform(ankle,0,Vector2(face,1))
	var tint=Color(.68,.73,.68)*depth;tint.a=1
	c.draw_texture_rect_region(c.head_atlas,Rect2(-6,-13,24,15.5),Rect2(837,857,410,333),tint)
	c.draw_set_transform(Vector2.ZERO)

static func hand(c,at,elbow,depth=1.0):
	var direction=(at-elbow).normalized()
	c.draw_set_transform(at,direction.angle()-PI*.5,Vector2(1,1))
	var tint=Color(.64,.66,.56)*depth;tint.a=1
	c.draw_texture_rect_region(c.head_atlas,Rect2(-3.2,-2,7.6,11.5),Rect2(151,928,175,275),tint)
	c.draw_set_transform(Vector2.ZERO)
