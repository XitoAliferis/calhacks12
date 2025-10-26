extends Node2D

@onready var textbox = $Textbox/RichTextLabel
@onready var text_figure = $Textbox
@onready var http_request = $HTTPRequest

const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
const OPENROUTER_KEY = "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"


func _ready() -> void:
	http_request.request_completed.connect(_on_request_completed)
	text_figure.visible = false

	if global.has_signal("saved_tasks_changed"):
		global.saved_tasks_changed.connect(_make_agent_comment)

	

func _make_agent_comment() -> void:
	if not global.saved_tasks or global.saved_tasks.size() == 0:
		print("⚠️ No tasks to analyze.")
		return

	# 🧠 Safely get the most recently added task
	var last_task_key: String = ""
	var keys = global.saved_tasks.keys()
	if keys.size() > 0:
		last_task_key = keys[keys.size() - 1]
	else:
		print("⚠️ No keys in saved_tasks.")
		return

	var last_task = global.saved_tasks.get(last_task_key, null)
	if last_task == null or typeof(last_task) != TYPE_DICTIONARY:
		print("⚠️ Invalid last_task data:", last_task)
		return

	print("🧩 Sending latest task to OpenRouter:", last_task)

	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer %s" % OPENROUTER_KEY
	]

	var body = {
		"model": "openai/gpt-4o-mini",
		"messages": [
			{
				"role": "system",
				"content": "You are a friendly assistant who leaves short, funny, or thoughtful comments on new tasks, note your have to make small, short, one-line quick comments."
			},
			{
				"role": "user",
				"content": "Here are all saved tasks:\n%s\n\nPlease make a short comment about the newest one: %s" % [
					JSON.stringify(global.saved_tasks),
					last_task.get("name", "Unnamed Task")
				]
			}
		]
	}

	http_request.request(
		OPENROUTER_URL,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
	)


func _on_request_completed(result, response_code, headers, body):
	if response_code != 200:
		print("❌ OpenRouter API error:", response_code)
		print(body.get_string_from_utf8())
		textbox.text = "Error: Could not get comment."
		return

	var json = JSON.parse_string(body.get_string_from_utf8())
	if json == null or not json.has("choices") or json.choices.is_empty():
		print("⚠️ Unexpected API response:", json)
		textbox.text = "No response from AI."
		return

	var message = json.choices[0].message.content.strip_edges()
	print("💬 AI comment:", message)
	textbox.text = message
	text_figure.visible = true

func _hide_textbox() :
		text_figure.visible = false
