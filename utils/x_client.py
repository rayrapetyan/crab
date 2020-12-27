import json

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
)

from twisted.internet.protocol import ReconnectingClientFactory


class XProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.on_open()

    def onMessage(self, payload, isBinary):
        msg = json.loads(payload.decode('utf8'))
        self.factory.on_message(msg)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class XClient(WebSocketClientFactory, ReconnectingClientFactory):
    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)

    def buildProtocol(self, addr):
        p = XProtocol()
        p.factory = self
        self.protocol = p
        return p

    def send_message(self, msg):
        assert(self.protocol)
        self.protocol.sendMessage(payload=json.dumps(msg).encode('utf-8'), isBinary=False)
