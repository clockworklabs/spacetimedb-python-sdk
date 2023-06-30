# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from typing import List, Callable

from spacetimedb_python_sdk.spacetimedb_client import SpacetimeDBClient


def create_player(name: str):
	name = name
	SpacetimeDBClient.instance._reducer_call("create_player", name)

def register_on_create_player(callback: Callable[[bytes, str, str, str], None]):
	if not _check_callback_signature(callback):
		raise ValueError("Callback signature does not match expected arguments")

	SpacetimeDBClient.instance._register_reducer("create_player", callback)

def _decode_args(data):
	return [str(data[0])]

def _check_callback_signature(callback: Callable) -> bool:
	expected_arguments = [bytes, str, str, str]
	callback_arguments = callback.__annotations__.values()

	return list(callback_arguments) == expected_arguments
