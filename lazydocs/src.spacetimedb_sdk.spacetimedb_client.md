<!-- markdownlint-disable -->

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `src.spacetimedb_sdk.spacetimedb_client`






---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DbEvent`
Represents a database event. 



**Attributes:**
 
 - <b>`table_name`</b> (str):  The name of the table associated with the event. 
 - <b>`row_pk`</b> (str):  The primary key of the affected row. 
 - <b>`row_op`</b> (str):  The operation performed on the row (e.g., "insert", "update", "delete"). 
 - <b>`decoded_value`</b> (Any, optional):  The decoded value of the affected row. Defaults to None. 

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `DbEvent.__init__`

```python
__init__(table_name, row_pk, row_op, decoded_value=None)
```









---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ReducerEvent`




<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ReducerEvent.__init__`

```python
__init__(caller_identity, reducer_name, status, message, args)
```









---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TransactionUpdateMessage`
Represents a transaction update message. Used in on_event callbacks. 

For more details, see `spacetimedb_client.SpacetimeDBClient.register_on_event` 



**Attributes:**
 
 - <b>`caller_identity`</b> (str):  The identity of the caller. 
 - <b>`status`</b> (str):  The status of the transaction. 
 - <b>`message`</b> (str):  A message associated with the transaction update. 
 - <b>`reducer`</b> (str):  The reducer used for the transaction. 
 - <b>`args`</b> (dict):  Additional arguments for the transaction. 
 - <b>`events`</b> (List[DbEvent]):  List of DBEvents that were committed. 

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `TransactionUpdateMessage.__init__`

```python
__init__(
    caller_identity: str,
    status: str,
    message: str,
    reducer_name: str,
    args: Dict
)
```








---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `TransactionUpdateMessage.append_event`

```python
append_event(table_name, event)
```






---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SpacetimeDBClient`
The SpacetimeDBClient class is the primary interface for communication with the SpacetimeDB Module in the SDK, facilitating interaction with the database. 

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.__init__`

```python
__init__(autogen_package)
```








---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.close`

```python
close()
```

Close the WebSocket connection. 

This function closes the WebSocket connection to the SpacetimeDB module. 



**Notes:**

> - This needs to be called when exiting the application to terminate the websocket threads. 
>

**Example:**
  SpacetimeDBClient.instance.close() 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.connect`

```python
connect(
    auth_token,
    host,
    address_or_name,
    ssl_enabled,
    on_connect,
    on_disconnect,
    on_identity,
    on_error
)
```





---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `SpacetimeDBClient.init`

```python
init(
    auth_token: str,
    host: str,
    address_or_name: str,
    ssl_enabled: bool,
    autogen_package: module,
    on_connect: Callable[[], NoneType] = None,
    on_disconnect: Callable[[str], NoneType] = None,
    on_identity: Callable[[bytes], NoneType] = None,
    on_error: Callable[[str], NoneType] = None
)
```

Create a network manager instance. 



**Args:**
 
 - <b>`auth_token`</b> (str):  This is the token generated by SpacetimeDB that matches the user's identity. If None, token will be generated 
 - <b>`host`</b> (str):  Hostname:port for SpacetimeDB connection 
 - <b>`address_or_name`</b> (str):  The name or address of the database to connect to 
 - <b>`autogen_package`</b> (ModuleType):  Python package where SpacetimeDB module generated files are located. 
 - <b>`on_connect`</b> (Callable[[], None], optional):  Optional callback called when a connection is made to the SpacetimeDB module. 
 - <b>`on_disconnect`</b> (Callable[[str], None], optional):  Optional callback called when the Python client is disconnected from the SpacetimeDB module. The argument is the close message. 
 - <b>`on_identity`</b> (Callable[[str, bytes], None], optional):  Called when the user identity is recieved from SpacetimeDB. First argument is the auth token used to login in future sessions. 
 - <b>`on_error`</b> (Callable[[str], None], optional):  Optional callback called when the Python client connection encounters an error. The argument is the error message. 



**Example:**
 SpacetimeDBClient.init(autogen, on_connect=self.on_connect) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L282"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.register_on_event`

```python
register_on_event(
    callback: Callable[[src.spacetimedb_sdk.spacetimedb_client.TransactionUpdateMessage], NoneType]
)
```

Register a callback function to handle transaction update events. 

This function registers a callback function that will be called when a reducer modifies a table matching any of the subscribed queries or if a reducer called by this Python client encounters a failure. 



**Args:**
  callback (Callable[[TransactionUpdateMessage], None]):  A callback function that takes a single argument of type `TransactionUpdateMessage`.  This function will be invoked with a `TransactionUpdateMessage` instance containing information  about the transaction update event. 



**Example:**
  def handle_event(transaction_update):  # Code to handle the transaction update event 

 SpacetimeDBClient.instance.register_on_event(handle_event) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.register_on_subscription_applied`

```python
register_on_subscription_applied(callback: Callable[[], NoneType])
```

Register a callback function to be executed when the local cache is updated as a result of a change to the subscription queries. 



**Args:**
 
 - <b>`callback`</b> (Callable[[], None]):  A callback function that will be invoked on each subscription update.  The callback function should not accept any arguments and should not return any value. 



**Example:**
 def subscription_callback():  # Code to be executed on each subscription update 

SpacetimeDBClient.instance.register_on_subscription_applied(subscription_callback) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.subscribe`

```python
subscribe(queries: List[str])
```

Subscribe to receive data and transaction updates for the provided queries. 

This function sends a subscription request to the SpacetimeDB module, indicating that the client wants to receive data and transaction updates related to the specified queries. 



**Args:**
 
 - <b>`queries`</b> (List[str]):  A list of queries to subscribe to. Each query is a string representing  an sql formatted query statement. 



**Example:**
 queries = ["SELECT * FROM table1", "SELECT * FROM table2 WHERE col2 = 0"] SpacetimeDBClient.instance.subscribe(queries) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L306"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.unregister_on_event`

```python
unregister_on_event(
    callback: Callable[[src.spacetimedb_sdk.spacetimedb_client.TransactionUpdateMessage], NoneType]
)
```

Unregister a callback function that was previously registered using `register_on_event`. 



**Args:**
 
 - <b>`callback`</b> (Callable[[TransactionUpdateMessage], None]):  The callback function to unregister. 



**Example:**
 SpacetimeDBClient.instance.unregister_on_event(handle_event) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L265"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.unregister_on_subscription_applied`

```python
unregister_on_subscription_applied(callback: Callable[[], NoneType])
```

Unregister a callback function from the subscription update event. 



**Args:**
 
 - <b>`callback`</b> (Callable[[], None]):  A callback function that was previously registered with the `register_on_subscription_applied` function. 



**Example:**
 def subscription_callback():  # Code to be executed on each subscription update 

SpacetimeDBClient.instance.register_on_subscription_applied(subscription_callback) SpacetimeDBClient.instance.unregister_on_subscription_applied(subscription_callback) 

---

<a href="..\src\spacetimedb_sdk\spacetimedb_client.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `SpacetimeDBClient.update`

```python
update()
```

Process all pending incoming messages from the SpacetimeDB module. 

NOTE: This function must be called on a regular interval to process incoming messages. 



**Example:**
  SpacetimeDBClient.init(autogen, on_connect=self.on_connect)  while True:  SpacetimeDBClient.instance.update()  # Call the update function in a loop to process incoming messages  # Additional logic or code can be added here 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
