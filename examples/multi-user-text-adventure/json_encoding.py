import json

from autogen.exit import Exit
from autogen.room import Room


class RoomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Room) or isinstance(obj, Exit):
            return obj.data
        return super().default(obj)  