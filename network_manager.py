from websocket_client import WebSocketClient
import spacetime_config
import json
import queue
from client_cache import ClientCache


class DbEvent:
    def __init__(self, table_name, row_pk, op, decoded_value=None):
        self.table_name = table_name
        self.row_pk = row_pk
        self.op = op
        self.decoded_value = decoded_value


class ClientApiMessage:
    def __init__(self, transaction_type):
        self.transaction_type = transaction_type
        self.events = []

    def append_event(self, event):
        self.events.append(event)


class SubscriptionUpdateMessage(ClientApiMessage):
    def __init__(self):
        super().__init__("SubscriptionUpdate")


class TransactionUpdateMessage(ClientApiMessage):
    def __init__(self, status, reducer, args):
        super().__init__("SubscriptionUpdate")
        self.status = status
        self.reducer = reducer
        self.args = args


class NetworkManager:
    def __init__(self, autogen_package, on_connect=None, on_disconnect=None, on_error=None):
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_error = on_error

        self._row_update_callbacks = {}
        self._reducer_callbacks = {}
        self._on_transaction_callback = None

        self.client_cache = ClientCache(autogen_package)
        self.message_queue = queue.Queue()

        self.processed_message_queue = queue.Queue()

        auth = spacetime_config.get_string("auth")
        self.wsc = WebSocketClient(
            "v1.text.spacetimedb", on_connect=on_connect, on_message=self.on_message)
        self.wsc.connect(auth, spacetime_config.get_string(
            "host"), spacetime_config.get_string("database"), False)

    def register_row_update(self, table_name, callback):
        if table_name not in self._row_update_callbacks:
            self._row_update_callbacks[table_name] = []

        self._row_update_callbacks[table_name].append(callback)

    def register_reducer(self, reducer_name, callback):
        if reducer_name not in self._reducer_callbacks:
            self._reducer_callbacks[reducer_name] = []

        self._reducer_callbacks[reducer_name].append(callback)

    def register_on_transaction(self, callback):
        if self._on_transaction_callback is None:
            self._on_transaction_callback = []

        self._on_transaction_callback.append(callback)

    def reducer_call(self, reducer, *args):
        if not self.wsc.is_connected:
            print("Not connected")

        message = {
            "fn": reducer,
            "args": args,
        }

        json_data = json.dumps(message)
        self.wsc.send(bytes(f"{{\"call\": {json_data}}}", "ascii"))

    def close(self):
        self.wsc.close()

    def subscribe(self, queries):
        json_data = json.dumps(queries)
        self.wsc.send(
            bytes(f"{{\"subscribe\": {{ \"query_strings\": {json_data}}}}}", "ascii"))

    # this is called from the message thread, only modifies the thread safe self.message_queue
    def on_message(self, data):
        message = json.loads(data)
        if 'IdentityToken' in message:
            # is this safe to do in the message thread?
            spacetime_config.set_string(
                "auth", message['IdentityToken']['token'])
        elif 'SubscriptionUpdate' in message or 'TransactionUpdate' in message:
            clientapi_message = None
            table_updates = None
            if 'SubscriptionUpdate' in message:
                clientapi_message = SubscriptionUpdateMessage()
                table_updates = message['SubscriptionUpdate']['table_updates']
            if 'TransactionUpdate' in message:
                clientapi_message = TransactionUpdateMessage()
                table_updates = message['TransactionUpdate']['subscription_update']['table_updates']

            for table_update in table_updates:
                table_name = table_update['table_name']
                for table_row_op in table_update['table_row_operations']:
                    row_op = table_row_op['op']
                    if row_op == "insert":
                        decoded_value = self.client_cache.decode(
                            table_name, table_row_op['row'])
                        clientapi_message.append_event(DbEvent(
                            table_name, table_row_op['row_pk'], row_op, decoded_value))
                    if row_op == "delete":
                        clientapi_message.append_event(
                            DbEvent(table_name, table_row_op['row_pk'], row_op))

            self.message_queue.put(clientapi_message)

    def update(self):
        while not self.message_queue.empty():
            next_message = self.message_queue.get()

            for db_event in next_message.events:
                # get the old value for sending callbacks
                old_value = self.client_cache.get_entry(
                    db_event.table_name, db_event.row_pk)

                if db_event.op == "insert":
                    self.client_cache.set_entry_decoded(
                        db_event.table_name, db_event.row_pk, db_event.decoded_value)
                elif db_event.op == "delete":
                    self.client_cache.delete_entry(
                        db_event.table_name, db_event.row_pk)
