# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from typing import List

class Exit:
	is_table_class = False

	def __init__(self, data: List[object]):
		self.data = {}
		self.data["direction"] = str(data[0])
		self.data["destination_room_id"] = str(data[1])

	def encode(self) -> List[object]:
		return [self.direction, self.destination_room_id]

	def __getattr__(self, name: str):
		return self.data.get(name)
