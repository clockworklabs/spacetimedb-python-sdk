# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from __future__ import annotations
from typing import List, Iterator, Callable

from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient, Identity, Address
from spacetimedb_sdk.spacetimedb_client import ReducerEvent

class User:
	is_table_class = True

	primary_key = "identity"

	@classmethod
	def register_row_update(cls, callback: Callable[[str,User,User,ReducerEvent], None]):
		SpacetimeDBClient.instance._register_row_update("User",callback)

	@classmethod
	def iter(cls) -> Iterator[User]:
		return SpacetimeDBClient.instance._get_table_cache("User").values()

	@classmethod
	def filter_by_identity(cls, identity) -> User:
		return next(iter([column_value for column_value in SpacetimeDBClient.instance._get_table_cache("User").values() if column_value.identity == identity]), None)

	@classmethod
	def filter_by_online(cls, online) -> List[User]:
		return [column_value for column_value in SpacetimeDBClient.instance._get_table_cache("User").values() if column_value.online == online]

	def __init__(self, data: List[object]):
		self.data = {}
		self.data["identity"] = Identity.from_string(data[0][0])
		self.data["name"] = str(data[1]['0']) if '0' in data[1] else None
		self.data["online"] = bool(data[2])

	def encode(self) -> List[object]:
		return [self.identity, {'0': [self.name]}, self.online]

	def __getattr__(self, name: str):
		return self.data.get(name)
