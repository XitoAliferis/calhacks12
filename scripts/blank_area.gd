extends Node2D

var selected_furniture = global.furniture[0]
var id: String = "" 

func _ready() -> void:
	# --- create persistent id based on position ---
	id = "furniture_%d_%d" % [int(global_position.x), int(global_position.y)]
	print("🪑 Initialized blank area:", id)

	$Popup/Window.successful_creation.connect(setup_task)
	$PickFurniture/Window.selected_furniture.connect(set_furniture)
	$TodoList/Window.task_complete.connect(finish_task)

	# --- check if this area already has a task/furniture ---
	if global.saved_tasks.has(id):
		print("🔁 Task already exists for:", id)
		$Button.hide()
		$TaskMarkerButton.show()
	else:
		$TaskMarkerButton.hide()

func setup_task():
	$Button.disabled = true
	$Button.hide()
	$TaskMarkerButton.show()
	print("✅ successfully created task for:", id)
	# open select furniture gui
	$PickFurniture/Window.show()

func _on_button_pressed() -> void:
	if global.creating_task: 
		return
	$Popup/Window.show()
	global.current_furniture = id
	global.creating_task = true

func _on_task_marker_button_mouse_entered() -> void:
	$TaskMarkerButton.position.y -= 1

func _on_task_marker_button_mouse_exited() -> void:
	$TaskMarkerButton.position.y += 1

func _on_task_marker_button_pressed() -> void:
	# open task view gui
	if $PickFurniture/Window.visible: return
	if $TodoList/Window.visible: $TodoList/Window.visible = false
	else: $TodoList/Window.visible = true

func set_furniture(index):
	selected_furniture = global.furniture[index]

func finish_task():
	$TaskMarkerButton.hide()
	var this_furniture = load(selected_furniture)
	add_child(this_furniture.instantiate())
	global.finished_tasks+=1
	global.finished_task.emit()
