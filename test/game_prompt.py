import cmd

from helpers import *

class GamePrompt(cmd.Cmd):
    prompt = '>> '    

    def __init__(self, c):
        super().__init__()

        self.c = c        
        self.update_prompt()        

    def update_prompt(self):
        room = get_local_player_room()
        
        room_name = self.c.blue(room.name)
        if len(room.exits) > 0:
            exits_names = []        
            for exit in room.exits:
                exits_names.append((str(exit.direction)).lower())
            exits_str = ', '.join(exits_names)            
        else:
            exits_str = "NONE"

        exits_str = self.c.yellow(f"[EXITS: {exits_str}]")

        spawnables_list = []
        for spawnable in Location.filter_by_room_id(room.room_id):
            if(spawnable.spawnable_entity_id != get_local_player_entity_id()):
                mob = Mobile.filter_by_spawnable_entity_id(spawnable.spawnable_entity_id)
                spawnables_list.append("You see {}.".format(mob.name))
        spawnables_str = "\n".join(spawnables_list)
        if(len(spawnables_list) > 0):
            spawnables_str = spawnables_str + "\n"

        prompt = self.c.red('>> ')
        self.prompt = f'{room_name}\n{room.description}\n{exits_str}\n{spawnables_str}{prompt}'

    def do_quit(self, arg):
        """Quit the game"""
        return True

    def do_look(self, arg):
        """Look around the room"""
        self.update_prompt()
        pass

    def do_go(self, direction):
        """Go in a direction"""
        room = get_local_player_room()
        if direction not in room.exits:
            print("You can't go that way!")
            return
        self.current_room = room['exits'][direction]
        self.update_prompt()

    def default(self, line: str) -> None:
        prompt = self.c.red('>> ')
        self.prompt = "Huh?!?\n" + prompt

    def postcmd(self, stop: bool, line: str) -> bool:
        return stop