extends Window

@onready var task_name_input = $VBoxContainer/LineEdit
@onready var description_input = $VBoxContainer/LineEdit2
@onready var steps_container = $VBoxContainer/ScrollContainer/StepsContainer
@onready var finish_button = $VBoxContainer/HBoxContainer/Button
@onready var add_new_step_button = $VBoxContainer/HBoxContainer/Button2
@onready var remove_step_button = $VBoxContainer/HBoxContainer/Button3
@onready var scroll = $VBoxContainer/ScrollContainer

func _ready() -> void:
	hide()
	remove_step_button.hide()
	connect("close_requested", Callable(self, "_on_close_requested"))
	finish_button.pressed.connect(_on_save)
	add_new_step_button.pressed.connect(_on_add_new_step)
	remove_step_button.pressed.connect(_on_remove_step)

func _on_close_requested() -> void:
	hide()

func _on_add_new_step() -> void:
	var step_count = steps_container.get_child_count() + 1
	if steps_container.get_child_count() > 0:
		remove_step_button.show()
		
	var new_step = LineEdit.new()
	new_step.placeholder_text = "Step %d" % step_count
	steps_container.add_child(new_step)

	# Wait one frame so UI updates, then scroll to bottom
	await get_tree().process_frame
	scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value


func _on_remove_step() -> void:
	if steps_container.get_child_count() == 1:
		remove_step_button.hide()
		return
	
	# Get the last step LineEdit in the container
	var last_step = steps_container.get_child(steps_container.get_child_count() - 1)
	
	# Remove and free it from memory
	steps_container.remove_child(last_step)
	last_step.queue_free()
	
	# If no steps remain, hide the remove button
	if steps_container.get_child_count() == 1:
		remove_step_button.hide()
	
	# Wait one frame so UI updates, then scroll to bottom
	await get_tree().process_frame
	scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _on_save() -> void:
	var task_name = task_name_input.text.strip_edges()
	var description = description_input.text.strip_edges()
	var steps = []

	for step_input in steps_container.get_children():
		if step_input is LineEdit:
			var text = step_input.text.strip_edges()
			if text != "":
				steps.append(text)

	print("=== New Task ===")
	print("Task Name:", task_name)
	print("Description:", description)
	print("Steps:")
	for s in steps:
		print(" -", s)

	hide()
