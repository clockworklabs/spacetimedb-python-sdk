from enum import Enum

from spacetimedb_python_sdk.network_manager import NetworkManager

import autogen
from autogen.player import Player
from autogen.create_player_reducer import create_player

from console_window import ConsoleWindow
from create_char_prompt import CreateCharPrompt
from game_prompt import GamePrompt
from helpers import *

import reducer_handlers

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
        NetworkManager.init("localhost:3000", "example-mud", False, autogen, on_connect=self.on_connect)
        NetworkManager.instance.register_on_transaction(self.on_transaction)

        reducer_handlers.register(self)

    # returns True if should exit
    def update(self):
        # Execute your desired function or code here
        NetworkManager.instance.update()

        # DAB Todo: Break these up into functions
        if self.game_state == GameState.CONNECTING:
            if self.initialized:
                player = Player.filter_by_identity(self.local_identity)
                if player is not None:     
                    ConsoleWindow.instance.print("Welcome back {}\n\n".format(get_name(player.spawnable_entity_id))) 
                    self.prompt = GamePrompt()
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
                    self.should_exit = True
        elif self.game_state == GameState.WAIT_FOR_PLAYER:
            player = Player.filter_by_identity(self.local_identity)
            if player:
                ConsoleWindow.instance.print("Welcome {}\n\n".format(get_name(player.spawnable_entity_id)))
                self.prompt = GamePrompt()
                self.game_state = GameState.GAME
        elif self.game_state == GameState.GAME:
            if self.prompt.result == "quit":
                self.should_exit = True
        

    def on_transaction(self):
        if not self.initialized:
            self.local_identity = NetworkManager.instance.identity
            self.initialized = True  

    def on_connect(self):
        NetworkManager.instance.subscribe(
            ["SELECT * FROM Mobile", 
             "SELECT * FROM Player", 
             "SELECT * FROM Location",
             "SELECT * FROM Room",
             "SELECT * FROM RoomChat"])

    def exit(self):        
        NetworkManager.instance.close()