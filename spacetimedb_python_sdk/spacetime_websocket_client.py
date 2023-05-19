import websocket
import threading
import base64
import binascii


class WebSocketClient:
    def __init__(self, protocol, on_connect=None, on_close=None, on_error=None, on_message=None):
        self._on_connect = on_connect
        self._on_close = on_close
        self._on_error = on_error
        self._on_message = on_message

        self.protocol = protocol
        self.ws = None
        self.message_thread = None
        self.host = None
        self.name_or_address = None
        self.is_connected = False

    def connect(self, auth, host, name_or_address, ssl_enabled):
        protocol = "wss" if ssl_enabled else "ws"
        url = f"{protocol}://{host}/database/subscribe?name_or_address={name_or_address}"

        self.host = host
        self.name_or_address = name_or_address

        ws_header = None
        if auth:
            token_bytes = bytes(f"token:{auth}", "utf-8")
            base64_str = base64.b64encode(token_bytes).decode("utf-8")
            headers = {
                "Authorization": f"Basic {base64_str}",
            }
        else:
            headers = None

        self.ws = websocket.WebSocketApp(url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close, 
                                         header=headers, 
                                         subprotocols=[self.protocol])

        self.message_thread = threading.Thread(target=self.ws.run_forever)
        self.message_thread.start()

    def decode_hex_string(hex_string):
        try:
            return binascii.unhexlify(hex_string)
        except binascii.Error:
            return None

    def send(self, data):
        if not self.is_connected:
            print("[send] Not connected")

        self.ws.send(data)

    def close(self):
        self.ws.close()

    def on_open(self, ws):
        self.is_connected = True
        if self._on_connect:
            self._on_connect()

    def on_message(self, ws, message):
        # Process incoming message on a separate thread here
        t = threading.Thread(target=self.process_message, args=(message,))
        t.start()

    def process_message(self, message):
        if self._on_message:
            self._on_message(message)
        pass

    def on_error(self, ws, error):
        if self._on_error:
            self._on_error(error)

    def on_close(self, ws, status_code, close_msg):
        if self._on_close:
            self._on_close(close_msg)
