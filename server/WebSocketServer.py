#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    from .WebSocketClient import WebSocketClient
except ValueError:
    from WebSocketClient import WebSocketClient

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

def log(s):
    pass


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def updateInfo(self):
        self.server.clients_info = []
        for client in self.server.clients:
            self.server.clients_info.append(client.info)

    def addClient(self, client):
        log('Add to clients table ' + str(client))
        self.server.clients.append(client)

    def handle(self):
        log('new client ' + str(self.client_address))
        WebSocketClient(self)

    def removeClient(self, client):
        log('Remove from clients table ' + str(client))
        try:
            self.server.clients.remove(client)
            self.updateInfo()
        except Exception:

            # # this is normal because we support both connection protocols

            pass


class ThreadedTCPServer(SocketServer.ThreadingMixIn,
    SocketServer.TCPServer):

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address,
        RequestHandlerClass,
        version,
        ):

        SocketServer.TCPServer.__init__(self, server_address,
                RequestHandlerClass)
        self.clients = []
        self.clients_info = []
        self.version = version

    def send_all(self, data):
        """
        Send a message to all the currently connected clients.
        """

        for client in self.clients:
            try:
                client.send(data)
            except Exception:
                self.clients.remove(client)

    def list_clients(self):
        """
        List all the currently connected clients.
        contains request URL, headers
        """

        return self.clients_info


class WebSocketServer:

    """
    Handle the Server, bind and accept new connections, open and close
    clients connections.
    """

    def __init__(self, port, version):
        self.server = ThreadedTCPServer((''.encode('ascii'), port),
                ThreadedTCPRequestHandler, version.encode('ascii'))

    def send(self, data):
        self.server.send_all(data)

    def stop(self):
        """
        Stop the server.
        """

        self.server.shutdown()

    def start(self):
        """
        Start the server.
        """

        self.server.serve_forever()
