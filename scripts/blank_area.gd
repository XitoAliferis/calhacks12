extends Node2D


func _on_button_pressed() -> void:
	if global.creating_task: return
	$Button.disabled = true
	$Button.hide()
	$TaskMarkerButton.show()
	$Popup/Window.show()
	global.creating_task = true


func _on_task_marker_button_mouse_entered() -> void:
	$TaskMarkerButton.position.y -= 1


func _on_task_marker_button_mouse_exited() -> void:
	$TaskMarkerButton.position.y += 1


func _on_task_marker_button_pressed() -> void:
	# open task view gui
	pass # Replace with function body.
