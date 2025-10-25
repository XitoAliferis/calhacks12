extends Node2D

@onready var area = $Area2D
@onready var window = $Window

func _ready() -> void:
	area.connect("input_event", Callable(self, "_on_area_input_event"))

func _on_area_input_event(viewport, event, shape_idx):
	if event is InputEventMouseButton and event.pressed:
		window.visible = not window.visible
		
