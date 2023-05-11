import threading
import time

from network_manager import NetworkManager
from client_cache import ClientCache
import autogen

from create_char_prompt import CreateCharPrompt
from game_prompt import GamePrompt

class GameController:
    network_manager = None
    prompt = None
    initialized = False

    def __init__(self):
        self.network_manager = NetworkManager(autogen, on_connect=lambda: self.on_connect)
        self.network_manager.register_on_transaction(lambda: self.on_transaction)
        self.network_manager.register_row_update("Player",lambda: self.on_player_update)

        self.update_thread = threading.Timer(0.1, self.network_manager.update)
        self.update_thread.start()

    def on_transaction(self):
        if not self.initialized:
            self.initialized = True

    def play(self):
        # wait for game state
        while not self.initialized:
            time.sleep(0.1)
                        
        # see if we have a player
        self.prompt = CreateCharPrompt()
        self.prompt.cmdloop()

        if self.prompt.success:
            # Start the prompt loop
            self.prompt = GamePrompt()
            self.prompt.cmdloop()

        print("Thanks for playing!")

        # Stop the update thread
        self.update_thread.cancel()
        self.network_manager.close()

    def exit(self):
        # cleanup
        pass

    def on_connect(self):
        self.network_manager.subscribe(["SELECT * FROM Mobile", "SELECT * FROM Room"])
        self.network_manager.reducer_call("add", "John")

    def on_player_update(self, row_op, old_value, new_value):
        print("NEW VALUE: " + str(new_value))