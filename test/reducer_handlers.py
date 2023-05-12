from network_manager import NetworkManager
from helpers import *
from console_window import ConsoleWindow

_game_controller = None

def register(game_controller):
    global _game_controller 
    _game_controller = game_controller

    NetworkManager.instance.register_reducer("say", on_say)
    NetworkManager.instance.register_reducer("create_player", on_create_player)
    NetworkManager.instance.register_reducer("sign_in", on_sign_in)
    NetworkManager.instance.register_reducer("sign_out", on_sign_out)
    NetworkManager.instance.register_reducer("go", on_go)

def on_say(caller, status, message, args): 
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

def on_create_player(caller, status, message, args): 
    if status == "committed" and NetworkManager.instance.identity != caller:
        local_room_id = get_local_player_room_id()
        source_player = Player.filter_by_identity(caller)
        source_location = Location.filter_by_spawnable_entity_id(source_player.spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(source_player.spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n".format(source_name,args.chat_text))
            ConsoleWindow.instance.prompt()

def on_sign_in(caller, status, message, args):
    if status == "committed" and args.player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(args.player_spawnable_entity_id)
        if(local_room_id == source_location.room_id):
            source_name = get_name(args.player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has entered the game.\n".format(source_name,args.chat_text))
            ConsoleWindow.instance.prompt()

def on_sign_out(caller, status, message, args):
    if status == "committed" and args.player_spawnable_entity_id != get_local_player_entity_id():
        local_room_id = get_local_player_room_id()
        source_location = Location.filter_by_spawnable_entity_id(args.player_spawnable_entity_id)
        if(local_room_id == source_location.last_room_id):
            source_name = get_name(args.player_spawnable_entity_id)    
            ConsoleWindow.instance.print("{} has left the game.\n".format(source_name,args.chat_text))    
            ConsoleWindow.instance.prompt()

def on_go(caller, status, message, args):    
    global _game_controller 
    
    if status == "committed":
        if NetworkManager.instance.identity == caller:
            ConsoleWindow.instance.print("You go {}.\n\n".format(args.exit_direction))    
            _game_controller.prompt.room()
        else:
            local_room_id = get_local_player_room_id()
            source_location = Location.filter_by_spawnable_entity_id(args.source_spawnable_entity_id)
            if(source_location.last_room_id == local_room_id):
                source_name = get_name(args.source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} has left.\n\n".format(source_name))    
                ConsoleWindow.instance.prompt()
            elif(source_location.room_id == local_room_id):
                source_name = get_name(args.source_spawnable_entity_id)    
                ConsoleWindow.instance.print("{} arrives.\n\n".format(source_name))
                ConsoleWindow.instance.prompt()
    else:
        print(status + " " + message)