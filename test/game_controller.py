from network_manager import NetworkManager

import autogen

from create_char_prompt import CreateCharPrompt
from game_prompt import GamePrompt
from helpers import *
from autogen.player import Player
from autogen.create_player_reducer import create_player
from console_window import ConsoleWindow
from enum import Enum

class GameState(Enum):
    CONNECTING = 1
    CREATE_CHARACTER = 2
    WAIT_FOR_PLAYER = 3
    GAME = 4

class GameController:
    network_manager = None
    prompt = None
    initialized = False
    local_identity = None
    should_exit = False

    game_state = GameState.CONNECTING

    def __init__(self):
        NetworkManager.init(autogen, on_connect=self.on_connect)
        NetworkManager.instance.register_on_transaction(self.on_transaction)

    # returns True if should exit
    def update(self):
        # Execute your desired function or code here
        NetworkManager.instance.update()

        # DAB Todo: Break these up into functions
        if self.game_state == GameState.CONNECTING:
            if self.initialized:
                player = Player.filter_by_identity(self.local_identity)
                if player is not None:     
                    ConsoleWindow.instance.print("Welcome back {}".format(get_name(player.spawnable_entity_id))) 
                    self.game_state = GameState.GAME
                else:
                    self.game_state = GameState.CREATE_CHARACTER
                    self.prompt = CreateCharPrompt()
        elif self.game_state == GameState.CREATE_CHARACTER:
            if self.prompt.result:
                if self.prompt.result == "success":
                    # wait for player
                    create_player(self.prompt.name, self.prompt.description)
                    self.game_state = GameState.WAIT_FOR_PLAYER
                else:
                    return True
        elif self.game_state == GameState.WAIT_FOR_PLAYER:
            player = Player.filter_by_identity(self.local_identity)
            if player:
                ConsoleWindow.instance.print("Welcome {}".format(get_name(player.spawnable_entity_id)))
                self.prompt = GamePrompt()
                self.game_state = GameState.GAME
        

    def on_transaction(self):
        if not self.initialized:
            self.local_identity = NetworkManager.instance.identity
            self.initialized = True  

    def on_connect(self):
        NetworkManager.instance.subscribe(
            ["SELECT * FROM Mobile", 
             "SELECT * FROM Player", 
             "SELECT * FROM Location",
             "SELECT * FROM Room"])

    def exit(self):
        self.should_exit = True
        NetworkManager.instance.close()