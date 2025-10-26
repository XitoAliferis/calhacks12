extends Window

signal successful_creation

@onready var task_name_input = $VBoxContainer/LineEdit
@onready var description_input = $VBoxContainer/TextEdit
@onready var steps_container = $VBoxContainer/ScrollContainer/StepsContainer
@onready var finish_button = $VBoxContainer/HBoxContainer/Button
@onready var add_new_step_button = $VBoxContainer/HBoxContainer/Button2
@onready var remove_step_button = $VBoxContainer/HBoxContainer/Button3
@onready var ai_button = $VBoxContainer/Button2
@onready var scroll = $VBoxContainer/ScrollContainer
@onready var http_request = $HTTPRequest  # reference to the HTTPRequest node

const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
const OPENROUTER_KEY = "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"

var is_loading := false
var current_furniture_id := ""

func _ready() -> void:
	hide()
	ai_button.disabled = true
	finish_button.disabled = true
	remove_step_button.hide()
	connect("close_requested", Callable(self, "_on_close_requested"))
	finish_button.pressed.connect(_on_save)
	add_new_step_button.pressed.connect(_on_add_new_step)
	remove_step_button.pressed.connect(_on_remove_step)
	ai_button.pressed.connect(_on_ai_pressed)
	http_request.request_completed.connect(_on_request_completed)
	description_input.text_changed.connect(_on_edit_description)
	# Hide all checkboxes initially
	for child in steps_container.get_children():
		if child is HBoxContainer:
			for subchild in child.get_children():
				if subchild is LineEdit:
					subchild.text_changed.connect(_on_edit_steps)
				elif subchild is CheckBox:
					subchild.visible = false
	
func _on_close_requested() -> void:
	hide()
	global.creating_task = false
	
func _on_edit_description() -> void:
	if OPENROUTER_KEY.length() == 0:
		return
	if description_input.text.length() == 0:
		ai_button.disabled = true
	else:
		ai_button.disabled = false
		
func _on_edit_steps(new_text := "") -> void:
	var has_text := false

	for child in steps_container.get_children():
		if child is LineEdit:
			if child.text.strip_edges() != "":
				has_text = true
				break
		elif child is HBoxContainer:
			for subchild in child.get_children():
				if subchild is LineEdit and subchild.text.strip_edges() != "":
					has_text = true
					break
			if has_text:
				break

	finish_button.disabled = not has_text

	
# --- ADD STEP ---

func _on_add_new_step() -> void:
	var step_count = steps_container.get_child_count() + 1
	if steps_container.get_child_count() > 0:
		remove_step_button.show()

	var new_step = LineEdit.new()
	new_step.placeholder_text = "Step %d" % step_count
	steps_container.add_child(new_step)

	await get_tree().process_frame
	scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

# --- REMOVE STEP ---
func _on_remove_step() -> void:
	if steps_container.get_child_count() == 1:
		remove_step_button.hide()
		return

	var last_step = steps_container.get_child(steps_container.get_child_count() - 1)
	steps_container.remove_child(last_step)
	last_step.queue_free()

	if steps_container.get_child_count() == 1:
		remove_step_button.hide()

	await get_tree().process_frame
	scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _on_save() -> void:
	var task_name = task_name_input.text.strip_edges()
	var description = description_input.text.strip_edges()
	var steps: Array = []

	for child in steps_container.get_children():
		# Case 1: Direct LineEdit
		if child is LineEdit:
			var text = child.text.strip_edges()
			if text != "":
				steps.append(text)

		# Case 2: HBoxContainer (with LineEdit inside)
		elif child is HBoxContainer:
			for subchild in child.get_children():
				if subchild is LineEdit:
					var text = subchild.text.strip_edges()
					if text != "":
						steps.append({ "text": text, "checked": false })

	hide()
	current_furniture_id = global.current_furniture
	global.save_task(current_furniture_id, task_name, description, steps)
	global.creating_task = false
	successful_creation.emit()


# --- AI BUTTON ---
func _on_ai_pressed() -> void:
	var description_text = description_input.text.strip_edges()
	if description_text.length() == 0:
		return
	ai_button.text = "Generating steps..."
	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer %s" % OPENROUTER_KEY,
		"HTTP-Referer: https://your-site-url.com",
		"X-Title: Godot Task App"
	]
	# Construct the message prompt dynamically
	var body = {
		"model": "anthropic/claude-3.5-haiku",  # ⚡ super fast model
		"messages": [
			{
				"role": "user",
				"content": "respond in this format (4 steps max but do only as many as necessary, just tell me the steps, don't overthink, barely think, the steps should be short bullets). do not show anything thinking, just the answer:\n\n" +
				"your message should look like:\n" +
				"\"step 1: describe step\nstep 2: describe step\nstep 3: describe step\nstep x: ...\"\n\n" +
				"the description we want you to step:\n" + description_text
			}
		]
	}

	http_request.request(
		OPENROUTER_URL,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
	)
	
func _on_request_completed(result_code, response_code, headers, body):
	if response_code != 200:
		print("API Error:", response_code)
		print(body.get_string_from_utf8())
		return

	var json = JSON.parse_string(body.get_string_from_utf8())
	if json == null or not json.has("choices") or json.choices.is_empty():
		print("Unexpected response:", json)
		return

	var message = json.choices[0].message.content
	var cut_index = message.rfind("</think>")
	if cut_index != -1:
		message = message.substr(cut_index + "</think>".length()).strip_edges()


	# --- Parse each "step X: ..." line ---
	var step_lines = message.split("\n", false)
	var steps: Array = []

	for line in step_lines:
		line = line.strip_edges()
		if line == "":
			continue
		var regex = RegEx.new()
		regex.compile("(?i)^step\\s*\\d+:\\s*(.*)")
		var match = regex.search(line)
		if match and match.get_string(1).strip_edges() != "":
			steps.append(match.get_string(1).strip_edges())

	# --- Clear all old steps ---
	for child in steps_container.get_children():
		child.queue_free()

	# --- Add the AI-generated steps ---
	for i in range(steps.size()):
		var hbox := HBoxContainer.new()
		var checkbox := CheckBox.new()
		var step_input := LineEdit.new()

		checkbox.focus_mode = Control.FOCUS_NONE
		checkbox.visible = false  # <-- will later be false until AI pressed
		step_input.placeholder_text = "Step %d" % (i + 1)
		step_input.custom_minimum_size = Vector2(545.0,0)
		step_input.text = steps[i]

		hbox.add_child(checkbox)
		hbox.add_child(step_input)
		steps_container.add_child(hbox)

	# --- Add one new blank step at the end ---
	var next_index := steps.size() + 1
	var new_empty_step := LineEdit.new()
	new_empty_step.placeholder_text = "Step %d" % next_index
	steps_container.add_child(new_empty_step)

	remove_step_button.show()
	await get_tree().process_frame
	scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value
	ai_button.text = "Generate Steps with AI 🪄"
	finish_button.disabled = false
	
