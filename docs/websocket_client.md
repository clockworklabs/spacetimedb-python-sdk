<!-- markdownlint-disable -->

<a href="..\websocket_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `websocket_client`






---

<a href="..\websocket_client.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WebSocketClient`




<a href="..\websocket_client.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.__init__`

```python
__init__(
    protocol,
    on_connect=None,
    on_close=None,
    on_error=None,
    on_message=None
)
```








---

<a href="..\websocket_client.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.close`

```python
close()
```





---

<a href="..\websocket_client.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.connect`

```python
connect(auth, host, name_or_address, ssl_enabled)
```





---

<a href="..\websocket_client.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.decode_hex_string`

```python
decode_hex_string(hex_string)
```





---

<a href="..\websocket_client.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.on_close`

```python
on_close(ws, status_code, close_msg)
```





---

<a href="..\websocket_client.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.on_error`

```python
on_error(ws, error)
```





---

<a href="..\websocket_client.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.on_message`

```python
on_message(ws, message)
```





---

<a href="..\websocket_client.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.on_open`

```python
on_open(ws)
```





---

<a href="..\websocket_client.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.process_message`

```python
process_message(message)
```





---

<a href="..\websocket_client.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `WebSocketClient.send`

```python
send(data)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
