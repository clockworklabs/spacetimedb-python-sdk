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

    current_future = None
    is_closing = False
    identity = None          

    scheduled_events = []
    scheduled_event_task = None

    def __init__(self, autogen_package):
        self.client = SpacetimeDBClient(autogen_package)

    def schedule_event(self, delay_secs, callback, *args):
        # convert the delay to a datetime
        fire_time = datetime.now() + timedelta(seconds=delay_secs)
        scheduled_event = SpacetimeDBScheduledEvent(fire_time, callback, args)

        # if we are listening for events and this event is sooner than the next event, cancel the current event and create a new one
        if self.current_future is not None and not self.current_future.done():
            # if we have an event scheduled and this one is sooner, cancel the current event
            if(self.scheduled_event_task is not None and self.scheduled_events[0].fire_time > fire_time):
                self.scheduled_event_task.cancel()

            # schedule our new one    
            self._create_scheduled_event_task(scheduled_event)
        
        self.scheduled_events.append(scheduled_event)

        # sort scheduled events in order of fire time ascending
        self.scheduled_events.sort(key=lambda x: x.fire_time)

    def force_close(self):
        self.is_closing = True
        if self.current_future:
            self.current_future.set_result(("force_close",None))

    def _create_scheduled_event_task(self, scheduled_event):     
        def on_scheduled_event():
            self.current_future.set_result(("scheduled_event",scheduled_event))
            scheduled_event.callback(*scheduled_event.args)
            self.scheduled_events.remove(scheduled_event)                            
            self.scheduled_event_task = None

        async def wait_for_delay():
            await asyncio.sleep((scheduled_event.fire_time - datetime.now()).total_seconds())
            on_scheduled_event()
        self.scheduled_event_task = asyncio.create_task(wait_for_delay())

    async def run(self, auth_token, host, address_or_name, ssl_enabled, on_connect, subscription_queries=[]):
        identity_result = await self.connect(auth_token, host, address_or_name, ssl_enabled, subscription_queries)

        if on_connect is not None:
            on_connect(identity_result[0],identity_result[1])

        while not self.is_closing:
            await self.event()

        await self.close() 
    
    async def connect(self, auth_token, host, address_or_name, ssl_enabled, subscription_queries=[]):
        identity_future = asyncio.get_running_loop().create_future()

        def on_error(error):
            #print(f"Request Error: {error}")
            self.current_future.set_exception(SpacetimeDBException(error))
        
        def on_disconnect(close_msg):
            if self.is_closing:
                self.current_future.set_result(close_msg)
            else:
                #print(f"Disconnected: {close_msg}")
                self.current_future.set_exception(SpacetimeDBException(close_msg))

        def on_identity_received(auth_token, identity):
            #print(f"Identity Recieved")
            self.identity = identity            
            self.client.subscribe(subscription_queries)
            identity_future.set_result((auth_token, identity))

        #print("Connecting...")
        self.current_future = identity_future
        self.client.connect(auth_token, host, address_or_name, ssl_enabled, on_connect=None, on_error=on_error, on_disconnect=on_disconnect, on_identity=on_identity_received)

        await self._wait_for_future(identity_future, self.request_timeout)

        return identity_future.result()

    async def call_reducer(self, reducer_name, *reducer_args):
        reducer_future = asyncio.get_running_loop().create_future()

        def on_reducer_result(event):
            if(event.reducer == reducer_name and event.caller_identity == self.identity):
                reducer_future.set_result(event)

        self.current_future = reducer_future
        self.client.register_on_event(on_reducer_result)
        self.client._reducer_call(reducer_name, *reducer_args)

        await self._wait_for_future(reducer_future, self.request_timeout)

        return reducer_future.result()
    
    # format is (time_to_fire, callback, args)
    scheduled_events = []

    async def event(self):
        event_future = asyncio.get_running_loop().create_future()

        def on_subscription_applied():
            event_future.set_result(("subscription_applied"))

        def on_event(event):
            event_future.set_result(("reducer_transaction",event))

        self.current_future = event_future
        self.client.register_on_event(on_event)
        self.client.register_on_subscription_applied(on_subscription_applied)

        if len(self.scheduled_events) > 0:
            self._create_scheduled_event_task(self.scheduled_events[0])

        await self._wait_for_future(event_future)

        self.current_future = None

        if self.scheduled_event_task is not None:
            self.scheduled_event_task.cancel()
            self.scheduled_event_task = None

        self.client.unregister_on_event(on_event)
        self.client.unregister_on_subscription_applied(on_subscription_applied)

        return event_future.result()
    
    async def close(self):
        close_future = asyncio.get_running_loop().create_future()

        self.is_closing = True
        self.current_future = close_future

        self.client.close()
        
        await self._wait_for_future(close_future, self.request_timeout)

        return close_future.result()

    async def _wait_for_future(self, future, timeout=None):
        time_spent = 0        
        
        while not future.done():
            self.client.update()
            await asyncio.sleep(0.1)  # Sleep for 100 ms.
            time_spent += 0.1
            if timeout is not None and time_spent > timeout:
                raise TimeoutError("Request timed out.")