# -*- coding: utf-8 -*-

"""
Name:           BurpScripter Plus
Version:        0.1
Author:         Ganapati - @G4N4P4T1
Github:         https://github.com/Acceis/BurpScripterPlus
Description:    This extension provide a Python panel for writing custom proxy script.
License :       THE BEER-WARE LICENSE" (Revision 42): ganapati (@G4N4P4T1) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.
"""

from java.awt import Font
from java.io import PrintWriter
from javax.swing import JScrollPane, JTextPane
from javax.swing.text import SimpleAttributeSet

from burp import (
    IBurpExtender,
    IExtensionStateListener,
    IHttpListener,
    ITab,
)

import base64
import urllib
import traceback

VERSION = "0.1"


def get_message(
    message_info, helpers, message_is_request, callbacks
):
    """ Return Message or Request according to message

        :param message_info: message_info  from Burp extender
        :param helpers: helpers  from Burp extender
        :param message_is_request: message_is_request  from Burp extender
        :param callbacks: callbacks from Burp extender
        :return: Request or Response instance
        :rtype: Message

    """
    if message_is_request:
        return Request(message_info, helpers, callbacks)
    else:
        return Response(message_info, helpers, callbacks)


class Message(object):
    """ Generic Class for Request and Response

        Only used as parent class
    """

    def __init__(self, message_info, helpers, callbacks):
        """ Message constructor

            :param message_info: message_info  from Burp extender
            :param helpers: helpers  from Burp extender
            :param callbacks: callbacks from Burp extender
            :return: Message instance (not usable, just a parent class for Request and Response)
            :rtype: Message
        """
        self.message_info = message_info
        self.callbacks = callbacks
        self.helpers = helpers

        self.is_request = False
        self.is_response = False
        self.is_in_scope = callbacks.isInScope(
            message_info.getUrl()
        )

    def parse_message(self):
        """ Parse message input from Burp extender
            
            Do not use this one, it's only for forcing childs to implement method
        """
        raise NotImplementedError

    def build_message(self):
        """ Build a string message from parsed message (created by parse_message)
            
            Do not use this one, it's only for forcing childs to implement method
        """
        raise NotImplementedError

    def update_content_length(self, data):
        """ Recalculate body length and set it in Content-Length header

            :param data: data is the body string used for re-calculating Content-Length header
            :type data: string
        """
        if data is not None:
            self.headers["Content-Length"] = len(data)


class Response(Message):
    """ Response class

        Map the entire Response into an object for easier manipulation
    """

    def __init__(self, message_info, helpers, callbacks):
        """ Response constructor

            :param message_info: message_info  from Burp extender
            :param helpers: helpers  from Burp extender
            :param callbacks: callbacks from Burp extender
            :return: Response instance 
            :rtype: Response
        """
        Message.__init__(
            self, message_info, helpers, callbacks
        )

        self.is_request = False
        self.is_response = True
        self.http_version = ""
        self.response_code = 200
        self.response_value = ""
        self.headers = {}
        self.body = ""

        self.parse_message()

    def parse_message(self):
        """ Parse message input from Burp extender
            
            This method populate the Response object with parsed data
        """
        message = self.message_info.getResponse()
        parsed_message = self.helpers.analyzeResponse(
            message
        )

        # Parse headers
        headers_dict = {}
        headers = parsed_message.getHeaders()

        # Reconstruct the headers as dict
        headers_list = list(headers)
        self.http_version, self.response_code, self.response_value = headers_list[
            0
        ].split(
            " ", 2
        )
        for header in headers_list[1:]:
            k, v = header.split(": ")
            headers_dict[str(k)] = str(v)

        self.headers = headers_dict
        self.body = message[
            (parsed_message.getBodyOffset()) :
        ].tostring()

    def build_message(self):
        """ Build Complete message as string from attributes

            This method takes all Response attributes and build a response string 
            This method is auto-called by extension and you don't have to call build_message yourself
        """
        self.update_content_length(self.body)

        message = ""
        message = "%s %s %s\r\n" % (
            self.http_version,
            self.response_code,
            self.response_value,
        )

        # Add headers
        for k, v in self.headers.items():
            message = message + "%s: %s\r\n" % (k, v)
        message = message + "\r\n"

        # Add body
        message = message + self.body.decode(
            "utf-8", "replace"
        )

        self.message_info.setResponse(message)


class Request(Message):
    """ Request class

        Map the entire Request into an object for easier manipulation
    """

    def __init__(self, message_info, helpers, callbacks):
        """ Request constructor

            :param message_info: message_info  from Burp extender
            :param helpers: helpers  from Burp extender
            :param callbacks: callbacks from Burp extender
            :return: Request instance 
            :rtype: Request
        """
        Message.__init__(
            self, message_info, helpers, callbacks
        )

        self.is_request = True
        self.is_response = False
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.params = {}
        self.headers = {}
        self.body = {}
        self.body_str = ""
        self.parse_message()

    def parse_parameters(self, line):
        """ Parse params string to dict

            This method takes the GET parameters as string and create a dictionnary in params attribute

            :param line: First line of request as string (ex: GET /foo?bar=baz HTTP/1.1)
            :type line: string
        """
        self.method, path_params, self.http_version = line.split(
            " "
        )
        path_params_array = path_params.split("?")
        self.path = path_params_array[0]
        if len(path_params_array) > 1:
            params = path_params_array[1]
            for _ in params.split("&"):
                try:
                    k, v = _.split("=")
                    self.params[k] = v
                except ValueError:
                    k = _.split("=")[0]
                    self.params[k] = ""

    def build_parameters(self):
        """ From params dict to string

            This method takes all key:values from parameters (GET) and build a string

            :return: GET parameters as string
            :rtype: string
        """
        params = ""
        for k, v in self.params.items():
            params = params + "%s=%s&" % (
                k.strip(),
                v.strip(),
            )
        if len(params) > 0:
            params = "?%s" % params[:-1]

        return params

    def parse_message(self):
        """ Parse message input from Burp extender
            
            This method populate the Request object with parsed data
        """
        message = self.message_info.getRequest()
        parsed_message = self.helpers.analyzeRequest(
            message
        )

        # Parse headers
        headers_dict = {}
        headers = parsed_message.getHeaders()

        # Reconstruct the headers as dict
        headers_list = list(headers)
        for header in headers_list[1:]:
            k, v = header.split(": ")
            headers_dict[str(k)] = str(v)

        self.headers = headers_dict

        self.parse_parameters(headers_list[0])

        # Extract body from message
        body = message[(parsed_message.getBodyOffset()) :]
        self.body_str = "".join(chr(_) for _ in body)
        body_dict = {}
        if "Content-Length" in self.headers.keys():
            try:
                if int(self.headers["Content-Length"]) > 0:
                    for arg in self.body_str.split("&"):
                        k, v = arg.split("=")
                        body_dict[k] = v
                self.body = body_dict
            except:
                self.body = None

    def build_body(self):
        """ Transform dict body to string

            This method takes all key:values items from doby and construct a body string

            :return: full body string
            :rtype: string
        """
        body = ""
        for k, v in self.body.items():
            body = body + "%s=%s&" % (k.strip(), v.strip())
        return body[:-1]

    def build_message(self):
        """ Build Complete message as string from attributes

            This method takes all Request attributes and build a response string 
            This method is auto-called by extension and you don't have to call build_message yourself
        """
        if isinstance(self.body, dict):
            self.body_str = self.build_body()
        else:
            if self.body is not None:
                self.body_str = self.body

        self.update_content_length(self.body_str)

        message = ""

        # Add method, path and params
        message = "%s %s%s %s\r\n" % (
            self.method,
            self.path,
            self.build_parameters(),
            self.http_version,
        )

        # Add headers
        for k, v in self.headers.items():
            message = message + "%s: %s\r\n" % (k, v)
        message = message + "\r\n"

        # Add body
        message = message + self.body_str.decode(
            "utf-8", "replace"
        )

        self.message_info.setRequest(message)


class BurpExtender(
    IBurpExtender,
    IExtensionStateListener,
    IHttpListener,
    ITab,
):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.helpers

        callbacks.setExtensionName("Burp Scripter Plus")

        stdout = PrintWriter(callbacks.getStdout(), True)
        stdout.println(
            """Successfully loaded Burp Scripter Plus v"""
            + VERSION
            + """\n
Repository @ https://github.com/Acceis/BurpScripterPlus
Send feedback or bug reports on twitter @G4N4P4T1"""
        )

        self.scriptpane = JTextPane()
        self.scriptpane.setFont(
            Font("Monospaced", Font.PLAIN, 12)
        )

        self.scrollpane = JScrollPane()
        self.scrollpane.setViewportView(self.scriptpane)

        self._code = compile("", "<string>", "exec")
        self._script = ""

        script = callbacks.loadExtensionSetting("script")

        if script:
            script = base64.b64decode(script)

            self.scriptpane.document.insertString(
                self.scriptpane.document.length,
                script,
                SimpleAttributeSet(),
            )

            self._script = script
            try:
                self._code = compile(
                    script, "<string>", "exec"
                )
            except Exception as e:
                traceback.print_exc(
                    file=self.callbacks.getStderr()
                )

        callbacks.registerExtensionStateListener(self)
        callbacks.registerHttpListener(self)
        callbacks.customizeUiComponent(
            self.getUiComponent()
        )
        callbacks.addSuiteTab(self)

        self.scriptpane.requestFocus()

    def extensionUnloaded(self):
        try:
            self.callbacks.saveExtensionSetting(
                "script",
                base64.b64encode(
                    self._script.replace(
                        "\nmessage.build_message()", ""
                    )
                ),
            )
        except Exception:
            traceback.print_exc(
                file=self.callbacks.getStderr()
            )
        return

    def processHttpMessage(
        self, toolFlag, messageIsRequest, messageInfo
    ):
        try:
            globals_ = {}
            locals_ = {
                "extender": self,
                "toolFlag": toolFlag,
                "messageInfo": messageInfo,
                "message": get_message(
                    messageInfo,
                    self.helpers,
                    messageIsRequest,
                    self.callbacks,
                ),
            }
            exec(self.script, globals_, locals_)
        except Exception:
            traceback.print_exc(
                file=self.callbacks.getStderr()
            )
        return

    def getTabCaption(self):
        return "Script+"

    def getUiComponent(self):
        return self.scrollpane

    @property
    def script(self):
        end = self.scriptpane.document.length
        _script = (
            self.scriptpane.document.getText(0, end)
            + "\nmessage.build_message()"
        )

        if _script == self._script:
            return self._code

        self._script = _script
        self._code = compile(_script, "<string>", "exec")
        return self._code
