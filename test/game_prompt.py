import cmd

class GamePrompt(cmd.Cmd):
    prompt = '>> '

    def __init__(self):
        super().__init__()
        self.rooms = {
            'start': {
                'name': 'Start Room',
                'description': 'You are standing in a small, dimly lit room.',
                'exits': {'north': 'north_room', 'east': 'east_room'}
            },
            'north_room': {
                'name': 'North Room',
                'description': 'You are in a large, spacious room with high ceilings.',
                'exits': {'south': 'start'}
            },
            'east_room': {
                'name': 'East Room',
                'description': 'You are in a small room with a single door to the west.',
                'exits': {'west': 'start'}
            }
        }
        self.current_room = 'start'
        self.update_prompt()

    def update_prompt(self):
        room = self.rooms[self.current_room]
        self.prompt = f'{room["name"]}\n{room["description"]}\n>> '

    def do_quit(self, arg):
        """Quit the game"""
        return True

    def do_look(self, arg):
        """Look around the room"""
        pass

    def do_go(self, direction):
        """Go in a direction"""
        room = self.rooms[self.current_room]
        if direction not in room['exits']:
            print("You can't go that way!")
            return
        self.current_room = room['exits'][direction]
        self.update_prompt()

    def postcmd(self, stop: bool, line: str) -> bool:
        return stop