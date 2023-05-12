from network_manager import NetworkManager
from helpers import *
from console_window import ConsoleWindow

def register():
    NetworkManager.instance.register_reducer("say", on_say)
    NetworkManager.instance.register_reducer("create_player", on_create_player)
    NetworkManager.instance.register_reducer("sign_in", on_sign_in)
    NetworkManager.instance.register_reducer("sign_out", on_sign_out)

def on_say(caller, status, args): 
    if status == "committed":
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(args.source_spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            if(get_local_player_entity_id() == args.source_spawnable_entity_id):
                ConsoleWindow.instance.print("You say \"{}\".\n".format(args.chat_text))
            else:
                source_name = get_name(args.source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} says \"{}\".\n".format(source_name,args.chat_text))

            ConsoleWindow.instance.prompt()

def on_create_player(caller, status, args): 
    if status == "committed" and NetworkManager.instance.identity != caller:
        local_room_id = get_local_player_room_id()
        source_player = Player.filter_by_identity(caller)
        source_location = Location.filter_by_spawnable_entity_id(source_player.spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(source_player.spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n".format(source_name,args.chat_text))
            ConsoleWindow.instance.prompt()

def on_sign_in(caller, status, args):
    if status == "committed" and args.player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(args.player_spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(args.player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n".format(source_name,args.chat_text))
            ConsoleWindow.instance.prompt()

def on_sign_out(caller, status, args):
    if status == "committed" and args.player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(args.player_spawnable_entity_id)
        if(local_room_id == source_location.last_room_id):
            source_name = get_name(args.player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has left the game.\n".format(source_name,args.chat_text))    
            ConsoleWindow.instance.prompt()
