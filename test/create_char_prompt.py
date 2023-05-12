import cmd
from enum import Enum

from console_window import ConsoleWindow

class CreateCharState(Enum):
    NAME = 1,
    DESCRIPTION = 2,
    CONFIRM = 3,
    
class CreateCharPrompt():    
    create_char_state = CreateCharState.NAME

    def __init__(self):
        super().__init__()
        self.name = None
        self.description = None
        self.success = False
        self.result = None

        ConsoleWindow.instance.print('What do you wish to be called?\n')   
        ConsoleWindow.instance.prompt()

    def command(self, line: str):
        if line.lower() == "quit":
            self.result = "quit"
            return True
        else:
            if self.create_char_state == CreateCharState.NAME:
                self.name = line
                self.create_char_state = CreateCharState.DESCRIPTION
                ConsoleWindow.instance.print('Provide a brief description.\n')
                ConsoleWindow.instance.prompt()
            elif self.create_char_state == CreateCharState.DESCRIPTION:
                self.description = line
                self.create_char_state = CreateCharState.CONFIRM
                ConsoleWindow.instance.print('Name: {}\nDescription: {}\n\nDo you wish to create this character? (y/n)\n'.format(self.name,self.description))            
                ConsoleWindow.instance.prompt()
            elif self.create_char_state == CreateCharState.CONFIRM:
                if(line.lower() == 'y' or line.lower() == 'yes'):
                    self.result = "success"
                    return True
                else:
                    self.create_char_state = CreateCharState.NAME
                    ConsoleWindow.instance.print('What do you wish to be called?\n')
                    ConsoleWindow.instance.prompt()
                