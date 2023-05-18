import cmd

from helpers import *
from console_window import ConsoleWindow
from autogen import say_reducer
from autogen import go_reducer

class GamePrompt(cmd.Cmd):
    result = None

    def __init__(self):
        super().__init__()

        self.room()        

    def room(self):
        room = get_local_player_room()
        
        if room:
            ConsoleWindow.instance.print(room.name + "\n","room_name")
            ConsoleWindow.instance.print(room.description + "\n")

            if len(room.exits) > 0:
                exits_strs = []        
                for exit in room.exits:
                    exits_strs.append(exit.direction.lower())
                exits_str = ', '.join(exits_strs)            
            else:
                exits_str = "NONE"

            ConsoleWindow.instance.print(f"[EXITS: {exits_str}]\n", "exits")

            spawnables_list = []
            for spawnable in Location.filter_by_room_id(room.room_id):
                if(spawnable.spawnable_entity_id != get_local_player_entity_id()):
                    mob = Mobile.filter_by_spawnable_entity_id(spawnable.spawnable_entity_id)
                    spawnables_list.append("You see {}.".format(mob.name))
            spawnables_str = "\n".join(spawnables_list)
            if(len(spawnables_list) > 0):
                spawnables_str = spawnables_str + "\n"

            ConsoleWindow.instance.print(spawnables_str)
            ConsoleWindow.instance.print(f"\n")
            
            ConsoleWindow.instance.prompt()

    def do_go(self, exit):
        """Go in a direction"""
        room = get_local_player_room()
        if exit not in room.exits:
            ConsoleWindow.instance.print(f"You can't go that way!\n")
            ConsoleWindow.instance.prompt()

            return
        
        go_reducer.go(get_local_player_entity_id(), exit.direction)

    def command(self, line: str):
        room = get_local_player_room()
        exits_strs = get_exits_strs(room)

        if line.lower() == "quit" or line.lower() == "q":
            self.result = "quit"
        elif line.lower() == "look" or line.lower() == "l":
            self.room()        
        elif line.lower().startswith("say ") or line.lower().startswith("'"):
            prefix = "say " if line.lower().startswith("say ") else "'"
            message = line[len(prefix):]
            say_reducer.say(get_local_player_entity_id(), message)
        elif line.lower() in exits_strs:
            index = exits_strs.index(line.lower())
            self.do_go(room.exits[index])
        else:            
            ConsoleWindow.instance.print("Huh?!?\n")
            ConsoleWindow.instance.prompt()