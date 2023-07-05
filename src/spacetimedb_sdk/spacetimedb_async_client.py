""" SpacetimeDB Python SDK AsyncIO Client

This module provides a client interface to your SpacetimeDB module using the asyncio library.
Essentially, you create your client object, register callbacks, and then start the client
using asyncio.run().

For details on how to use this module, see the documentation on the SpacetimeDB website and
the examples in the examples/asyncio directory. 

"""

import asyncio
from datetime import timedelta
from datetime import datetime
import traceback

from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient


class SpacetimeDBException(Exception):
    pass


class SpacetimeDBScheduledEvent:
    def __init__(self, datetime, callback, args):
        self.fire_time = datetime
        self.callback = callback
        self.args = args


class SpacetimeDBAsyncClient:
    request_timeout = 5

    is_connected = False
    is_closing = False
    identity = None

    def __init__(self, autogen_package):
        """
        Create a SpacetimeDBAsyncClient object

        Attributes:
            autogen_package : package folder created by running the generate command from the CLI

        """
        self.client = SpacetimeDBClient(autogen_package)
        self.prescheduled_events = []
        self.event_queue = None

    def schedule_event(self, delay_secs, callback, *args):
        """
        Schedule an event to be fired after a delay

        To create a repeating event, call schedule_event() again from within the callback function.

        Args:
            delay_secs : number of seconds to wait before firing the event
            callback : function to call when the event fires
            args (variable): arguments to pass to the callback function
        """

        # if this is called before we start the async loop, we need to store the event
        if self.event_queue is None:
            self.prescheduled_events.append((delay_secs, callback, args))
        else:
            # convert the delay to a datetime
            fire_time = datetime.now() + timedelta(seconds=delay_secs)
            scheduled_event = SpacetimeDBScheduledEvent(fire_time, callback, args)

            # create async task
            def on_scheduled_event():
                self.event_queue.put_nowait(("scheduled_event", scheduled_event))
                scheduled_event.callback(*scheduled_event.args)

            async def wait_for_delay():
                await asyncio.sleep(
                    (scheduled_event.fire_time - datetime.now()).total_seconds()
                )
                on_scheduled_event()

            asyncio.create_task(wait_for_delay())

    def force_close(self):
        """
        Signal the client to stop processing events and close the connection to the server.

        This will cause the client to close even if there are scheduled events that have not fired yet.
        """

        self.is_closing = True

        # TODO Cancel all scheduled event tasks

        self.event_queue.put_nowait(("force_close", None))

    async def run(
        self,
        auth_token,
        host,
        address_or_name,
        ssl_enabled,
        on_connect,
        subscription_queries=[],
    ):
        """
        Run the client. This function will not return until the client is closed.

        Args:
            auth_token : authentication token to use when connecting to the server
            host : host name or IP address of the server
            address_or_name : address or name of the module to connect to
            ssl_enabled : True to use SSL, False to not use SSL
            on_connect : function to call when the client connects to the server
            subscription_queries : list of queries to subscribe to
        """

        if not self.event_queue:
            self._on_async_loop_start()

        identity_result = await self.connect(
            auth_token, host, address_or_name, ssl_enabled, subscription_queries
        )

        if on_connect is not None:
            on_connect(identity_result[0], identity_result[1])

        def on_subscription_applied():
            self.event_queue.put_nowait(("subscription_applied", None))

        def on_event(event):
            self.event_queue.put_nowait(("reducer_transaction", event))

        self.client.register_on_event(on_event)
        self.client.register_on_subscription_applied(on_subscription_applied)

        while not self.is_closing:
            event, payload = await self._event()
            if event == "disconnected":
                if self.is_closing:
                    return payload
                else:
                    raise payload
            elif event == "error":
                raise payload
            elif event == "force_close":
                break

        await self.close()

    async def connect(
        self, auth_token, host, address_or_name, ssl_enabled, subscription_queries=[]
    ):
        """
        Connect to the server.

        NOTE: DO NOT call this function if you are using the run() function. It will connect for you.

        Args:
            auth_token : authentication token to use when connecting to the server
            host : host name or IP address of the server
            address_or_name : address or name of the module to connect to
            ssl_enabled : True to use SSL, False to not use SSL
            subscription_queries : list of queries to subscribe to
        """

        if not self.event_queue:
            self._on_async_loop_start()

        def on_error(error):
            self.event_queue.put_nowait(("error", SpacetimeDBException(error)))

        def on_disconnect(close_msg):
            if self.is_closing:
                self.event_queue.put_nowait(("disconnected", close_msg))
            else:
                self.event_queue.put_nowait(("error", SpacetimeDBException(close_msg)))

        def on_identity_received(auth_token, identity):
            self.identity = identity
            self.client.subscribe(subscription_queries)
            self.event_queue.put_nowait(("connected", (auth_token, identity)))

        self.client.connect(
            auth_token,
            host,
            address_or_name,
            ssl_enabled,
            on_connect=None,
            on_error=on_error,
            on_disconnect=on_disconnect,
            on_identity=on_identity_received,
        )

        while True:
            event, payload = await self._event()
            if event == "error":
                raise payload
            elif event == "connected":
                self.is_connected = True
                return payload

    async def call_reducer(self, reducer_name, *reducer_args):
        """
        Call a reducer on the async loop. This function will not return until the reducer call completes.

        NOTE: DO NOT call this function if you are using the run() function. You should use the
        auto-generated reducer functions instead.

        Args:
            reducer_name : name of the reducer to call
            reducer_args (variable) : arguments to pass to the reducer

        """

        def on_reducer_result(event):
            if event.reducer == reducer_name and event.caller_identity == self.identity:
                self.event_queue.put_nowait(("reducer_result", event))

        self.client.register_on_event(on_reducer_result)

        timeout_task = asyncio.create_task(self._timeout_task(self.request_timeout))

        self.client._reducer_call(reducer_name, *reducer_args)

        while True:
            event, payload = await self._event()
            if event == "reducer_result":
                if not timeout_task.done():
                    timeout_task.cancel()
                return payload
            elif event == "timeout":
                raise SpacetimeDBException("Reducer call timed out.")

    async def close(self):
        """
        Close the client. This function will not return until the client is closed.

        NOTE: DO NOT call this function if you are using the run() function. It will close for you.
        """
        self.is_closing = True

        timeout_task = asyncio.create_task(self._timeout_task(self.request_timeout))

        self.client.close()

        while True:
            event, payload = await self._event()
            if event == "disconnected":
                if not timeout_task.done():
                    timeout_task.cancel()
                break
            elif event == "timeout":
                raise SpacetimeDBException("Close time out.")

    def _on_async_loop_start(self):
        self.event_queue = asyncio.Queue()
        for event in self.prescheduled_events:
            self.schedule_event(event[0], event[1], *event[2])

    async def _timeout_task(self, timeout):
        await asyncio.sleep(timeout)
        self.event_queue.put_nowait(("timeout",))

    async def _event(self):
        update_task = asyncio.create_task(self._periodic_update())
        try:
            result = await self.event_queue.get()
            update_task.cancel()
            return result
        except Exception as e:
            update_task.cancel()
            print(f"Exception: {e}")
            raise e

    async def _periodic_update(self):
        while True:
            try:
                self.client.update()
            except Exception as e:
                print(f"Exception: {e}")
                self.event_queue.put_nowait(("error", e))
                return
            await asyncio.sleep(0.1)
