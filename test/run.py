
import os
import sys
import signal
import time
import autogen

client = None

# Get the parent directory of the current file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the system path
sys.path.append(parent_dir)

if 'NetworkManager' not in sys.modules:
    from network_manager import NetworkManager


def signal_handler(sig, frame):
    print("Received termination signal")
    client.close()
    # Add any cleanup or shutdown code here
    exit(0)


# Register the signal handler function for the SIGINT and SIGBREAK signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGBREAK, signal_handler)


def on_connect():
    client.subscribe(["SELECT * FROM Mobile", "SELECT * FROM Room"])
    client.reducer_call("add", "John")


if __name__ == "__main__":
    client = NetworkManager(autogen, on_connect=on_connect)

    while (True):
        time.sleep(1)
