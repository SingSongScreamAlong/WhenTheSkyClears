extends RigidBody2D
var game
var object_id=""
var origin=Vector2.ZERO
func _ready():
	lock_rotation=true; mass=5; gravity_scale=1; linear_damp=7; can_sleep=true
	collision_layer=1; collision_mask=1
	var shape=CollisionShape2D.new(); shape.shape=RectangleShape2D.new(); shape.shape.size=Vector2(70,52); add_child(shape)
func reset_to_origin(): position=origin; linear_velocity=Vector2.ZERO; angular_velocity=0
