# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from .exit_direction import ExitDirection

class Exit:
	is_table_class = False

	def __init__(self, data):
		self.data = {}
		self.data["direction"] = ExitDirection(int(next(iter(data[0])))+1)
		self.data["examine"] = str(data[1])
		self.data["destination_room_id"] = str(data[2])

	def __getattr__(self, name):
		return self.data.get(name)
