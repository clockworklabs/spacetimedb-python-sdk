import cmd
import asyncio

import sys
import threading

sys.path.insert(0, "../../")

from spacetimedb_python_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient

import autogen
from autogen import user_chat_reducer
from autogen import create_user_reducer
from autogen import update_motd_reducer
from autogen.global_table import GlobalTable

# The custom cmd.Cmd class.
class ChatCmd(cmd.Cmd):
    prompt = ""

    def do_quit(self, line: str) -> None:
        """Quits the program."""
        print("Quitting.")
        return True

    def do_motd(self, line: str) -> None:
        update_motd_reducer.update_motd(line)

    def default(self, line: str) -> None:
        user_chat_reducer.user_chat(line)
        print(f"Self: {line}")

chatCmd = ChatCmd()

spacetime_client = SpacetimeDBAsyncClient(autogen)

local_identity = None

# print out remote chat to the console and reprompt
def on_remote_chat(caller: bytes, status: str, message: str, chat: str = None):
    global local_identity

    if caller != local_identity and status == "committed":
        print(f"\nRemote: {chat}\n{chatCmd.prompt}", end="")
        
user_chat_reducer.register_on_user_chat(on_remote_chat)

# print out motd when it changes
def on_global_table_row_update(row_op, old_value, new_value, reducer_event):
    if(row_op == "update"):
        print(f"New motd: {new_value.message_of_the_day}\n{chatCmd.prompt}", end="")

GlobalTable.register_row_update(on_global_table_row_update)

def on_subscription_applied():
    chatCmd.prompt = "> "

    print(f"\nSYSTEM: Connected.")    

    global_table = GlobalTable.filter_by_version(0)
    print(f"SYSTEM: {global_table.message_of_the_day}\n{chatCmd.prompt}", end="")
    
    create_user_reducer.create_user()

spacetime_client.client.register_on_subscription_applied(on_subscription_applied)

def on_connect(auth_token,identity):
    global local_identity
    
    local_identity = identity

def run_client(): 
    subscription_queries = [
        "SELECT * FROM GlobalTable",
        "SELECT * FROM User", 
        "SELECT * FROM UserChat" ]

    asyncio.run(spacetime_client.run(None, "localhost:3000", "asyncio", False, on_connect, subscription_queries))

if __name__ == "__main__":
    thread = threading.Thread(target=run_client)
    thread.start()
    chatCmd.cmdloop()    
    spacetime_client.force_close()
    thread.join()
