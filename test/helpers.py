from network_manager import NetworkManager

from autogen.mobile import Mobile
from autogen.player import Player
from autogen.location import Location
from autogen.room import Room

def get_name(spawnable_entity_id) -> str:
    mobile = Mobile.filter_by_spawnable_entity_id(spawnable_entity_id)
    return mobile.name if mobile else "Unknown"

def get_local_player_entity_id() -> int:
    local_identity = NetworkManager.instance.identity
    player = Player.filter_by_identity(local_identity)
    return player.spawnable_entity_id if player else None

def get_local_player_location() -> str:
    local_player_id = get_local_player_entity_id()
    if(local_player_id):
        location = Location.filter_by_spawnable_entity_id(local_player_id)
        return location.room_id if location else None
    
def get_local_player_room() -> Room:
    return Room.filter_by_room_id(get_local_player_location())