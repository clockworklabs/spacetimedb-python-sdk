import asyncio

from spacetimedb_client import SpacetimeDBClient

class SpacetimeDBException(Exception):
    pass

class SpacetimeDBAsyncClient:
    request_timeout = 5

    current_future = None
    is_closing = False
    identity = None          

    def __init__(self, autogen_package):
        self.client = SpacetimeDBClient(autogen_package)

    async def run(self, auth_token, host, address_or_name, ssl_enabled, on_connect, subscription_queries=[]):
        identity_result = await self.connect(auth_token, host, address_or_name, ssl_enabled, subscription_queries)

        if on_connect is not None:
            on_connect(identity_result)

        while not self.is_closing:
            await self.event()    

        await self.close() 
    
    async def connect(self, auth_token, host, address_or_name, ssl_enabled, autogen_package, subscription_queries=[]):
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
            self.SpacetimeDBClient.subscribe(subscription_queries)
            identity_future.set_result((auth_token, identity))

        #print("Connecting...")
        self.current_future = identity_future
        self.SpacetimeDBClient = SpacetimeDBClient(auth_token, host, address_or_name, ssl_enabled, autogen_package, on_connect=None, on_error=on_error, on_disconnect=on_disconnect, on_identity=on_identity_received)

        await self._wait_for_future(identity_future)

        return identity_future.result()

    async def call_reducer(self, reducer_name, *reducer_args):
        reducer_future = asyncio.get_running_loop().create_future()

        def on_reducer_result(event):
            if(event.reducer == reducer_name and event.caller_identity == self.identity):
                reducer_future.set_result(event)

        self.current_future = reducer_future
        self.SpacetimeDBClient.register_on_event(on_reducer_result)
        self.SpacetimeDBClient._reducer_call(reducer_name, *reducer_args)

        await self._wait_for_future(reducer_future)

        return reducer_future.result()
    
    async def event(self):
        event_future = asyncio.get_running_loop().create_future()

        def on_subscription_applied():
            event_future.set_result("subscription_applied")

        def on_event(event):
            event_future.set_result("reducer_transaction",event)

        self.current_future = event_future
        self.SpacetimeDBClient.register_on_event(on_event)
        self.SpacetimeDBClient.register_on_subscription_applied(on_subscription_applied)

        await self._wait_for_future(event_future)

        self.SpacetimeDBClient.unregister_on_event(on_event)
        self.SpacetimeDBClient.unregister_on_subscription_applied(on_subscription_applied)

        return event_future.result()
    
    async def close(self):
        close_future = asyncio.get_running_loop().create_future()

        self.is_closing = True
        self.current_future = close_future

        self.SpacetimeDBClient.close()
        
        await self._wait_for_future(close_future)

        return close_future.result()

    async def _wait_for_future(self, future):
        time_spent = 0        
        
        while not future.done():
            self.SpacetimeDBClient.update()
            await asyncio.sleep(0.1)  # Sleep for 100 ms.
            time_spent += 0.1
            if time_spent > self.request_timeout:
                raise TimeoutError("Request timed out.")