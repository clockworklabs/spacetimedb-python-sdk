import os
import random
import sys
import signal
import time

from PyQt6.QtWidgets import QApplication
from console_window import ConsoleWindow

# Get the directory of sdk module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the parent directory to the system path
sys.path.append(parent_dir)

from game_controller import GameController
game_controller = None

def signal_handler(sig, frame):
    print("Received termination signal")
    game_controller.exit()
    # Add any cleanup or shutdown code here
    exit(0)


# Register the signal handler function for the SIGINT and SIGBREAK signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGBREAK, signal_handler)

if __name__ == "__main__":    
    random.seed()
    
    game_controller = GameController()

    app = QApplication(sys.argv)
    window = ConsoleWindow(game_controller)
    window.resize(800, 600)
    window.show()
    window.command_line_edit.setFocus()    
    
    while not game_controller.should_exit:
        app.processEvents()
        game_controller.update()
        time.sleep(1/60)

    game_controller.exit()

    window.close()
    app.quit()
    sys.exit()