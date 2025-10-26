extends Node2D

var selected_furniture = global.furniture[0]

func _ready() -> void:
	$Popup/Window.successful_creation.connect(setup_task)
	$PickFurniture/Window.selected_furniture.connect(set_furniture)

func setup_task():
	$Button.disabled = true
	$Button.hide()
	$TaskMarkerButton.show()
	print("successfully created task")
	# open select furniture gui
	$PickFurniture/Window.show()

func _on_button_pressed() -> void:
	if global.creating_task: return
	$Popup/Window.show()
	global.creating_task = true

func _on_task_marker_button_mouse_entered() -> void:
	$TaskMarkerButton.position.y -= 1


func _on_task_marker_button_mouse_exited() -> void:
	$TaskMarkerButton.position.y += 1


func _on_task_marker_button_pressed() -> void:
	# open task view gui
	if $PickFurniture/Window.visible: return
	$TaskMarkerButton.hide()
	var this_furniture = load(selected_furniture)
	add_child(this_furniture.instantiate())
	global.finished_tasks+=1
	global.finished_task.emit()

func set_furniture(index):
	selected_furniture = global.furniture[index]
