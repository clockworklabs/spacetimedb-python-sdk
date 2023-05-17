from network_manager import NetworkManager
from helpers import *
from console_window import ConsoleWindow
from autogen import create_player_reducer, go_reducer, sign_in_reducer, sign_out_reducer, say_reducer

_game_controller = None

def register(game_controller):
    global _game_controller 
    _game_controller = game_controller

    say_reducer.register_on_say(on_say)
    create_player_reducer.register_on_create_player(on_create_player)
    sign_in_reducer.register_on_sign_in(on_sign_in)
    sign_out_reducer.register_on_sign_out(on_sign_out)
    go_reducer.register_on_go(on_go)

def on_say(caller: bytes, status: str, message: str, source_spawnable_entity_id: int, chat_text: str): 
    if status == "committed":
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(source_spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            if(get_local_player_entity_id() == source_spawnable_entity_id):
                ConsoleWindow.instance.print("You say \"{}\".\n".format(chat_text))
            else:
                source_name = get_name(source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} says \"{}\".\n".format(source_name,chat_text))

            ConsoleWindow.instance.prompt()

def on_create_player(caller: bytes, status: str, message: str, name: str, description: str): 
    if status == "committed" and NetworkManager.instance.identity != caller:
        local_room_id = get_local_player_room_id()
        source_player = Player.filter_by_identity(caller)
        source_location = Location.filter_by_spawnable_entity_id(source_player.spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(source_player.spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n")
            ConsoleWindow.instance.prompt()

def on_sign_in(caller: bytes, status: str, message: str, player_spawnable_entity_id: int):
    if status == "committed" and player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(player_spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n")
            ConsoleWindow.instance.prompt()

def on_sign_out(caller: bytes, status: str, message: str, player_spawnable_entity_id: int):
    if status == "committed" and player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(player_spawnable_entity_id)
        if(local_room_id == source_location.last_room_id):
            source_name = get_name(player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has left the game.\n")    
            ConsoleWindow.instance.prompt()

def on_go(caller: bytes, status: str, message: str, source_spawnable_entity_id: int, exit_direction: str):    
    global _game_controller 
    
    if status == "committed":
        if NetworkManager.instance.identity == caller:
            ConsoleWindow.instance.print("You go {}.\n".format(exit_direction))    
            _game_controller.prompt.room()
        else:
            local_room_id = get_local_player_room_id()
            source_location = Location.filter_by_spawnable_entity_id(source_spawnable_entity_id)
            if(source_location.last_room_id == local_room_id):
                source_name = get_name(source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} has left.\n".format(source_name))    
                ConsoleWindow.instance.prompt()
            elif(source_location.room_id == local_room_id):
                source_name = get_name(source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} arrives.\n".format(source_name))
                ConsoleWindow.instance.prompt()