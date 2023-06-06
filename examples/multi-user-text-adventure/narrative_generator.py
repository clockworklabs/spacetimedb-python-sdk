import json
import threading
import time
import uuid
from autogen import create_world_reducer, create_zone_reducer
from autogen.world import World
from autogen.zone import Zone
from openai_harness import openai_call
from zone_connection_generator import ZoneConnectionGenerator
from zone_generator import ZoneGenerator

class NarrativeGenerator:
    narrative_prompt_prefix = f"As a MUD game designer, you are creating a world using zones with rooms connected by exits.\n\n"
    active_world_generators = []
    retries = 0

    @classmethod
    def generate(cls, prompt):
        worldgen = NarrativeGenerator(prompt)
        NarrativeGenerator.active_world_generators.append(worldgen)
        worldgen.start(prompt)        

    def __init__(self, prompt):
        create_world_reducer.register_on_create_world(self.on_create_world)
        create_zone_reducer.register_on_create_zone(self.on_create_zone)

        self.world_id = None
                
    def start(self, user_prompt):
        prompt = f"{self.narrative_prompt_prefix} Create a cohesive game world, including an original and descriptive name and a clear and concise overall description of the setting and key features. Ensure proper syntax, formatting, and structure. The game world should be immersive, creative, and consistent with a theme or genre. It should also be original and not based on existing intellectual property unless it is considered public domain. Return only the name and description in JSON format. Example: {{ \"world_id\": \"short_world_id_with_underscores\" \"name\": \"World Name\", \"description\": \"Description\" }}\n\nInfo: {user_prompt}"
        print(f"Creating world narrative...")
        NarrativeGenerator.retries = 0
        threading.Thread(target=self.create_world, args=(prompt,)).start()

    def create_world(self,prompt):
        new_world_json = None
        try:
            new_world = openai_call(prompt)    
            new_world_json = json.loads(new_world)
        except Exception as e:
            print(e)
            if NarrativeGenerator.retries < 3:
                print("Error creating world narrative. Trying again.")
                NarrativeGenerator.retries += 1
                self.create_world(prompt)                
            else:
                print("Error creating world narrative. Exiting.")
                NarrativeGenerator.active_world_generators.remove(self)
            return
        self.world_id = new_world_json["world_id"]
        create_world_reducer.create_world(new_world_json["world_id"], new_world_json["name"], new_world_json["description"])

    def on_create_world(self, caller: bytes, status: str, message: str, world_id: str, world_name: str, world_description: str):
        if status == "committed":
            print(f"Create world narrative success! {world_name}")
            NarrativeGenerator.retries = 0
            threading.Thread(target=self.create_next_area, args=(world_id,)).start()
            
    def create_next_area(self, world_id):
        world_json = None
        zone_jsons = None
        try:
            world_json = json.dumps(World.filter_by_world_id(world_id).data)
            zone_jsons = json.dumps([zone.data for zone in Zone.filter_by_world_id(world_id)])
        except Exception as e:
            print(e)
            print("Error parsing existing world data. Exiting.")
            NarrativeGenerator.active_world_generators.remove(self)
            return

        prompt = f"You are a game designer for a MUD (multiuser dungeon). You are coming up with a list of zones for your game. Zones are a collection of rooms that make up a larger area like a castle or a forest. In this step we are only creating the name and the description of the zone. We will create the rooms later. World Info:\n{world_json}\nExisting Zone Info:{zone_jsons}\n\nCreate the json for a new zone in this world. Format: {{ \"zone_id\": \"short_zone_id_with_underscores\" \"name\": \"Area Name\", \"description\": \"Description\"}}"

        new_zone_json = None
        try:
            new_zone = openai_call(prompt)
            new_zone_json = json.loads(new_zone)
        except Exception as e:
            print(e)
            if NarrativeGenerator.retries < 3:
                print("Error creating zone narrative. Trying again.")
                NarrativeGenerator.retries += 1
                self.create_next_area(world_id)                
            else:
                print("Error creating zone narrative. Exiting.")
                NarrativeGenerator.active_world_generators.remove(self)
            return
        zone_id = uuid.uuid4().hex
        print("Creating zone narrative...")
        create_zone_reducer.create_zone(new_zone_json["zone_id"], world_id, new_zone_json["name"], new_zone_json["description"])

    def on_create_zone(self, caller: bytes, status: str, message: str, zone_id: str, world_id: str, zone_name: str, zone_description: str):
        if status == "committed":
            print(f"Create zone narrative success! {zone_name}")
            zone_iter = Zone.filter_by_world_id(self.world_id)
            if len(zone_iter) < 1:
                NarrativeGenerator.retries = 0
                threading.Thread(target=self.create_next_area, args=(world_id,)).start()
            else:
                print("World generation complete!")
                # create a zone generator for each zone and start it up
                for zone in zone_iter:
                    ZoneGenerator.generate(zone.zone_id)
                
                # start a thread that waits for the zone generators to complete
                threading.Thread(target=self.wait_for_zone_generators).start()

    def wait_for_zone_generators(self):
        while ZoneGenerator.active_zone_generators[self.world_id] is not None and len(ZoneGenerator.active_zone_generators[self.world_id]) > 0:
            time.sleep(0.1)
            pass
        print("All zone generators complete!")
        
        ZoneConnectionGenerator.generate(self.world_id)
        # first we will ask openai to pick the starting zone to connect to the nexus
        # then we ask openai to find the room in that zone that connects to the nexus and connect it
        # then we ask openai to pick two zones that should be connected and pick a room from each 
