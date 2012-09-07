#!/usr/bin/python
# -*- coding: utf-8 -*-

from WSRequestHandler import WSRequestHandler
from base64 import b64encode, b64decode
import sublime
from struct import pack, unpack_from
import array
import json
import LiveReload

try:
    from hashlib import md5, sha1
except:
    from md5 import md5
    from sha import sha as sha1

s2a = lambda s: [ord(c) for c in s]


def log(s):
    if False:
        print 'WebSocketClient: ' + str(s)


class WebSocketClient(object):

    """
    A single connection (client) of the program
    """

    # Handshaking, create the WebSocket connection

    server_handshake_hybi = \
        """HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: %s\r
"""
    GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self, handler):
        self.handler = handler
        self.socket = handler.request
        self.addr = handler.client_address
        self.server = handler.server
        try:
            self.wsh = WSRequestHandler(self.socket, self.addr, False)
            if not hasattr(self.wsh, 'headers'):
                self.close()
            self.headers = self.wsh.headers
            self.ver = self.headers.get('Sec-WebSocket-Version')
            self.handshaken = False
            if self.ver:

                # HyBi/IETF version of the protocol

                # HyBi-07 report version 7
                # HyBi-08 - HyBi-12 report version 8
                # HyBi-13 reports version 13

                if self.ver in ['7', '8', '13']:
                    self.version = 'hybi-%02d' % int(self.ver)
                else:
                    raise Exception('Unsupported protocol version %s'
                                    % self.ver)

                key = self.headers.get('Sec-WebSocket-Key')
                log(key)

                # Generate the hash value for the accept header

                accept = b64encode(sha1(key + self.GUID).digest())

                response = self.server_handshake_hybi % accept
                response += '\r\n'
                log(response)
                self.socket.send(response.encode())
                self.handler.addClient(self)
                while 0x1:
                    try:
                        data = self.socket.recv(1024)
                    except Exception, e:
                        log(e)
                        break
                    if not data:
                        break
                    dec = WebSocketClient.decode_hybi(data)
                    if dec['opcode'] == 0x08:
                        self.close()
                    else:
                        self.onreceive(dec)

                # Close the client connection

                self.close()
        except Exception, e:

            self.close()

    @staticmethod
    def unmask(buf, f):
        pstart = f['hlen'] + 4
        pend = pstart + f['length']

        # Slower fallback

        data = array.array('B')
        mask = s2a(f['mask'])
        data.fromstring(buf[pstart:pend])
        for i in range(len(data)):
            data[i] ^= mask[i % 4]
        return data.tostring()

    @staticmethod
    def encode_hybi(buf, opcode, base64=False):
        """ Encode a HyBi style WebSocket frame.
        Optional opcode:
            0x0 - continuation
            0x1 - text frame (base64 encode buf)
            0x2 - binary frame (use raw buf)
            0x8 - connection close
            0x9 - ping
            0xA - pong
        """

        if base64:
            buf = b64encode(buf)

        b1 = 0x80 | opcode & 0x0f  # FIN + opcode
        payload_len = len(buf)
        if payload_len <= 125:
            header = pack('>BB', b1, payload_len)
        elif payload_len > 125 and payload_len < 65536:
            header = pack('>BBH', b1, 126, payload_len)
        elif payload_len >= 65536:
            header = pack('>BBQ', b1, 0x7f, payload_len)

        log('Encoded: %s' % repr(header + buf))

        return (header + buf, len(header), 0)

    @staticmethod
    def decode_hybi(buf, base64=False):
        """ Decode HyBi style WebSocket packets.
        Returns:
            {'fin'          : 0_or_1,
             'opcode'       : number,
             'mask'         : 32_bit_number,
             'hlen'         : header_bytes_number,
             'length'       : payload_bytes_number,
             'payload'      : decoded_buffer,
             'left'         : bytes_left_number,
             'close_code'   : number,
             'close_reason' : string}
        """

        f = {
            'fin': 0,
            'opcode': 0,
            'mask': 0,
            'hlen': 2,
            'length': 0,
            'payload': None,
            'left': 0,
            'close_code': None,
            'close_reason': None,
            }

        blen = len(buf)
        f['left'] = blen

        if blen < f['hlen']:
            return f  # Incomplete frame header

        (b1, b2) = unpack_from('>BB', buf)
        f['opcode'] = b1 & 0x0f
        f['fin'] = (b1 & 0x80) >> 7
        has_mask = (b2 & 0x80) >> 7

        f['length'] = b2 & 0x7f

        if f['length'] == 126:
            f['hlen'] = 4
            if blen < f['hlen']:
                return f  # Incomplete frame header
            (f['length'], ) = unpack_from('>xxH', buf)
        elif f['length'] == 0x7f:
            f['hlen'] = 10
            if blen < f['hlen']:
                return f  # Incomplete frame header
            (f['length'], ) = unpack_from('>xxQ', buf)

        full_len = f['hlen'] + has_mask * 4 + f['length']

        if blen < full_len:  # Incomplete frame
            return f  # Incomplete frame header

        # Number of bytes that are part of the next frame(s)

        f['left'] = blen - full_len

        # Process 1 frame

        if has_mask:

            # unmask payload

            f['mask'] = buf[f['hlen']:f['hlen'] + 4]
            f['payload'] = WebSocketClient.unmask(buf, f)
        else:
            log('Unmasked frame: %s' % repr(buf))
            f['payload'] = buf[f['hlen'] + has_mask * 4:full_len]

        if base64 and f['opcode'] in [0x1, 2]:
            try:
                f['payload'] = b64decode(f['payload'])
            except:
                log('Exception while b64decoding buffer: %s'
                    % repr(buf))
                raise

        if f['opcode'] == 0x08:
            if f['length'] >= 2:
                f['close_code'] = unpack_from('>H', f['payload'])
            if f['length'] > 3:
                f['close_reason'] = (f['payload'])[2:]

        return f

    def close(self):
        """
        Close this connection
        """

        self.handler.removeClient(self)
        self.socket.close()

    def send(self, msg):
        """
        Send a message to this client
        """

        msg = WebSocketClient.encode_hybi(msg, 0x1, False)
        self.socket.send(msg[0])

    def onreceive(self, data):
        """
        Event called when a message is received from this client
        """

        try:
            log(data)

            if 'payload' in data:
                log('payload true')
                req = json.loads(data.get('payload'))
                log(req.get('command'))
                if not self.handshaken:
                    if req.get('command') == 'hello':
                        sublime.set_timeout(lambda : \
                                sublime.status_message('New LiveReload v2 client connected'
                                ), 100)
                        self.send('{"command":"hello","protocols":["http://livereload.com/protocols/connection-check-1","http://livereload.com/protocols/official-6","http://livereload.com/protocols/official-7","http://dz0ny.info/sm2-plugin"]}'
                                  )
                    else:
                        sublime.set_timeout(lambda : \
                                sublime.status_message('New LiveReload v1 client connected'
                                ), 100)
                        self.send('!!ver:' + str(self.server.version))

                    self.handshaken = True
                    self.info = {'origin': self.headers.get('Origin'),
                                 'url': data.get('payload')}
                    self.handler.updateInfo()
                else:
                    LiveReload.API.dispatch_onReceive(req,
                            self.self.headers.get('Origin'))
        except Exception, e:

            log(e)

    def _clean(self, msg):
        """
        Remove special chars used for the transmission
        """

        msg = msg.replace('\x00', '', 0x1)
        msg = msg.replace('\xff', '', 0x1)
        return msg
