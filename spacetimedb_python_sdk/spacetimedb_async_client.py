# Known issues: If two events are processed in the same frame it throws an exception

import asyncio
from datetime import timedelta
from datetime import datetime
import traceback

from spacetimedb_python_sdk.spacetimedb_client import SpacetimeDBClient

class SpacetimeDBException(Exception):
    pass

class SpacetimeDBScheduledEvent():
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
        self.client = SpacetimeDBClient(autogen_package)
        self.prescheduled_events = []
        self.event_queue = None    

    def schedule_event(self, delay_secs, callback, *args):
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
                await asyncio.sleep((scheduled_event.fire_time - datetime.now()).total_seconds())
                on_scheduled_event()
            
            asyncio.create_task(wait_for_delay())
        
    def force_close(self):
        self.is_closing = True        

        # TODO Cancel all scheduled event tasks

        self.event_queue.put_nowait(("force_close", None))

    async def run(self, auth_token, host, address_or_name, ssl_enabled, on_connect, subscription_queries=[]):
        if not self.event_queue:
            self._on_async_loop_start()

        identity_result = await self.connect(auth_token, host, address_or_name, ssl_enabled, subscription_queries)

        if on_connect is not None:
            on_connect(identity_result[0],identity_result[1])

        def on_subscription_applied():
            self.event_queue.put_nowait(("subscription_applied", None))

        def on_event(event):
            self.event_queue.put_nowait(("reducer_transaction", event))

        self.client.register_on_event(on_event)
        self.client.register_on_subscription_applied(on_subscription_applied)

        while not self.is_closing:
            event, payload = await self._event()
            if event == 'disconnected':
                if self.is_closing:
                    return payload
                else:
                    raise payload
            elif event == 'error':
                raise payload
            elif event == 'force_close':
                break            

        await self.close() 

    async def connect(self, auth_token, host, address_or_name, ssl_enabled, subscription_queries=[]):
        if not self.event_queue:
            self._on_async_loop_start()

        def on_error(error):
            self.event_queue.put_nowait(('error', SpacetimeDBException(error)))

        def on_disconnect(close_msg):
            if self.is_closing:
                self.event_queue.put_nowait(('disconnected', close_msg))
            else:
                self.event_queue.put_nowait(('error', SpacetimeDBException(close_msg)))

        def on_identity_received(auth_token, identity):
            self.identity = identity            
            self.client.subscribe(subscription_queries)
            self.event_queue.put_nowait(('connected', (auth_token, identity)))

        self.client.connect(auth_token, host, address_or_name, ssl_enabled, on_connect=None, 
                            on_error=on_error, 
                            on_disconnect=on_disconnect, 
                            on_identity=on_identity_received)

        while True:
            event, payload = await self._event()
            if event == 'error':
                raise payload
            elif event == 'connected':
                self.is_connected = True
                return payload

    async def call_reducer(self, reducer_name, *reducer_args):
        def on_reducer_result(event):
            if(event.reducer == reducer_name and event.caller_identity == self.identity):
                self.event_queue.put_nowait(("reducer_result", event))

        self.client.register_on_event(on_reducer_result)

        timeout_task = asyncio.create_task(self._timeout_task(self.request_timeout))

        self.client._reducer_call(reducer_name, *reducer_args)

        while True:
            event, payload = await self._event()
            if event == 'reducer_result':
                if not timeout_task.done():
                    timeout_task.cancel()
                return payload
            elif event == "timeout":
                raise SpacetimeDBException("Reducer call timed out.")

    async def close(self):
        self.is_closing = True

        timeout_task = asyncio.create_task(self._timeout_task(self.request_timeout))

        self.client.close()
        
        while True:
            event, payload = await self._event()
            if event == 'disconnected':
                if not timeout_task.done():
                    timeout_task.cancel()
                break
            elif event == "timeout":
                raise SpacetimeDBException("Close time out.")

    def _on_async_loop_start(self):
        self.event_queue = asyncio.Queue()
        for event in self.prescheduled_events:
            self.schedule_event(event[0],event[1],*event[2])    

    async def _timeout_task(self, timeout):
        await asyncio.sleep(timeout)
        self.event_queue.put_nowait(('timeout',))

    async def _event(self):
        update_task = asyncio.create_task(self._periodic_update())
        try:
            result = await self.event_queue.get()
            update_task.cancel()
            return result
        except Exception as e:
            update_task.cancel()
            raise e        

    async def _periodic_update(self):
        while True:
            self.client.update()
            await asyncio.sleep(0.1)
