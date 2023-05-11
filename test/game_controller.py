import threading
import time

from colorful import Colorful

from network_manager import NetworkManager
from client_cache import ClientCache
import autogen

from create_char_prompt import CreateCharPrompt
from game_prompt import GamePrompt
from helpers import *
from autogen.player import Player
from autogen.create_player_reducer import create_player

class GameController:
    network_manager = None
    prompt = None
    initialized = False
    local_identity = None
    should_exit = False

    def __init__(self):
        NetworkManager.init(autogen, on_connect=self.on_connect)
        NetworkManager.instance.register_on_transaction(self.on_transaction)

        # DAB Note: this should be called on the main thread but cmdloop blocks (we need to fix this)
        self.update_thread = threading.Thread(target=self.network_update)
        self.update_thread.start()

    def network_update(self):
        while not self.should_exit:
            # Execute your desired function or code here
            NetworkManager.instance.update()
            time.sleep(0.1)        

    def on_transaction(self):
        if not self.initialized:
            self.local_identity = NetworkManager.instance.identity
            self.initialized = True

    def play(self):        
        # wait for game state
        while not self.initialized:
            time.sleep(0.1)
        
        c = Colorful()

        player = Player.filter_by_identity(self.local_identity)
        if player is not None:       
            print("Welcome back {}\n".format(get_name(player.spawnable_entity_id)))                               
        else:
            self.prompt = CreateCharPrompt(c)
            self.prompt.cmdloop()
            if self.prompt.success:
                # wait for player
                create_player(self.prompt.name, self.prompt.description)
                while player is None:
                    player = Player.filter_by_identity(self.local_identity)

                print("Welcome {}\n".format(get_name(player.spawnable_entity_id)))

        if player is not None:
            # Start the prompt loop
            self.prompt = GamePrompt(c)
            self.prompt.cmdloop()

        print("Thanks for playing!")

        # Stop the update thread
        self.should_exit = True
        NetworkManager.instance.close()    

    def on_connect(self):
        NetworkManager.instance.subscribe(
            ["SELECT * FROM Mobile", 
             "SELECT * FROM Player", 
             "SELECT * FROM Location",
             "SELECT * FROM Room"])

    def exit(self):
        self.should_exit = True
        NetworkManager.instance.close()