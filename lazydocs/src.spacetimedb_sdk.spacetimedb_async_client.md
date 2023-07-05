<!-- markdownlint-disable -->

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `src.spacetimedb_sdk.spacetimedb_async_client`
SpacetimeDB Python SDK AsyncIO Client 

This module provides a client interface to your SpacetimeDB module using the asyncio library. Essentially, you create your client object, register callbacks, and then start the client using asyncio.run(). 

For details on how to use this module, see the documentation on the SpacetimeDB website and the examples in the examples/asyncio directory.  



---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBException`








---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBScheduledEvent`




<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBScheduledEvent.__init__`

```python
__init__(datetime, callback, args)
```









---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBAsyncClient`




<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.__init__`

```python
__init__(autogen_package)
```

Create a SpacetimeDBAsyncClient object 



**Attributes:**
 
 - <b>`autogen_package `</b>:  package folder created by running the generate command from the CLI    




---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.call_reducer`

```python
call_reducer(reducer_name, *reducer_args)
```

Call a reducer on the async loop. This function will not return until the reducer call completes. 

NOTE: DO NOT call this function if you are using the run() function. You should use the auto-generated reducer functions instead.  

Args:         reducer_name : name of the reducer to call  reducer_args (variable) : arguments to pass to the reducer             

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.close`

```python
close()
```

Close the client. This function will not return until the client is closed. 

NOTE: DO NOT call this function if you are using the run() function. It will close for you. 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.connect`

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

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.force_close`

```python
force_close()
```

Signal the client to stop processing events and close the connection to the server. 

This will cause the client to close even if there are scheduled events that have not fired yet. 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.run`

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

<a href="..\src\spacetimedb_sdk\spacetimedb_async_client.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBAsyncClient.schedule_event`

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

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
