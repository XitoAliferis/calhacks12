extends Node2D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	$Button.disabled = true
	global.finished_task.connect(unlock)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_button_pressed() -> void:
	pass


func _on_button_mouse_entered() -> void:
	$Button.position.y -= 1


func _on_button_mouse_exited() -> void:
	$Button.position.y += 1

func unlock():
	$Button.disabled = false;
	$Button.set_texture(load("res://assets/buttons/unlock.png"))
