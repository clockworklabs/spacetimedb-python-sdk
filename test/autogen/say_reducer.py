# THIS FILE IS AUTOMATICALLY GENERATED BY SPACETIMEDB. EDITS TO THIS FILE
# WILL NOT BE SAVED. MODIFY TABLES IN RUST INSTEAD.

from network_manager import NetworkManager

def say(sourceSpawnableEntityId, chatText):
	NetworkManager.instance.reducer_call("say", sourceSpawnableEntityId, chatText)