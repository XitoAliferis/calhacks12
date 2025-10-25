extends Node2D

func _on_button_pressed() -> void:
	$Button.disabled = true
	$Button.visible = false
	$TaskMarkerButton.visible = true
	# open the task creation gui


func _on_task_marker_button_mouse_entered() -> void:
	$TaskMarkerButton.position.y -= 1


func _on_task_marker_button_mouse_exited() -> void:
	$TaskMarkerButton.position.y += 1


func _on_task_marker_button_pressed() -> void:
	# open task view gui
	pass # Replace with function body.
