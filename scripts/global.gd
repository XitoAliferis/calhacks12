extends Node

signal finished_task
var finished_tasks = 10
var open_furniture_slots = 18
var creating_task = false
var furniture = [
	"res://scenes/furniture/1.tscn",
	"res://scenes/furniture/2.tscn",
	"res://scenes/furniture/3.tscn",
	"res://scenes/furniture/4.tscn",
	"res://scenes/furniture/5.tscn",
	"res://scenes/furniture/6.tscn",
	"res://scenes/furniture/7.tscn",
	"res://scenes/furniture/8.tscn",
	"res://scenes/furniture/9.tscn",
	"res://scenes/furniture/10.tscn"
]
var saved_tasks := {}
var current_furniture: String = ""

func save_task(id: String, name: String, description: String, steps: Array) -> void:
	saved_tasks[id] = {
		"name": name,
		"description": description,
		"steps": steps
	}
	print(saved_tasks[id])
	print("wowowowowo")
	
func get_task(id: String) -> Dictionary:
	if saved_tasks.has(id):
		return saved_tasks[id]
	return {}
	
var room_types = [
	"res://scenes/room_layout_1.tscn",
	"res://scenes/room_layout_2.tscn",
	"res://scenes/room_layout_3.tscn"
	
]
