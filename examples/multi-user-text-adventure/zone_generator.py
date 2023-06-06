from collections import defaultdict
import json
import random
import threading
import uuid
from autogen import create_connection_reducer, create_room_reducer, create_zone_reducer
from autogen.room import Room
from autogen.world import World
from autogen.zone import Zone
from helpers import get_world_id, get_zone_rooms_json
from json_encoding import RoomEncoder
from openai_harness import openai_call

# DAB TODO: Have the AI go back and add hints or clues to rooms for their connections
# DAB TODO: Fix the generator reusing the same directions
# DAB TODO: Break all of these prompts into "commands" or "tasks"

class ZoneGenerator:
    zone_prompt_prefix = f"As a MUD game designer, you create zones with rooms connected by exits."
    active_zone_generators = defaultdict(list)
    retries = 0
    num_rooms_to_create = 0    

    @classmethod
    def generate(cls,zone_id):
        zonegen = ZoneGenerator(zone_id)        
        zonegen.start()   
    
    def __init__(self, zone_id):
        self.zone = Zone.filter_by_zone_id(zone_id)
        self.world = World.filter_by_world_id(self.zone.world_id)
        # we store this so we can create a room connection after the next room is created
        self.last_adjacent_room_id = None
        # lets create a number of rooms between 10 and 20        
        #self.num_rooms_to_create = random.randint(5, 20)
        self.num_rooms_to_create = 10
        self.is_complete = False
        
        self.zone_prompt_prefix += f"\n\nWorld narrative: {json.dumps(self.world.data)}\n\nZone narrative: {json.dumps(self.zone.data)}\n\n"
        ZoneGenerator.active_zone_generators[self.world.world_id].append(self)

        create_room_reducer.register_on_create_room(self.on_create_room)
        create_connection_reducer.register_on_create_connection(self.on_create_connection)

    def start(self):
        print(f"Creating zone rooms ({self.zone.name})...")
        threading.Thread(target=self.create_initial_room).start()
    
    def on_complete(self):
        # deregister reducers
        #create_room_reducer.deregister_on_create_room(self.on_create_room)
        #create_connection_reducer.deregister_on_create_connection(self.on_create_connection)
        self.is_complete = True
        ZoneGenerator.active_zone_generators[self.world.world_id].remove(self)
        if len(ZoneGenerator.active_zone_generators[self.world.world_id]) == 0:
            del ZoneGenerator.active_zone_generators[self.world.world_id]

    def create_initial_room(self):
        self.create_room("Create first zone room.")

    def create_next_room(self, previous_room_id, prompt_suffix=""):
        self.last_adjacent_room_id = previous_room_id
        previous_room_json=None
        try:
            previous_room = Room.filter_by_room_id(previous_room_id)
            previous_room_json = json.dumps(previous_room, cls=RoomEncoder)
        except Exception as e:
            print(e)
            print("Error parsing previous room data. Exiting.")
            return

        new_room_json = self.create_room(f"Adjacent room info:\n\n{previous_room_json}.\n\nUse adjacent room info to generate new room ideas without referencing the user's origin in the description. Additional Info: {prompt_suffix}")    

    def create_room(self,prompt_suffix):        
        prompt = f"{self.zone_prompt_prefix}Create a concise room description without assuming the user's previous knowledge of other rooms.\n\n{prompt_suffix}\n\nRespond in JSON format Example: {{ \"world_id\": \"short_world_id_with_underscores\", \"name\": \"Room Name\", \"description\": \"Description\" }}"

        new_room_json = None
        try:
            new_room = openai_call(prompt)
            new_room_json = json.loads(new_room)
        except Exception as e:
            print(e)
            if self.retries < 3:
                print("Error creating room. Trying again.")
                self.retries += 1
                self.create_room(prompt_suffix)                
            else:
                print("Error creating room. Exiting.")
                self.on_complete()
            return
        
        room_id = uuid.uuid4().hex
        print("Creating room...")
        create_room_reducer.create_room(self.zone.zone_id, room_id, new_room_json["name"], new_room_json["description"])    
    
    def on_create_room(self, caller: bytes, status: str, message: str, zone_id: str, room_id: str, room_name: str, room_description: str):
        world_id = get_world_id(room_id)
        if not self.is_complete and self.world.world_id == world_id and status == "committed":
            print(f"Create room success! {room_name}")
            self.retries = 0            
            if self.last_adjacent_room_id is None:
                # no need to make a room connection since this is the first room, lets make the next room
                threading.Thread(target=self.create_next_room, args=(room_id,)).start()
            else:
                # make a room connection between the last room and this room
                threading.Thread(target=self.create_room_connection, args=(self.last_adjacent_room_id, room_id)).start()

    def create_room_connection(self, from_room_id, to_room_id):
        from_room_json = None
        to_room_json = None
        try:
            from_room_json = json.dumps(Room.filter_by_room_id(from_room_id), cls=RoomEncoder)
            to_room_json = json.dumps(Room.filter_by_room_id(to_room_id), cls=RoomEncoder)
        except Exception as e:
            print(e)
            print("Error parsing from or to room data. Exiting.")
            return

        prompt = f"{self.zone_prompt_prefix}Create a connection between these two rooms by adding an appropriate exit or exits. When adding a connection, make sure you don't pick a direction that already exists for that room. If two-way travel is possible, create two exits (one from each room), otherwise create a single exit.\n\n{from_room_json}\n\n{to_room_json}\n\nResponse in JSON Example: {{\"from_room_exit\": {{ \"direction\": \"north\", \"description\": \"Description\" }}, \"to_room_exit\": {{ \"direction\": \"south\", \"description\": \"Description\" }}}}\n\n"

        connection_json = None
        try:
            connection = openai_call(prompt)
            connection_json = json.loads(connection)
            if not connection_json["from_room_exit"]:
                raise Exception("No from room exit provided.")
        except Exception as e:
            print(e)
            if self.retries < 3:
                print("Error creating room connection. Trying again.")
                self.retries += 1
                self.create_room_connection(from_room_id, to_room_id)
            else:
                print("Error creating room. Exiting.")
                self.on_complete()
            return
        
        to_direction = ""
        to_exit_description = ""
        if connection_json["to_room_exit"]:
            to_direction = connection_json["to_room_exit"]["direction"]
            to_exit_description = connection_json["to_room_exit"]["description"]
        create_connection_reducer.create_connection(from_room_id, to_room_id, connection_json["from_room_exit"]["direction"], to_direction, connection_json["from_room_exit"]["description"], to_exit_description)
        
    def on_create_connection(self, caller: bytes, status: str, message: str, from_room_id: str, to_room_id: str, from_direction: str, to_direction: str, from_exit_description: str, to_exit_description: str):
        world_id = get_world_id(from_room_id)
        if not self.is_complete and world_id == self.world.world_id and status == "committed":
            from_room = Room.filter_by_room_id(from_room_id)
            to_room = Room.filter_by_room_id(to_room_id)
            print(f"Create connection success! {from_room.name} to {to_room.name}")
            zone_rooms = Room.filter_by_zone_id(self.zone.zone_id)
            if len(zone_rooms) < self.num_rooms_to_create:
                self.retries = 0
                # we need to create another room
                threading.Thread(target=self.find_next_room).start()
            else:
                # This is not working yet, so we will just exit for now
                #self.check_for_additional_connections()
                print (f"Zone generation complete! {self.zone.name}")
                self.on_complete()

    def find_next_room(self):        
        zone_rooms_json = get_zone_rooms_json(self.zone.zone_id, False)
        
        # prompt the ai to find the next room
        prompt = f"{self.zone_prompt_prefix}Select the location of the next room in the zone by choosing an adjacent room from the provided list. Return the room_id of the selected adjacent room as the adjacent_room_id in the response. Also return some information to be used in the prompt to create the description for this next room. \n\n{zone_rooms_json}\n\nReturn the response in JSON format. Example {{ \"adjacent_room_id\": \"room_id\", \"room_creation_info\": \"Prompt\" }}"

        next_room_json = None
        try:
            next_room = openai_call(prompt)
            next_room_json = json.loads(next_room)
            if not next_room_json["adjacent_room_id"] or Room.filter_by_room_id(next_room_json["adjacent_room_id"]) is None:
                raise Exception("No adjacent room provided.")
        except Exception as e:
            print(e)
            if self.retries < 3:
                print("Error finding next room. Trying again.")
                self.retries += 1
                self.find_next_room()
            else:
                print("Error finding next room. Exiting.")
                self.on_complete()
            return

        # create the next room
        self.create_next_room(next_room_json["adjacent_room_id"], next_room_json["room_creation_info"])

    # this function will repeatedly ask the AI to create additional connections between rooms until it can't find any more
    def check_for_additional_connections(self):
        zone_rooms_json = get_zone_rooms_json(self.zone.zone_id, False)

        prompt = f"{self.zone_prompt_prefix}Analyze rooms and exits to find two rooms that can have an additional connection. Create one or two exits depending on whether two-way travel is possible. When choosing the direction, pick a direction that makes sense in the context and don't pick a direction that is already used in one of the rooms. Return empty json if no connection is found.\n\n{zone_rooms_json}\n\nResponse in JSON Example: {{\"from_room_id\": \"room_id\", \"to_room_id\": \"room_id\", \"from_room_exit\": {{ \"direction\": \"north\", \"description\": \"Description\" }}, \"to_room_exit\": {{ \"direction\": \"south\", \"description\": \"Description\" }}}}\n\n"

        connection_json = None
        try:
            connection = openai_call(prompt)
            connection_json = json.loads(connection)
        except Exception as e:  
            print(e)
            if self.retries < 3:
                print("Error finding additional connections. Trying again.")
                self.retries += 1
                self.check_for_additional_connections()
            else:
                print("Error finding additional connections. Exiting.")
                self.on_complete()
            return
        
        if not connection_json["from_room_id"]:
            print (f"Zone generation complete! {self.zone.name}")
            self.on_complete()
        else:
            # create the connection
            if connection_json["to_room_exit"]:
                to_direction = connection_json["to_room_exit"]["direction"]
                to_exit_description = connection_json["to_room_exit"]["description"]
            create_connection_reducer.create_connection(connection_json["from_room_id"], connection_json["to_room_id"], connection_json["from_room_exit"]["direction"], to_direction, connection_json["from_room_exit"]["description"], to_exit_description)