import keyboard
import time
from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient

import spacetime_types
from spacetime_types.user_chat import UserChat
from spacetime_types.user_chat_reducer import user_chat


def on_connect():
    print("Connected.")
    SpacetimeDBClient.instance.subscribe(
        ["SELECT * FROM User", "SELECT * FROM UserChat"]
    )


SpacetimeDBClient.init(
    auth_token=None,
    host="localhost:3000",
    address_or_name="MySpacetimeDBProject",
    ssl_enabled=False,
    autogen_package=spacetime_types,
    on_connect=on_connect,
)

UserChat.register_row_update(lambda caller, old_value, new_value: print(new_value.chat))

try:
    while True:
        SpacetimeDBClient.instance.update()
        time.sleep(1 / 60)
        if keyboard.is_pressed(" "):
            user_chat(input(">")[1:])
except KeyboardInterrupt:
    SpacetimeDBClient.instance.close()
    exit(0)
