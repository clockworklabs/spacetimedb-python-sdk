import json
import threading
from autogen import create_connection_reducer
from autogen.room import Room
from autogen.world import World
from autogen.zone import Zone
from helpers import get_world_rooms_json, get_zone_rooms_json
from openai_harness import openai_call

# this class connects the zones together
class ZoneConnectionGenerator:
    zone_prompt_prefix = f"As a MUD game designer, you create zones with rooms connected by exits."
    active_zone_generator = None

    @classmethod
    def generate(cls,world_id):
        worldgen = ZoneConnectionGenerator(world_id)        
        worldgen.start()   

    def __init__(self, world_id):
        self.world = World.filter_by_world_id(world_id)
        self.zone_prompt_prefix += f"\n\nWorld narrative: {json.dumps(self.world.data)}\n\nZone narratives: {json.dumps([zone.data for zone in Zone.iter()])}\n\n"
        ZoneConnectionGenerator.active_zone_generator = self

        create_connection_reducer.register_on_create_connection(self.on_create_connection)

    def start(self):
        has_nexus_connection = False
        zones = Zone.filter_by_world_id(self.world.world_id)
        # check if any zones have a "nexus" connection
        for zone in zones:
            if zone.connections and "nexus" in zone.connections:
                has_nexus_connection = True
                return
            
        if not has_nexus_connection:
            threading.Thread(target=self.create_nexus_connection).start()
        else:
            threading.Thread(target=self.create_next_connection).start()

    def on_complete(self):
        #create_connection_reducer.unregister_on_create_connection(self.on_create_connection)
        ZoneConnectionGenerator.active_zone_generator = None

    def create_nexus_connection(self):
        room_json = get_world_rooms_json(world_id=self.world.world_id, include_descriptions=False)

        prompt = f"{self.zone_prompt_prefix}Choose the ideal room within the zones as the initial arrival point for players entering this world. Return the room_id of the room you selected in room_id in the response JSON. Info: {room_json}\n\nRespond in JSON format Example: {{ \"room_id\": \"room_id\" }}. Remove any explanatory text or additional information from the JSON response."
        try:
            start_room = openai_call(prompt)
            start_room_json = json.loads(start_room)
        except Exception as e:
            print(e)
            print("Error creating nexus connection. Exiting.")
            self.on_complete()
            return
                
        create_connection_reducer.create_connection("start", start_room_json["room_id"], self.world.world_id, "nexus", "Enter the world.", "Return to the Nexus.")
        
    def create_next_connection(self):
        world_rooms_json = get_world_rooms_json(self.world.world_id, include_descriptions=False)
        prompt = f"{self.zone_prompt_prefix}Analyze the provided list of zones and their rooms. We are going to attempt to add a connection between zones by picking two rooms in different zones and connecting them. If there are any zones that do not have any connections, choose one of those zones first. If all zones have atleast one connection, see if there are any other zone connections that might make sense. When adding a connection, make sure you don't pick a direction that already exists for that room. If no zone connections need to be made, just return an empty JSON.\n\nInfo: {self.get_zone_narratives_json()}\n\n{world_rooms_json}\n\nRespond in JSON format Example: {{ \"from_room_id\": \"room_id\", \"to_room_id\": \"room_id\", \"from_direction\": \"north\", \"to_direction\": \"south\", \"from_exit_description\": \"Enter the room.\", \"to_exit_description\": \"Exit the room.\" }}"

        try:
            room_connection = openai_call(prompt)
            room_connection_json = json.loads(room_connection)
        except Exception as e:
            print(e)
            print("Error creating zone connection. Exiting.")
            self.on_complete()
            return
        
        if not room_connection_json['from_room_id']:
            print(f"Zone Connection Generation Complete! {self.world.name}")
            self.on_complete()
            return

        create_connection_reducer.create_connection(room_connection_json["from_room_id"], room_connection_json["to_room_id"], room_connection_json['from_direction'], room_connection_json['to_direction'], room_connection_json['from_exit_description'], room_connection_json['to_exit_description'])

    def on_create_connection(self, caller: bytes, status: str, message: str, from_room_id: str, to_room_id: str, from_direction: str, to_direction: str, from_exit_description: str, to_exit_description: str):
        if status == "committed":
            #we are not worrying about zone to zone additional connections for now
            #threading.Thread(target=self.create_next_connection).start()
            print(f"Zone Connection Generation Complete! {self.world.name}")
            self.on_complete()
    
    def get_zone_narratives_json(self):
        zone_narratives = Zone.filter_by_world_id(self.world.world_id)
        zone_narratives_json = None
        try:
            zone_narratives_json = json.dumps([zone.data for zone in zone_narratives])
        except Exception as e:
            print(e)
            print("Error parsing zone rooms data. Exiting.")
            return
        
        return zone_narratives_json