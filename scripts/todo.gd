extends Window

signal task_complete

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
	# Recalculate based on current state
	_on_update_subtask(true)



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
	task_complete.emit()
	hide()


func _on_close_requested() -> void:
	hide()

func load_task_from_global() -> void:
	if not global.saved_tasks.has(global.current_furniture):
		print("⚠️ No task found for:", global.current_furniture)
		return

	var task_data = global.saved_tasks[global.current_furniture]
	print("🪑 Loading task:", task_data)

	task_name_input.text = task_data.get("name", "")
	description_input.text = task_data.get("description", "")

	# --- Clear any existing steps first ---
	for child in steps_container.get_children():
		steps_container.remove_child(child)
		child.free()

	# --- Recreate steps from saved data ---
	var steps = task_data.get("steps", [])
	for i in range(steps.size()):
		var hbox := HBoxContainer.new()
		var checkbox := CheckBox.new()
		var step_input := LineEdit.new()

		step_input.placeholder_text = "Step %d" % (i + 1)
		step_input.text = steps[i]
		step_input.custom_minimum_size = Vector2(545, 0)

		hbox.add_child(checkbox)
		hbox.add_child(step_input)
		steps_container.add_child(hbox)

		# Always connect once
		checkbox.connect("toggled", Callable(self, "_on_update_subtask"))

	# --- Update button status properly ---
	_on_update_subtask(true)
