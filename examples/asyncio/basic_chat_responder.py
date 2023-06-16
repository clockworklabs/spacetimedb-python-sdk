""" Basic Chat Example Script for SpacetimeDB Python SDK

This script connects to our basic_chat module and listens for incoming chats. When a chat is received,
 it responds with a random response.

This pattern is useful for a completely event driven interface to your SpacetimeDB module where you
do not need control of the main loop.

"""

import asyncio
import random

import sys
sys.path.insert(0, "../../")

from spacetimedb_python_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient

import autogen
from autogen import create_user_reducer, user_chat_reducer


spacetime_client = SpacetimeDBAsyncClient(autogen)

local_identity = None

def on_connect(auth_token,identity):
    global local_identity
    
    local_identity = identity
    print(f"Connected with identity {identity}")    
    create_user_reducer.create_user()

responses = [
    "That's very interesting! Can you tell me more about that?",
    "I see. Do you have any specific questions about this topic?",
    "Thank you for sharing that. How does it affect you personally?",
    "I appreciate your perspective. Do you have any further insights on this matter?",
    "That's a great point. What led you to think about this?"
]

# when someone else says something, respond with a random response
def on_remote_chat(caller: bytes, status: str, message: str, chat: str = None):
    global local_identity

    if caller != local_identity:
        print(f"Chat from {caller}: {chat}")
        user_chat_reducer.user_chat(responses[random.randint(0, len(responses) - 1)])

user_chat_reducer.register_on_user_chat(on_remote_chat)

# every 5 seconds send a message "Hello?"
def send_message(msg):
    print("Sending message!! " + str(msg))
    user_chat_reducer.user_chat(msg)
    spacetime_client.schedule_event(5,send_message,"Hello?")

spacetime_client.schedule_event(5,send_message,"Hello?")

if __name__ == "__main__":
    asyncio.run(spacetime_client.run(None, "localhost:3000", "asyncio", False, on_connect, ["SELECT * FROM User", "SELECT * FROM UserChat"]))
