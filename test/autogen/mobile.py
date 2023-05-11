# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from client_cache import ClientCache

class Mobile:
	is_table_class = True

	@classmethod
	def iter(cls):
		return ClientCache.instance.get_table_cache("Mobile").values()

	@classmethod
	def filter_by_spawnable_entity_id(cls, spawnable_entity_id):
		return next(iter([column_value for column_value in ClientCache.instance.get_table_cache("Mobile").values() if column_value.spawnable_entity_id == spawnable_entity_id]), None)

	@classmethod
	def filter_by_name(cls, name):
		return [column_value for column_value in ClientCache.instance.get_table_cache("Mobile").values() if column_value.name == name]

	@classmethod
	def filter_by_description(cls, description):
		return [column_value for column_value in ClientCache.instance.get_table_cache("Mobile").values() if column_value.description == description]

	def __init__(self, data):
		self.data = {}
		self.data["spawnable_entity_id"] = int(data[0])
		self.data["name"] = str(data[1])
		self.data["description"] = str(data[2])

	def __getattr__(self, name):
		return self.data.get(name)
