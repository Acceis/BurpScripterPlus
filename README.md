# Burp Scripter Plus

Burp Scripter Plus adds an extra proxy layer to Burp with a simple Python interface.

Browser -> BURP -> BurpScripterPlus -> Website
Browser <- BURP <- BurpScripterPlus <- Website

This project is a fork of "Python Scripter" (https://github.com/portswigger/python-scripter) with some new features :
- Response and Request are mapped into easy to use objects
- Auto Content-Length generation
- Auto message parser/rebuild for switching between string request and easy to use object
- Documentation !

Request object has multiple attributes :
- params : dictionnary of GET parameters/values
- body : dictionnary of body key/values (or a simple string if other format like xml, json, etc.)
- headers : dictionnary of headers parameters/values
- is_request : boolean (True)
- is_response : boolean (False)
- method : string HTTP method
- path : string url
- http_version : string like HTTP/1.1

Response object has multiple attributes :
- body : dictionnary of body key/values (or a simple string if other format like xml, json, html,etc.)
- headers : dictionnary of headers parameters/values
- is_request : boolean (False)
- is_response : boolean (True)
- http_version : string (ex: HTTP/1.1)
- response_code : int (ex: 200)
- response_value : string (ex: OK)

## Setup
- Add the Jython jarfile to Burp (https://www.jython.org/download)
- Go to extender, click "Add"
- Extension type : Python
- Extension file : burpscripterplus.py
- Click "Next"

A new tab "Script+" is appended to the Burp interface; you can type your code in it. The message's object is directly accessible (following examples work with a simple copy/paste).

## Examples

### Change or add the "param1" GET parameter in outgoing request

```
if message.is_request:
    message.params["param1"] = "my_new_value"
```

### Edit the outgoing request if "my_header" is in the headers

```
if message.is_request:
    if "my_header" in message.headers.keys():
        message.headers["my_header"] = "my_new_header_value"
```

### Change the outgoing request body as string

```
if message.is_request:
    message.body = "This is a new body"
```

### Change the outgoing request body param

```
if message.is_request:
    message.body["myparam"] = "This is a new value"
```

### Base64 encode the outgoing request body param

```
import base64

if message.is_request:
    message.body["myparam"] = base64.b64encode(message.body["myparam"])
```

### Change response header

```
if message.is_response:
    if "my_header" in message.headers.keys():
        message.headers["my_header"] = "my_new_header_value"
```

### Modify response body

```
if message.is_response:
    message.body = message.body.replace("foo", "bar")
```

## Documentation

```
Help on module burpscripterplus:

NAME
    burpscripterplus

CLASSES
    __builtin__.object
        Message
            Request
            Response

    class Message(__builtin__.object)
     |  Methods defined here:
     |  
     |  __init__(self, message_info, helpers, callbacks)
     |      Message constructor
     |      
     |      :param message_info: message_info  from Burp extender
     |      :param helpers: helpers  from Burp extender
     |      :param callbacks: callbacks from Burp extender
     |      :return: Message instance (not usable, just a parent class for Request and Response)
     |      :rtype: Message
     |  
     |  build_message(self)
     |      Build a string message from parsed message (created by parse_message)
     |      
     |      Do not use this one, it's only for forcing childs to implement method
     |  
     |  parse_message(self)
     |      Parse message input from Burp extender
     |      
     |      Do not use this one, it's only for forcing childs to implement method
     |  
     |  update_content_length(self, data)
     |      Recalculate body length and set it in Content-Length header
     |      
     |      :param data: data is the body string used for re-calculating Content-Length header
     |      :type data: string
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Request(Message)
     |  Method resolution order:
     |      Request
     |      Message
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, message_info, helpers, callbacks)
     |      Request constructor
     |      
     |      :param message_info: message_info  from Burp extender
     |      :param helpers: helpers  from Burp extender
     |      :param callbacks: callbacks from Burp extender
     |      :return: Request instance
     |      :rtype: Request
     |  
     |  build_body(self)
     |      Transform dict body to string
     |      
     |      This method takes all key:values items from doby and construct a body string
     |      
     |      :return: full body string
     |      :rtype: string
     |  
     |  build_message(self)
     |      Build Complete message as string from attributes
     |      
     |      This method takes all Request attributes and build a response string
     |      This method is auto-called by extension and you don't have to call build_message yourself
     |  
     |  build_parameters(self)
     |      From params dict to string
     |      
     |      This method takes all key:values from parameters (GET) and build a string
     |      
     |      :return: GET parameters as string
     |      :rtype: string
     |  
     |  parse_message(self)
     |      Parse message input from Burp extender
     |      
     |      This method populate the Request object with parsed data
     |  
     |  parse_parameters(self, line)
     |      Parse params string to dict
     |      
     |      This method takes the GET parameters as string and create a dictionnary in params attribute
     |      
     |      :param line: First line of request as string (ex: GET /foo?bar=baz HTTP/1.1)
     |      :type line: string
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Message:
     |  
     |  update_content_length(self, data)
     |      Recalculate body length and set it in Content-Length header
     |      
     |      :param data: data is the body string used for re-calculating Content-Length header
     |      :type data: string
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Message:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Response(Message)
     |  Method resolution order:
     |      Response
     |      Message
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, message_info, helpers, callbacks)
     |      Response constructor
     |      
     |      :param message_info: message_info  from Burp extender
     |      :param helpers: helpers  from Burp extender
     |      :param callbacks: callbacks from Burp extender
     |      :return: Response instance
     |      :rtype: Response
     |  
     |  build_message(self)
     |      Build Complete message as string from attributes
     |      
     |      This method takes all Response attributes and build a response string
     |      This method is auto-called by extension and you don't have to call build_message yourself
     |  
     |  parse_message(self)
     |      Parse message input from Burp extender
     |      
     |      This method populate the Response object with parsed data
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Message:
     |  
     |  update_content_length(self, data)
     |      Recalculate body length and set it in Content-Length header
     |      
     |      :param data: data is the body string used for re-calculating Content-Length header
     |      :type data: string
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Message:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    get_message(message_info, helpers, message_is_request, callbacks)
        Return Message or Request according to message

        :param message_info: message_info  from Burp extender
        :param helpers: helpers  from Burp extender
        :param message_is_request: message_is_request  from Burp extender
        :param callbacks: callbacks from Burp extender
        :return: Request or Response instance
        :rtype: Message
```

## License

```
THE BEER-WARE LICENSE" (Revision 42): ganapati (@G4N4P4T1) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.
```
