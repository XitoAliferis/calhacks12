extends Window

signal successful_creation

@onready var task_name_input = $VBoxContainer/LineEdit
@onready var description_input = $VBoxContainer/TextEdit
@onready var steps_container = $VBoxContainer/ScrollContainer/StepsContainer
@onready var complete_task_button = $VBoxContainer/HBoxContainer/Button
@onready var scroll = $VBoxContainer/ScrollContainer

func _ready() -> void:
	hide()
	complete_task_button.disabled = true
	connect("close_requested", Callable(self, "_on_close_requested"))
	complete_task_button.pressed.connect(_on_complete_task)

	# Connect all existing checkboxes (if any)
	_connect_all_checkboxes()

	# Detect dynamically added HBoxes (e.g., AI-generated or user-added steps)
	steps_container.child_entered_tree.connect(_on_child_added)


# --- When a new step (HBox with CheckBox) is added ---
func _on_child_added(child: Node) -> void:
	if child is HBoxContainer:
		for sub in child.get_children():
			if sub is CheckBox:
				if not sub.is_connected("toggled", Callable(self, "_on_update_subtask")):
					sub.connect("toggled", Callable(self, "_on_update_subtask"))
		# Update state right after adding
		_on_update_subtask()


# --- Connect all checkboxes currently in steps_container ---
func _connect_all_checkboxes() -> void:
	for hbox in steps_container.get_children():
		if hbox is HBoxContainer:
			for sub in hbox.get_children():
				if sub is CheckBox:
					if not sub.is_connected("toggled", Callable(self, "_on_update_subtask")):
						sub.connect("toggled", Callable(self, "_on_update_subtask"))
	_on_update_subtask()


func _on_update_subtask(_toggled: bool = false) -> void:
	var total_steps := 0
	var completed_steps := 0

	for hbox in steps_container.get_children():
		if hbox is HBoxContainer:
			for child in hbox.get_children():
				if child is CheckBox:
					total_steps += 1
					if child.button_pressed:
						completed_steps += 1

	if total_steps == 0:
		complete_task_button.text = "No Steps"
		complete_task_button.disabled = true
		return

	if completed_steps == total_steps:
		complete_task_button.text = "Complete Task 🎉"
		complete_task_button.disabled = false
	else:
		var step_word = "step" if total_steps == 1 else "steps"
		complete_task_button.text = "%d/%d %s completed" % [completed_steps, total_steps, step_word]
		complete_task_button.disabled = true



# --- Handle completion ---
func _on_complete_task() -> void:
	print("✅ Task completed:", task_name_input.text)
	emit_signal("successful_creation")
	hide()
	global.creating_task = false


func _on_close_requested() -> void:
	hide()
	global.creating_task = false
