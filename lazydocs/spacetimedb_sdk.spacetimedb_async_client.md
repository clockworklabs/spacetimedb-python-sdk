<!-- markdownlint-disable -->

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `spacetimedb_sdk.spacetimedb_async_client`
SpacetimeDB Python SDK AsyncIO Client 

This module provides a client interface to your SpacetimeDB module using the asyncio library. Essentially, you create your client object, register callbacks, and then start the client using asyncio.run(). 

For details on how to use this module, see the documentation on the SpacetimeDB website and the examples in the examples/asyncio directory.  



---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBException`








---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBScheduledEvent`




<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(datetime, callback, args)
```









---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBAsyncClient`




<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(autogen_package)
```

Create a SpacetimeDBAsyncClient object 



**Attributes:**
 
 - <b>`autogen_package `</b>:  package folder created by running the generate command from the CLI 




---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `call_reducer`

```python
call_reducer(reducer_name, *reducer_args)
```

Call a reducer on the async loop. This function will not return until the reducer call completes. 

NOTE: DO NOT call this function if you are using the run() function. You should use the auto-generated reducer functions instead. 



**Args:**
 
 - <b>`reducer_name `</b>:  name of the reducer to call 
 - <b>`reducer_args (variable) `</b>:  arguments to pass to the reducer 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L271"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close()
```

Close the client. This function will not return until the client is closed. 

NOTE: DO NOT call this function if you are using the run() function. It will close for you. 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `connect`

```python
connect(auth_token, host, address_or_name, ssl_enabled, subscription_queries=[])
```

Connect to the server. 

NOTE: DO NOT call this function if you are using the run() function. It will connect for you. 



**Args:**
 
 - <b>`auth_token `</b>:  authentication token to use when connecting to the server 
 - <b>`host `</b>:  host name or IP address of the server 
 - <b>`address_or_name `</b>:  address or name of the module to connect to 
 - <b>`ssl_enabled `</b>:  True to use SSL, False to not use SSL 
 - <b>`subscription_queries `</b>:  list of queries to subscribe to 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `force_close`

```python
force_close()
```

Signal the client to stop processing events and close the connection to the server. 

This will cause the client to close even if there are scheduled events that have not fired yet. 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `register_on_subscription_applied`

```python
register_on_subscription_applied(callback)
```

Register a callback function to be executed when the local cache is updated as a result of a change to the subscription queries. 



**Args:**
 
 - <b>`callback`</b> (Callable[[], None]):  A callback function that will be invoked on each subscription update.  The callback function should not accept any arguments and should not return any value. 



**Example:**
 def subscription_callback():  # Code to be executed on each subscription update 

spacetime_client.register_on_subscription_applied(subscription_callback) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    auth_token,
    host,
    address_or_name,
    ssl_enabled,
    on_connect,
    subscription_queries=[]
)
```

Run the client. This function will not return until the client is closed. 



**Args:**
 
 - <b>`auth_token `</b>:  authentication token to use when connecting to the server 
 - <b>`host `</b>:  host name or IP address of the server 
 - <b>`address_or_name `</b>:  address or name of the module to connect to 
 - <b>`ssl_enabled `</b>:  True to use SSL, False to not use SSL 
 - <b>`on_connect `</b>:  function to call when the client connects to the server 
 - <b>`subscription_queries `</b>:  list of queries to subscribe to 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `schedule_event`

```python
schedule_event(delay_secs, callback, *args)
```

Schedule an event to be fired after a delay 

To create a repeating event, call schedule_event() again from within the callback function. 



**Args:**
 
 - <b>`delay_secs `</b>:  number of seconds to wait before firing the event 
 - <b>`callback `</b>:  function to call when the event fires 
 - <b>`args`</b> (variable):  arguments to pass to the callback function 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `subscribe`

```python
subscribe(queries: List[str])
```

Subscribe to receive data and transaction updates for the provided queries. 

This function sends a subscription request to the SpacetimeDB module, indicating that the client wants to receive data and transaction updates related to the specified queries. 



**Args:**
 
 - <b>`queries`</b> (List[str]):  A list of queries to subscribe to. Each query is a string representing  an sql formatted query statement. 



**Example:**
 queries = ["SELECT * FROM table1", "SELECT * FROM table2 WHERE col2 = 0"] spacetime_client.subscribe(queries) 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
