import os
import sys
import signal
import time

from PyQt6.QtWidgets import QApplication
from console_window import ConsoleWindow

# Get the parent directory of the current file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    game_controller = GameController()

    app = QApplication(sys.argv)
    window = ConsoleWindow(game_controller)
    window.resize(800, 600)
    window.show()
    window.command_line_edit.setFocus()    
    
    should_exit = False
    while not should_exit:
        app.processEvents()
        should_exit = game_controller.update()

    sys.exit(app.exec())