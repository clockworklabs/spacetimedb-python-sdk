import asyncio
from multiprocessing import Queue
import threading

from spacetimedb_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient
import spacetimedb_sdk.local_config as local_config

import autogen
from autogen import user_message
from autogen import add_message_reducer
from autogen import delete_message_reducer

connected = False
input_queue = Queue()

def print_menu():
    print("1. Read messages")
    print("2. Send a message")
    print("3. Delete a message")
    print("4. Quit")

def input_loop():
    global input_queue

    while(True):
        choice = input()
        if choice == "1":
            input_queue.put((choice,None))    
        elif choice == "2":
            message = input("Enter message: ")
            input_queue.put((choice, message))
        elif choice == "3":
            message_id = input("Enter message id: ")
            input_queue.put((choice, int(message_id)))
        elif choice == "4":
            break        
        else:
            print("Invalid choice")

def run_client(spacetime_client):
    local_config.init(".spacetimedb-python-quickstart")
    asyncio.run(
        spacetime_client.run(
            local_config.get_string("auth_token"), "localhost:3000", "quickstart", False, on_connect, ["SELECT * FROM UserMessage"]
        )
    )

if __name__ == "__main__":
    spacetime_client = SpacetimeDBAsyncClient(autogen)

    def on_subscription_applied():
        global connected

        print(f"\nSYSTEM: Connected.")
        print_menu()

    spacetime_client.client.register_on_subscription_applied(on_subscription_applied)

    def check_commands():
        global input_queue

        if not input_queue.empty():
            choice = input_queue.get()
            if choice[0] == "1":
                print("\nID: Message")
                for message in user_message.UserMessage.iter():
                    print(f"{message.message_entity_id}: {message.message}")
                print("\n")
                print_menu()
            elif choice[0] == "2":
                add_message_reducer.add_message(choice[1])
                print("Request sent.")
                print_menu()
            elif choice[0] == "3":
                delete_message_reducer.delete_message(choice[1])
                print("Request sent.")
                print_menu()

        spacetime_client.schedule_event(0.1, check_commands)

    spacetime_client.schedule_event(0.1, check_commands)

    def on_connect(auth_token, identity):        
        local_config.set_string("auth_token", auth_token)    

    thread = threading.Thread(target=run_client, args=(spacetime_client,))
    thread.start()

    input_loop()    

    spacetime_client.force_close()    
    thread.join()