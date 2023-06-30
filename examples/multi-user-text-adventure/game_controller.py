from enum import Enum

import sys

sys.path.insert(0, "../..")

from spacetimedb_python_sdk.spacetimedb_client import SpacetimeDBClient

import autogen
from autogen.player import Player
from autogen.create_player_reducer import create_player

from console_window import ConsoleWindow
from create_char_prompt import CreateCharPrompt
from game_prompt import GamePrompt
import spacetimedb_python_sdk.local_config as local_config
from helpers import *

import reducer_handlers


class GameState(Enum):
    CONNECTING = 1
    CREATE_CHARACTER = 2
    SELECT_WORLD = 3
    WAIT_FOR_PLAYER = 4
    GAME = 5


class GameController:
    prompt = None
    initialized = False
    local_identity = None
    should_exit = False

    game_state = GameState.CONNECTING

    def __init__(self):
        local_config.init(".spacetime-mud", "settings.ini")
        auth_token = local_config.get_string("auth")
        SpacetimeDBClient.init(
            auth_token,
            "localhost:3000",
            "example-mud",
            False,
            autogen,
            on_connect=self.on_connect,
            on_identity=self.on_identity,
        )
        SpacetimeDBClient.instance.register_on_subscription_applied(
            self.on_subscription_applied
        )

        reducer_handlers.register(self)

    # returns True if should exit
    def update(self):
        SpacetimeDBClient.instance.update()

        if self.game_state == GameState.CONNECTING:
            if self.initialized:
                player = Player.filter_by_identity(self.local_identity)
                if player is not None:
                    ConsoleWindow.instance.print(
                        "Welcome back {}\n\n".format(
                            get_name(player.spawnable_entity_id)
                        )
                    )
                    self.prompt = GamePrompt()
                    self.game_state = GameState.GAME
                else:
                    self.game_state = GameState.CREATE_CHARACTER
                    self.prompt = CreateCharPrompt()
        elif self.game_state == GameState.CREATE_CHARACTER:
            if self.prompt.result:
                if self.prompt.result == "success":
                    # wait for player
                    create_player(self.prompt.name)
                    self.game_state = GameState.WAIT_FOR_PLAYER
                else:
                    self.should_exit = True
        elif self.game_state == GameState.WAIT_FOR_PLAYER:
            player = Player.filter_by_identity(self.local_identity)
            if player:
                ConsoleWindow.instance.print(
                    "Welcome {}\n\n".format(get_name(player.spawnable_entity_id))
                )
                self.prompt = GamePrompt()
                self.game_state = GameState.GAME
        elif self.game_state == GameState.GAME:
            if self.prompt.result == "quit":
                self.should_exit = True

    def on_identity(self, auth_token, identity):
        # save the auth_token for future sessions
        local_config.set_string("auth", auth_token)
        self.local_identity = SpacetimeDBClient.instance.identity

    def on_subscription_applied(self):
        if not self.initialized:
            self.initialized = True

    def on_connect(self):
        SpacetimeDBClient.instance.subscribe(
            [
                "SELECT * FROM Mobile",
                "SELECT * FROM Player",
                "SELECT * FROM Location",
                "SELECT * FROM Room",
                "SELECT * FROM RoomChat",
            ]
        )

    def exit(self):
        SpacetimeDBClient.instance.close()
