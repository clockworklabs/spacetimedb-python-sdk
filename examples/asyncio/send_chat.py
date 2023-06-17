""" Send chat example script for SpacetimeDB Python SDK

This script will connect to the basic_chat module and send a chat to the server from the command line
argument you provide then exits.

This pattern is useful for testing reducers on your SpacetimeDB module.

"""

import asyncio

import sys
sys.path.insert(0, "../../")

from spacetimedb_python_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient

import autogen

async def main():
    try:
        client = SpacetimeDBAsyncClient(autogen)

        # Connect to the server.
        (auth_token, identity) = await client.connect(None, "localhost:3000", "asyncio", False, ["SELECT * FROM User", "SELECT * FROM UserChat"])

        print(f"Connected with identity {identity}")

        # Call the reducers.
        result = await client.call_reducer("create_user")
        print(f"Reducer result: {result}")

        result = await client.call_reducer("user_chat", sys.argv[1])

        print(f"Reducer result: {result}")
        await client.close()
    except Exception as e:                
        await client.close()      
        raise e  

if __name__ == "__main__":
    asyncio.run(main())
