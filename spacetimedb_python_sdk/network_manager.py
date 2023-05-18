from typing import List, Dict, Callable
from types import ModuleType

import json
import queue

from spacetimedb_python_sdk.spacetime_websocket_client import WebSocketClient
from spacetimedb_python_sdk.client_cache import ClientCache
from spacetimedb_python_sdk import spacetime_config

class DbEvent:
    """
    Represents a database event.

    Attributes:
        table_name (str): The name of the table associated with the event.
        row_pk (str): The primary key of the affected row.
        row_op (str): The operation performed on the row (e.g., "insert", "update", "delete").
        decoded_value (Any, optional): The decoded value of the affected row. Defaults to None.
    """
    def __init__(self, table_name, row_pk, row_op, decoded_value=None):
        self.table_name = table_name
        self.row_pk = row_pk
        self.row_op = row_op
        self.decoded_value = decoded_value


class _ClientApiMessage:
    """
    This class is intended for internal use only and should not be used externally.
    """
    def __init__(self, transaction_type):
        self.transaction_type = transaction_type
        self.events = []

    def append_event(self, event):
        self.events.append(event)


class _SubscriptionUpdateMessage(_ClientApiMessage):
    """
    This class is intended for internal use only and should not be used externally.
    """
    def __init__(self):
        super().__init__("SubscriptionUpdate")


class TransactionUpdateMessage(_ClientApiMessage):
    """
    Represents a transaction update message. Used in on_event callbacks.

    For more details, see `network_manager.NetworkManager.register_on_event`

    Attributes:
        caller_identity (str): The identity of the caller.
        status (str): The status of the transaction.
        message (str): A message associated with the transaction update.
        reducer (str): The reducer used for the transaction.
        args (dict): Additional arguments for the transaction.
        events (List[DbEvent]): List of DBEvents that were committed.
    """
    def __init__(self, caller_identity: str, status: str, message: str, reducer: str, args: Dict):
        super().__init__("TransactionUpdate")
        self.caller_identity = caller_identity
        self.status = status
        self.message = message
        self.reducer = reducer
        self.args = args


class NetworkManager:
    """
    The NetworkManager class is the primary interface for communication with the SpacetimeDB Module in the SDK, facilitating interaction with the database.
    """

    instance = None

    @classmethod
    def init(cls, host: str, address_or_name: str, ssl_enabled: bool, autogen_package: ModuleType, on_connect:Callable[[], None]=None, on_disconnect:Callable[[str], None]=None, on_error:Callable[[str], None]=None):
        """
        Create a network manager instance.

        Args:
            host (str): Hostname:port for SpacetimeDB connection
            address_or_name (str): The name or address of the database to connect to
            autogen_package (ModuleType): Python package where SpaceTimeDB module generated files are located.            
            on_connect (Callable[[], None], optional): Optional callback called when a connection is made to the SpaceTimeDB module.
            on_disconnect (Callable[[str], None], optional): Optional callback called when the Python client is disconnected from the SpaceTimeDB module. The argument is the close message.
            on_error (Callable[[str], None], optional): Optional callback called when the Python client connection encounters an error. The argument is the error message.

        Example:
            NetworkManager.init(autogen, on_connect=self.on_connect)
        """
        cls.instance = NetworkManager(host, address_or_name, ssl_enabled, autogen_package, on_connect, on_disconnect, on_error)
    
    # Do not call this directly. Use init to instantiate the instance.    
    def __init__(self, host, address_or_name, ssl_enabled, autogen_package, on_connect, on_disconnect, on_error):
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_error = on_error

        self._row_update_callbacks = {}
        self._reducer_callbacks = {}
        self._on_transaction_callback = []
        self._on_event = []

        self.identity = None

        ClientCache.init(autogen_package)
        self.message_queue = queue.Queue()

        self.processed_message_queue = queue.Queue()

        auth = spacetime_config.get_string("auth")
        self.wsc = WebSocketClient(
            "v1.text.spacetimedb", on_connect=on_connect, on_message=self._on_message
        )
        self.wsc.connect(
            auth,
            host,
            address_or_name,
            ssl_enabled,
        )

    def update(self):
        """
        Process incoming messages from the SpaceTimeDB module.

        This function needs to be called on a regular frequency to handle and process incoming messages
        from the SpaceTimeDB module. It ensures that the client stays synchronized with the module and
        processes any updates or notifications received.

        Notes:
            - Calling this function allows the client to receive and handle new messages from the module.
            - It's important to ensure that this function is called frequently enough to maintain synchronization
            with the module and avoid missing important updates.

        Example:
            NetworkManager.init(autogen, on_connect=self.on_connect)
            while True:
                NetworkManager.instance.update()  # Call the update function in a loop to process incoming messages
                # Additional logic or code can be added here
        """
        self._do_update()

    def close(self):
        """
        Close the WebSocket connection.

        This function closes the WebSocket connection to the SpaceTimeDB module.

        Notes:
            - This needs to be called when exiting the application to terminate the websocket threads.

        Example:
            NetworkManager.instance.close()
        """
        self.wsc.close()

    def subscribe(self, queries: List[str]):
        """
        Subscribe to receive data and transaction updates for the provided queries.

        This function sends a subscription request to the SpaceTimeDB module, indicating that the client
        wants to receive data and transaction updates related to the specified queries.

        Args:
            queries (List[str]): A list of queries to subscribe to. Each query is a string representing
                an sql formatted query statement.

        Example:
            queries = ["SELECT * FROM table1", "SELECT * FROM table2 WHERE col2 = 0"]
            NetworkManager.instance.subscribe(queries)
        """
        json_data = json.dumps(queries)
        self.wsc.send(
            bytes(f'{{"subscribe": {{ "query_strings": {json_data}}}}}', "ascii")
        )

    def register_on_transaction(self, callback: Callable[[], None]):
        """
        Register a callback function to be executed on each transaction.

        Args:
            callback (Callable[[], None]): A callback function that will be invoked on each transaction.
                The callback function should not accept any arguments and should not return any value.

        Example:
            def transaction_callback():
                # Code to be executed on each transaction

            NetworkManager.instance.register_on_transaction(transaction_callback)
        """
        if self._on_transaction_callback is None:
            self._on_transaction_callback = []

        self._on_transaction_callback.append(callback)

    def register_on_event(self, callback: Callable[[TransactionUpdateMessage], None]):
        """
        Register a callback function to handle transaction update events.

        This function registers a callback function that will be called when a reducer modifies a table
        matching any of the subscribed queries or if a reducer called by this Python client encounters a failure.

        Args:
            callback (Callable[[TransactionUpdateMessage], None]):
                A callback function that takes a single argument of type `TransactionUpdateMessage`.
                This function will be invoked with a `TransactionUpdateMessage` instance containing information
                about the transaction update event.        

        Example:
            def handle_event(transaction_update):
                # Code to handle the transaction update event

            NetworkManager.instance.register_on_event(handle_event)
        """
        if self._on_event is None:
            self._on_event = []

        self._on_event.append(callback)

    def _register_row_update(self, table_name: str, callback: Callable[[str,object,object], None]):
        if table_name not in self._row_update_callbacks:
            self._row_update_callbacks[table_name] = []

        self._row_update_callbacks[table_name].append(callback)

    def _register_reducer(self, reducer_name, callback):
        if reducer_name not in self._reducer_callbacks:
            self._reducer_callbacks[reducer_name] = []

        self._reducer_callbacks[reducer_name].append(callback)

    def _reducer_call(self, reducer, *args):
        if not self.wsc.is_connected:
            print("[reducer_call] Not connected")        

        message = {
            "fn": reducer,
            "args": args,
        }

        json_data = json.dumps(message)
        self.wsc.send(bytes(f'{{"call": {json_data}}}', "ascii"))    

    def _on_message(self, data):
        message = json.loads(data)
        if "IdentityToken" in message:
            # is this safe to do in the message thread?
            self.identity = bytes.fromhex(message["IdentityToken"]["identity"])
            spacetime_config.set_string("auth", message["IdentityToken"]["token"])
        elif "SubscriptionUpdate" in message or "TransactionUpdate" in message:
            clientapi_message = None
            table_updates = None
            if "SubscriptionUpdate" in message:
                clientapi_message = _SubscriptionUpdateMessage()
                table_updates = message["SubscriptionUpdate"]["table_updates"]
            if "TransactionUpdate" in message:
                spacetime_message = message["TransactionUpdate"]
                # DAB Todo: We need reducer codegen to parse the args
                clientapi_message = TransactionUpdateMessage(
                    spacetime_message["event"]["caller_identity"],
                    spacetime_message["event"]["status"],
                    spacetime_message["event"]["message"],
                    spacetime_message["event"]["function_call"]["reducer"],
                    json.loads(spacetime_message["event"]["function_call"]["args"]),
                )
                table_updates = message["TransactionUpdate"]["subscription_update"][
                    "table_updates"
                ]

            for table_update in table_updates:
                table_name = table_update["table_name"]
                for table_row_op in table_update["table_row_operations"]:
                    row_op = table_row_op["op"]
                    if row_op == "insert":
                        decoded_value = ClientCache.instance.decode(
                            table_name, table_row_op["row"]
                        )
                        clientapi_message.append_event(
                            DbEvent(
                                table_name,
                                table_row_op["row_pk"],
                                row_op,
                                decoded_value,
                            )
                        )
                    if row_op == "delete":
                        clientapi_message.append_event(
                            DbEvent(table_name, table_row_op["row_pk"], row_op)
                        )

            self.message_queue.put(clientapi_message)

    def _do_update(self):
        while not self.message_queue.empty():
            next_message = self.message_queue.get()
            
            # apply all the event state before calling callbacks
            for db_event in next_message.events:
                # get the old value for sending callbacks
                db_event.old_value = ClientCache.instance.get_entry(
                    db_event.table_name, db_event.row_pk
                )

                if db_event.row_op == "insert":
                    ClientCache.instance.set_entry_decoded(
                        db_event.table_name, db_event.row_pk, db_event.decoded_value
                    )
                elif db_event.row_op == "delete":
                    ClientCache.instance.delete_entry(db_event.table_name, db_event.row_pk)

            for db_event in next_message.events:
                # call row update callback
                if db_event.table_name in self._row_update_callbacks:
                    for row_update_callback in self._row_update_callbacks[db_event.table_name]:
                        row_update_callback(
                            db_event.row_op,
                            db_event.old_value,
                            db_event.decoded_value,
                        )

            if next_message.transaction_type == "SubscriptionUpdate" or next_message.transaction_type == "TransactionUpdate":
                # call ontransaction callback
                for on_transaction_callback in self._on_transaction_callback:
                    on_transaction_callback()

            if next_message.transaction_type == "TransactionUpdate":
                # call on event callback
                for event_callback in self._on_event:
                    event_callback(next_message)

                # call reducer callback
                if next_message.reducer in self._reducer_callbacks:
                    decode_func = ClientCache.instance.reducer_cache[next_message.reducer]
                    for reducer_callback in self._reducer_callbacks[next_message.reducer]:
                        reducer_callback(
                            bytes.fromhex(next_message.caller_identity),
                            next_message.status,
                            next_message.message,
                            *decode_func(next_message.args)
                         )
                
