import cmd
import asyncio

import sys
import threading
sys.path.insert(0, "../../")

from spacetimedb_python_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient

import autogen
from autogen import user_chat_reducer
from autogen import create_user_reducer

# The custom cmd.Cmd class.
class ChatCmd(cmd.Cmd):
    prompt = ""

    def do_quit(self, line: str) -> None:
        """Quits the program."""
        print("Quitting.")
        return True

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

def on_connect(auth_token,identity):
    global local_identity
    
    local_identity = identity
    print(f"\nSYSTEM: Connected.\n> ", end="")    
    chatCmd.prompt = "> "
    create_user_reducer.create_user()

def run_client():    
    asyncio.run(spacetime_client.run(None, "localhost:3000", "asyncio", False, on_connect, ["SELECT * FROM User", "SELECT * FROM UserChat"]))

if __name__ == "__main__":
    thread = threading.Thread(target=run_client)
    thread.start()
    chatCmd.cmdloop()    
    spacetime_client.force_close()
    thread.join()
