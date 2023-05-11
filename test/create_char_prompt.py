import cmd
from enum import Enum

class CreateCharState(Enum):
    NAME = 1,
    DESCRIPTION = 2,
    CONFIRM = 3,
    
class CreateCharPrompt(cmd.Cmd):    
    prompt = 'What do you wish to be called\n>> '
    create_char_state = CreateCharState.NAME

    def __init__(self,c):
        super().__init__()
        self.name = None
        self.description = None
        self.success = False
        self.c = c

    def update_prompt(self):
        if self.create_char_state == CreateCharState.NAME:
            self.prompt = 'What do you wish to be called?\n>> ',
        elif self.create_char_state == CreateCharState.DESCRIPTION:
            self.prompt = 'Provide a brief description.\n>> '
        elif self.create_char_state == CreateCharState.CONFIRM:
            self.prompt = 'Name: {}\nDescription: {}\n\nDo you wish to create this character?\n>> '.format(self.name,self.description)

    def do_quit(self, arg):
        """Quit the game"""
        return True

    def default(self, line: str) -> None:
        if self.create_char_state == CreateCharState.NAME:
            self.name = line
            self.create_char_state = CreateCharState.DESCRIPTION
            self.update_prompt()
        elif self.create_char_state == CreateCharState.DESCRIPTION:
            self.description = line
            self.create_char_state = CreateCharState.CONFIRM
            self.update_prompt()
        elif self.create_char_state == CreateCharState.CONFIRM:
            if(line.lower() == 'y' or line.lower() == 'yes'):
                self.success = True
                return True
            else:
                self.create_char_state = CreateCharState.NAME
                self.update_prompt()