import copy
import json
from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient

from autogen.mobile import Mobile
from autogen.player import Player
from autogen.location import Location
from autogen.room import Room
from autogen.zone import Zone
from json_encoding import RoomEncoder


def get_name(spawnable_entity_id) -> str:
    mobile = Mobile.filter_by_spawnable_entity_id(spawnable_entity_id)
    return mobile.name if mobile else "Unknown"


def get_local_player_entity_id() -> int:
    local_identity = SpacetimeDBClient.instance.identity
    player = Player.filter_by_identity(local_identity)
    return player.spawnable_entity_id if player else None


def get_local_player_room_id() -> str:
    local_player_id = get_local_player_entity_id()
    if local_player_id:
        location = Location.filter_by_spawnable_entity_id(local_player_id)
        return location.room_id if location else None


def get_room(room_id) -> Room:
    return Room.filter_by_room_id(room_id)


def get_local_player_room() -> Room:
    return Room.filter_by_room_id(get_local_player_room_id())


def get_exits_strs(room):
    if room:
        return [exit.direction for exit in room.exits]
    return ""


def get_world_id(room_id):
    room = get_room(room_id)
    if room:
        zone = Zone.filter_by_zone_id(room.zone_id)
        if zone:
            return zone.world_id
    return None


def get_world_rooms_json(world_id, include_descriptions):
    rooms_list = None
    if not world_id:
        rooms_list = list(Room.iter())
    else:
        rooms_list = []
        world_zones = Zone.filter_by_world_id(world_id)
        for zone in world_zones:
            rooms_list.extend(Room.filter_by_zone_id(zone.zone_id))

    return convert_rooms_list_to_json(rooms_list, include_descriptions)


def get_zone_rooms_json(zone_id, include_descriptions):
    rooms_list = None
    if not zone_id:
        rooms_list = list(Room.iter())
    else:
        rooms_list = Room.filter_by_zone_id(zone_id)

    return convert_rooms_list_to_json(rooms_list, include_descriptions)


def convert_rooms_list_to_json(rooms_list, include_descriptions):
    rooms_json = None

    try:
        rooms_json = json.dumps(rooms_list, cls=RoomEncoder)
        if not include_descriptions:
            rooms_list = json.loads(rooms_json)
            for room in rooms_list:
                del room["description"]
                del room["exits"]
        rooms_json = json.dumps(rooms_list)
    except Exception as e:
        print(e)
        print("Error parsing rooms data. Exiting.")
        return

    return rooms_json
