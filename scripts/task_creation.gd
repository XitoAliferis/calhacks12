extends Window

@onready var task_name_input = $VBoxContainer/LineEdit
@onready var description_input = $VBoxContainer/LineEdit2
@onready var step_inputs = [
	$VBoxContainer/VBoxContainer/LineEdit3,
	$VBoxContainer/VBoxContainer/LineEdit4,
	$VBoxContainer/VBoxContainer/LineEdit5,
]
@onready var finish_button = $VBoxContainer/HBoxContainer/Button
@onready var add_new_step_button = $VBoxContainer/HBoxContainer/Button2

func _ready() -> void:
	hide()
	connect("close_requested", Callable(self, "_on_close_requested"))
	finish_button.pressed.connect(_on_save)

func _on_close_requested() -> void:
	hide()

func _on_save() -> void:
	var task_name = task_name_input.text.strip_edges()
	var description = description_input.text.strip_edges()
	var steps = []

	for step_input in step_inputs:
		var text = step_input.text.strip_edges()
		if text != "":
			steps.append(text)

	# For now, just print the results (replace with your logic later)
	print("=== New Task ===")
	print("Task Name:", task_name)
	print("Description:", description)
	print("Steps:")
	for s in steps:
		print(" -", s)

	# Optionally hide the window after saving
	hide()
