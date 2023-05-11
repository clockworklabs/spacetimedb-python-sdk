import os
import sys
import signal

# Get the parent directory of the current file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the system path
print(parent_dir)
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
    game_controller.play()
