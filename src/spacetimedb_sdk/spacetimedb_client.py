from typing import List, Dict, Callable
from types import ModuleType

import json
import queue

from spacetimedb_sdk.spacetime_websocket_client import WebSocketClient
from spacetimedb_sdk.client_cache import ClientCache


class Identity:
    """
    Represents a user identity. This is a wrapper around the Uint8Array that is recieved from SpacetimeDB.

    Attributes:
        data (bytes): The identity data.
    """

    def __init__(self, data):
        self.data = bytes(data)  # Ensure data is always bytes

    @staticmethod
    def from_string(string):
        """
        Returns an Identity object with the data attribute set to the byte representation of the input string.

        Args:
            string (str): The input string.

        Returns:
            Identity: The Identity object.
        """
        return Identity(bytes.fromhex(string))

    @staticmethod
    def from_bytes(data):
        """
        Returns an Identity object with the data attribute set to the input bytes.

        Args:
            data (bytes): The input bytes.

        Returns:
            Identity: The Identity object.
        """
        return Identity(data)

    # override to_string
    def __str__(self):
        return self.data.hex()

    # override = operator
    def __eq__(self, other):
        return isinstance(other, Identity) and self.data == other.data

    def __hash__(self):
        return hash(self.data)


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
        self.events = {}

    def append_event(self, table_name, event):
        self.events.setdefault(table_name, []).append(event)


class _IdentityReceivedMessage(_ClientApiMessage):
    """
    This class is intended for internal use only and should not be used externally.
    """

    def __init__(self, auth_token, identity):
        super().__init__("IdentityReceived")

        self.auth_token = auth_token
        self.identity = identity


class _SubscriptionUpdateMessage(_ClientApiMessage):
    """
    This class is intended for internal use only and should not be used externally.
    """

    def __init__(self):
        super().__init__("SubscriptionUpdate")


class ReducerEvent:
    def __init__(self, caller_identity, reducer_name, status, message, args):
        self.caller_identity = caller_identity
        self.reducer_name = reducer_name
        self.status = status
        self.message = message
        self.args = args


class TransactionUpdateMessage(_ClientApiMessage):
    """
    Represents a transaction update message. Used in on_event callbacks.

    For more details, see `spacetimedb_client.SpacetimeDBClient.register_on_event`

    Attributes:
        caller_identity (str): The identity of the caller.
        status (str): The status of the transaction.
        message (str): A message associated with the transaction update.
        reducer (str): The reducer used for the transaction.
        args (dict): Additional arguments for the transaction.
        events (List[DbEvent]): List of DBEvents that were committed.
    """

    def __init__(
        self,
        caller_identity: Identity,
        status: str,
        message: str,
        reducer_name: str,
        args: Dict,
    ):
        super().__init__("TransactionUpdate")
        self.reducer_event = ReducerEvent(
            caller_identity, reducer_name, status, message, args
        )


class SpacetimeDBClient:
    """
    The SpacetimeDBClient class is the primary interface for communication with the SpacetimeDB Module in the SDK, facilitating interaction with the database.
    """

    instance = None
    client_cache = None

    @classmethod
    def init(
        cls,
        auth_token: str,
        host: str,
        address_or_name: str,
        ssl_enabled: bool,
        autogen_package: ModuleType,
        on_connect: Callable[[], None] = None,
        on_disconnect: Callable[[str], None] = None,
        on_identity: Callable[[str, Identity], None] = None,
        on_error: Callable[[str], None] = None,
    ):
        """
        Create a network manager instance.

        Args:
            auth_token (str): This is the token generated by SpacetimeDB that matches the user's identity. If None, token will be generated
            host (str): Hostname:port for SpacetimeDB connection
            address_or_name (str): The name or address of the database to connect to
            autogen_package (ModuleType): Python package where SpacetimeDB module generated files are located.
            on_connect (Callable[[], None], optional): Optional callback called when a connection is made to the SpacetimeDB module.
            on_disconnect (Callable[[str], None], optional): Optional callback called when the Python client is disconnected from the SpacetimeDB module. The argument is the close message.
            on_identity (Callable[[str, bytes], None], optional): Called when the user identity is recieved from SpacetimeDB. First argument is the auth token used to login in future sessions.
            on_error (Callable[[str], None], optional): Optional callback called when the Python client connection encounters an error. The argument is the error message.

        Example:
            SpacetimeDBClient.init(autogen, on_connect=self.on_connect)
        """
        client = SpacetimeDBClient(autogen_package)
        client.connect(
            auth_token,
            host,
            address_or_name,
            ssl_enabled,
            on_connect,
            on_disconnect,
            on_identity,
            on_error,
        )

    # Do not call this directly. Use init to instantiate the instance.
    def __init__(self, autogen_package):
        SpacetimeDBClient.instance = self

        self._row_update_callbacks = {}
        self._reducer_callbacks = {}
        self._on_subscription_applied = []
        self._on_event = []

        self.identity = None

        self.client_cache = ClientCache(autogen_package)
        self.message_queue = queue.Queue()

        self.processed_message_queue = queue.Queue()

    def connect(
        self,
        auth_token,
        host,
        address_or_name,
        ssl_enabled,
        on_connect,
        on_disconnect,
        on_identity,
        on_error,
    ):
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_identity = on_identity
        self._on_error = on_error

        self.wsc = WebSocketClient(
            "v1.text.spacetimedb",
            on_connect=on_connect,
            on_error=on_error,
            on_close=on_disconnect,
            on_message=self._on_message,
        )
        # print("CONNECTING " + host + " " + address_or_name)
        self.wsc.connect(
            auth_token,
            host,
            address_or_name,
            ssl_enabled,
        )

    def update(self):
        """
        Process all pending incoming messages from the SpacetimeDB module.

        NOTE: This function must be called on a regular interval to process incoming messages.

        Example:
            SpacetimeDBClient.init(autogen, on_connect=self.on_connect)
            while True:
                SpacetimeDBClient.instance.update()  # Call the update function in a loop to process incoming messages
                # Additional logic or code can be added here
        """
        self._do_update()

    def close(self):
        """
        Close the WebSocket connection.

        This function closes the WebSocket connection to the SpacetimeDB module.

        Notes:
            - This needs to be called when exiting the application to terminate the websocket threads.

        Example:
            SpacetimeDBClient.instance.close()
        """

        self.wsc.close()

    def subscribe(self, queries: List[str]):
        """
        Subscribe to receive data and transaction updates for the provided queries.

        This function sends a subscription request to the SpacetimeDB module, indicating that the client
        wants to receive data and transaction updates related to the specified queries.

        Args:
            queries (List[str]): A list of queries to subscribe to. Each query is a string representing
                an sql formatted query statement.

        Example:
            queries = ["SELECT * FROM table1", "SELECT * FROM table2 WHERE col2 = 0"]
            SpacetimeDBClient.instance.subscribe(queries)
        """
        json_data = json.dumps(queries)
        self.wsc.send(
            bytes(f'{{"subscribe": {{ "query_strings": {json_data}}}}}', "ascii")
        )

    def register_on_subscription_applied(self, callback: Callable[[], None]):
        """
        Register a callback function to be executed when the local cache is updated as a result of a change to the subscription queries.

        Args:
            callback (Callable[[], None]): A callback function that will be invoked on each subscription update.
                The callback function should not accept any arguments and should not return any value.

        Example:
            def subscription_callback():
                # Code to be executed on each subscription update

            SpacetimeDBClient.instance.register_on_subscription_applied(subscription_callback)
        """
        if self._on_subscription_applied is None:
            self._on_subscription_applied = []

        self._on_subscription_applied.append(callback)

    def unregister_on_subscription_applied(self, callback: Callable[[], None]):
        """
        Unregister a callback function from the subscription update event.

        Args:
            callback (Callable[[], None]): A callback function that was previously registered with the `register_on_subscription_applied` function.

        Example:
            def subscription_callback():
                # Code to be executed on each subscription update

            SpacetimeDBClient.instance.register_on_subscription_applied(subscription_callback)
            SpacetimeDBClient.instance.unregister_on_subscription_applied(subscription_callback)
        """
        if self._on_subscription_applied is not None:
            self._on_subscription_applied.remove(callback)

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

            SpacetimeDBClient.instance.register_on_event(handle_event)
        """
        if self._on_event is None:
            self._on_event = []

        self._on_event.append(callback)

    def unregister_on_event(self, callback: Callable[[TransactionUpdateMessage], None]):
        """
        Unregister a callback function that was previously registered using `register_on_event`.

        Args:
            callback (Callable[[TransactionUpdateMessage], None]): The callback function to unregister.

        Example:
            SpacetimeDBClient.instance.unregister_on_event(handle_event)
        """
        if self._on_event is not None:
            self._on_event.remove(callback)

    def _get_table_cache(self, table_name: str):
        return self.client_cache.get_table_cache(table_name)

    def _register_row_update(
        self,
        table_name: str,
        callback: Callable[[str, object, object, ReducerEvent], None],
    ):
        if table_name not in self._row_update_callbacks:
            self._row_update_callbacks[table_name] = []

        self._row_update_callbacks[table_name].append(callback)

    def _unregister_row_update(
        self,
        table_name: str,
        callback: Callable[[str, object, object, ReducerEvent], None],
    ):
        if table_name in self._row_update_callbacks:
            self._row_update_callbacks[table_name].remove(callback)

    def _register_reducer(self, reducer_name, callback):
        if reducer_name not in self._reducer_callbacks:
            self._reducer_callbacks[reducer_name] = []

        self._reducer_callbacks[reducer_name].append(callback)

    def _unregister_reducer(self, reducer_name, callback):
        if reducer_name in self._reducer_callbacks:
            self._reducer_callbacks[reducer_name].remove(callback)

    def _reducer_call(self, reducer, *args):
        if not self.wsc.is_connected:
            print("[reducer_call] Not connected")

        message = {
            "fn": reducer,
            "args": args,
        }

        json_data = json.dumps(message)
        # print("_reducer_call(JSON): " + json_data)
        self.wsc.send(bytes(f'{{"call": {json_data}}}', "ascii"))

    def _on_message(self, data):
        # print("_on_message data: " + data)
        message = json.loads(data)
        if "IdentityToken" in message:
            # is this safe to do in the message thread?
            token = message["IdentityToken"]["token"]
            identity = Identity.from_string(message["IdentityToken"]["identity"])
            self.message_queue.put(_IdentityReceivedMessage(token, identity))
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
                    Identity.from_string(spacetime_message["event"]["caller_identity"]),
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
                        decoded_value = self.client_cache.decode(
                            table_name, table_row_op["row"]
                        )
                        clientapi_message.append_event(
                            table_name,
                            DbEvent(
                                table_name,
                                table_row_op["row_pk"],
                                row_op,
                                decoded_value,
                            ),
                        )
                    if row_op == "delete":
                        clientapi_message.append_event(
                            table_name,
                            DbEvent(table_name, table_row_op["row_pk"], row_op),
                        )

            self.message_queue.put(clientapi_message)

    def _do_update(self):
        while not self.message_queue.empty():
            next_message = self.message_queue.get()

            if next_message.transaction_type == "IdentityReceived":
                self.identity = next_message.identity
                if self._on_identity:
                    self._on_identity(next_message.auth_token, self.identity)
            else:
                # print(f"next_message: {next_message.transaction_type}")
                # apply all the event state before calling callbacks
                for table_name, table_events in next_message.events.items():
                    # first retrieve the old values for all events
                    for db_event in table_events:
                        # get the old value for sending callbacks
                        db_event.old_value = self.client_cache.get_entry(
                            db_event.table_name, db_event.row_pk
                        )

                    # if this table has a primary key, find table updates by looking for matching insert/delete events
                    primary_key = getattr(
                        self.client_cache.get_table_cache(table_name).table_class,
                        "primary_key",
                        None,
                    )
                    # print(f"Primary key: {primary_key}")
                    if primary_key is not None:
                        primary_key_row_ops = {}

                        for db_event in table_events:
                            if db_event.row_op == "insert":
                                # NOTE: we have to do look up in actual data dict because primary_key is a property of the table class
                                primary_key_value = db_event.decoded_value.data[
                                    primary_key
                                ]
                            else:
                                primary_key_value = db_event.old_value.data[primary_key]

                            if primary_key_value in primary_key_row_ops:
                                other_db_event = primary_key_row_ops[primary_key_value]
                                if (
                                    db_event.row_op == "insert"
                                    and other_db_event.row_op == "delete"
                                ):
                                    # this is a row update so we need to replace the insert
                                    db_event.row_op = "update"
                                    db_event.old_pk = other_db_event.row_pk
                                    db_event.old_value = other_db_event.old_value
                                    primary_key_row_ops[primary_key_value] = db_event
                                elif (
                                    db_event.row_op == "delete"
                                    and other_db_event.row_op == "insert"
                                ):
                                    # the insert was the row update so just upgrade it to update
                                    primary_key_row_ops[
                                        primary_key_value
                                    ].row_op = "update"
                                    primary_key_row_ops[
                                        primary_key_value
                                    ].old_pk = db_event.row_pk
                                    primary_key_row_ops[
                                        primary_key_value
                                    ].old_value = db_event.old_value
                                else:
                                    print(
                                        f"Error: duplicate primary key {table_name}:{primary_key_value}"
                                    )
                            else:
                                primary_key_row_ops[primary_key_value] = db_event

                        table_events = primary_key_row_ops.values()
                        next_message.events[table_name] = table_events

                    # now we can apply the events to the cache
                    for db_event in table_events:
                        # print(f"db_event: {db_event.row_op} {table_name}")
                        if db_event.row_op == "insert" or db_event.row_op == "update":
                            # in the case of updates we need to delete the old entry
                            if db_event.row_op == "update":
                                self.client_cache.delete_entry(
                                    db_event.table_name, db_event.old_pk
                                )
                            self.client_cache.set_entry_decoded(
                                db_event.table_name,
                                db_event.row_pk,
                                db_event.decoded_value,
                            )
                        elif db_event.row_op == "delete":
                            self.client_cache.delete_entry(
                                db_event.table_name, db_event.row_pk
                            )

                # now that we have applied the state we can call the callbacks
                for table_events in next_message.events.values():
                    for db_event in table_events:
                        # call row update callback
                        if db_event.table_name in self._row_update_callbacks:
                            reducer_event = (
                                next_message.reducer_event
                                if next_message.transaction_type == "TransactionUpdate"
                                else None
                            )
                            for row_update_callback in self._row_update_callbacks[
                                db_event.table_name
                            ]:
                                row_update_callback(
                                    db_event.row_op,
                                    db_event.old_value,
                                    db_event.decoded_value,
                                    reducer_event,
                                )

                if next_message.transaction_type == "SubscriptionUpdate":
                    # call ontransaction callback
                    for on_subscription_applied in self._on_subscription_applied:
                        on_subscription_applied()

                if next_message.transaction_type == "TransactionUpdate":
                    # call on event callback
                    for event_callback in self._on_event:
                        event_callback(next_message)

                    # call reducer callback
                    reducer_event = next_message.reducer_event
                    if reducer_event.reducer_name in self._reducer_callbacks:
                        args = []
                        decode_func = self.client_cache.reducer_cache[
                            reducer_event.reducer_name
                        ]
                        if reducer_event.status == "committed":
                            args = decode_func(reducer_event.args)

                        for reducer_callback in self._reducer_callbacks[
                            reducer_event.reducer_name
                        ]:
                            reducer_callback(
                                reducer_event.caller_identity,
                                reducer_event.status,
                                reducer_event.message,
                                *args,
                            )
