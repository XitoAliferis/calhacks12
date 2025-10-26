extends Node2D

@export var required_tasks = 10
@export var room_type = 0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	$Button.disabled = true
	global.finished_task.connect(unlock)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_button_pressed() -> void:
	var room = load(global.room_types[room_type]).instantiate()
	room.global_position = global_position
	get_parent().add_child(room)
	queue_free()


func _on_button_mouse_entered() -> void:
	$Button.position.y -= 1


func _on_button_mouse_exited() -> void:
	$Button.position.y += 1

func unlock():
	if global.finished_tasks >= required_tasks:
		$Button.disabled = false
		$Button.icon = load("res://assets/buttons/unlock.png")
