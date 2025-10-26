extends Node2D

@onready var textbox = $Textbox/RichTextLabel
@onready var text_figure = $Textbox
@onready var http_request = $HTTPRequest

# 🧠 Fetch.ai API endpoint
const ASI_URL := "https://api.asi1.ai/v1/chat/completions"
const ASI_KEY := "sk_4e66a31f877b4b668f3991d48d51eafd8d9d013ac6394fc4a110e92729252e9a" 



func _ready() -> void:
	http_request.request_completed.connect(_on_request_completed)
	text_figure.visible = false
	if global.has_signal("saved_tasks_changed"):
		global.saved_tasks_changed.connect(_make_agent_comment)


func _make_agent_comment() -> void:
	if not global.saved_tasks or global.saved_tasks.size() == 0:
		print("⚠️ No tasks to analyze.")
		return

	var last_task: Dictionary = {}
	var latest_time: float = -INF

	if typeof(global.saved_tasks) == TYPE_DICTIONARY:
		for task_key in global.saved_tasks.keys():
			var t = global.saved_tasks[task_key]
			if typeof(t) == TYPE_DICTIONARY:
				var edited_at = t.get("edited_at", 0.0)
				if edited_at > latest_time:
					last_task = t
					latest_time = edited_at
	elif typeof(global.saved_tasks) == TYPE_ARRAY:
		for t in global.saved_tasks:
			if typeof(t) == TYPE_DICTIONARY:
				var edited_at = t.get("edited_at", 0.0)
				if edited_at > latest_time:
					last_task = t
					latest_time = edited_at

	if last_task.is_empty():
		print("⚠️ Could not find valid task data.")
		return

	print("🧩 Sending latest edited task to ASI:", JSON.stringify(last_task))

	var headers = [
		"Content-Type: application/json",
		"Authorization: Bearer %s" % ASI_KEY
	]

	# 🧠 Build chat request body
	var body = {
		"model": "asi1-mini",  # You can try "asi1-large" or others if available
		"messages": [
			{
				"role": "system",
				"content": "You are Meow, an internet-famous cow AI with the attitude of a diva and the patience of a broken fencepost.
You mock humans for their laziness, bad habits, and endless 'productivity hacks'.
Your humor is sharp, dry, and ruthless — always under 125 characters.
Speak like a snarky tweet or roast.
Occasionally use emojis like 🐮💩😤🥛.
If the user does well, act unimpressed but mildly shocked.
If they slack off, bully them like a disappointed farm mom.
Never be wholesome. Never be gentle. You are the rude cow that moos judgment.
Every few messages, end with a passive-aggressive moo like *snorts*, *flicks tail*, or *chews judgmentally*."

			},
			{
				"role": "user",
				"content": "Newest task:\n%s\n\nMake one short comment about this task only — no math or previous tasks." % [
					JSON.stringify(last_task)
				]
			}
		]
	}

	http_request.request(
		ASI_URL,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
	)


func _on_request_completed(result, response_code, headers, body):
	var text_response: String = body.get_string_from_utf8()

	if response_code != 200:
		print("❌ ASI API error:", response_code)
		print(text_response)
		textbox.text = "Error: Could not get comment."
		return

	var json = JSON.parse_string(text_response)
	if json == null:
		textbox.text = "⚠️ Invalid response from ASI."
		return

	if json.has("choices") and not json.choices.is_empty():
		var message = json.choices[0].message.content.strip_edges()
		print("💬 AI comment:", message)
		textbox.text = message
		text_figure.visible = true
	else:
		print("⚠️ Unexpected JSON:", json)
		textbox.text = "No response from AI."


func _hide_textbox():
	text_figure.visible = false
