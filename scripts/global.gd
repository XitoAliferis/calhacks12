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
var room_types = [
	"res://scenes/room_layout_1.tscn",
	"res://scenes/room_layout_2.tscn",
	"res://scenes/room_layout_3.tscn"
	
]
