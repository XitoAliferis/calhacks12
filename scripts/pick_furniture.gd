extends Window

signal selected_furniture
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var i = 1
	for f in global.furniture:
		var hbox = HBoxContainer.new()
		$VBoxContainer.add_child(hbox)
		var furniture = load(f).instantiate()
		furniture.scale.x = 2
		furniture.scale.y  = 2
		hbox.add_child(furniture)
		var btn = Button.new()
		btn.set_text("            ")
		i += 1
		hbox.add_child(btn)
		btn.pressed.connect(set_furniture.bind(btn))
	hide()

func set_furniture(this:Button):
	selected_furniture.emit(int(this.get_text()) - 1)
	hide()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_close_requested() -> void:
	hide()
