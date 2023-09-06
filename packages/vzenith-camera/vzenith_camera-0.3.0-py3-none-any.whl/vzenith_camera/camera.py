from __future__ import annotations
import logging
import json
import struct
import time
from dataclasses import dataclass
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Optional

from .emitter import Emitter
from .exceptions import BadPacketHeader, HeartbeatError, BadResponse, BadRequest, Unauthorized, NotFound, \
    MethodNotAllowed, RequestTimeout, InternalServerError
from .types import PlateResult

PACKET_TYPE_DATA = 0
PACKET_TYPE_HEARTBEAT = 1
PACKET_TYPE_BINARY = 2

DATA_ENCODING = 'gb2312'

WATCHER_IVSRESULT_ENABLED = True


@dataclass
class PacketHeader:
    type: int
    length: int
    sn: int = 0

    def to_bytes(self) -> bytes:
        return struct.pack('!2sBBI', b'VZ', self.type, self.sn, self.length)

    @staticmethod
    def parse(s: bytes) -> Optional[PacketHeader]:
        if len(s) != 8 or s[0:2] != b'VZ':
            raise BadPacketHeader(s)

        fds = struct.unpack('!2sBBI', s)

        return PacketHeader(type=fds[1], length=fds[3], sn=fds[2])


@dataclass
class Packet:
    header: PacketHeader
    data: Optional[bytes]


class SmartCamera(Emitter):
    socket: socket

    name: str
    host: str
    port: int

    def __init__(self, name: str, host: str, port: int = 8131):
        super().__init__()

        self.socket = socket(AF_INET, SOCK_STREAM)

        self.name = name
        self.host = host
        self.port = port

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_bytes(self, s: bytes):
        logging.debug('send: %s to %s:%d', s, self.host, self.port)
        self.socket.send(s)

    def send_request(self, req: dict):
        data = json.dumps(req, ensure_ascii=False).encode(DATA_ENCODING)

        header = PacketHeader(PACKET_TYPE_DATA, len(data))

        s = header.to_bytes() + data
        self.send_bytes(s)

    def recv_bytes(self, n: int, blocking: bool = True) -> Optional[bytes]:
        self.socket.setblocking(blocking)
        s = self.socket.recv(n)
        logging.debug('recv: %s from %s:%d', s, self.host, self.port)

        return s

    def recv_response(self, blocking: bool = True) -> Optional[dict]:
        s = self.recv_bytes(8, blocking)

        header = PacketHeader.parse(s)

        if header.type == PACKET_TYPE_HEARTBEAT:
            return None

        s = self.recv_bytes(header.length)

        return json.loads(s.decode(DATA_ENCODING))

    def heartbeat(self):
        self.send_bytes(PacketHeader(PACKET_TYPE_HEARTBEAT, 0).to_bytes())
        s = self.recv_bytes(8)
        if s != b'VZ\x01\x00\x00\x00\x00\x00':
            raise HeartbeatError(s)

    def recv_cmd_response(self, blocking: bool = True) -> dict:
        res = self.recv_response(blocking)
        if 'state_code' not in res:
            raise BadResponse(res)

        if res['state_code'] == 400:
            raise BadRequest(res)
        if res['state_code'] == 401:
            raise Unauthorized(res)
        if res['state_code'] == 404:
            raise NotFound(res)
        if res['state_code'] == 405:
            raise MethodNotAllowed(res)
        if res['state_code'] == 408:
            raise RequestTimeout(res)
        if res['state_code'] == 500:
            raise InternalServerError(res)

        return res

    def cmd_getsn(self) -> str:
        self.send_request({'cmd': 'getsn'})

        res = self.recv_cmd_response()
        return res['value']

    def cmd_ivsresult(self, enable: bool = False, result_format: str = 'json', image: bool = True, image_type: int = 0):

        cmd = {
            'cmd': 'ivsresult',
            'enable': enable,
            'format': result_format,
            'image': image,
            'image_type': image_type
        }

        self.send_request(cmd)
        self.recv_response()

        if enable:
            thread = Thread(target=_ivsresult_watcher, args=(self,))
            thread.start()


def _ivsresult_watcher(camera: SmartCamera):
    count = 0

    while WATCHER_IVSRESULT_ENABLED:
        if count > 3:
            camera.heartbeat()
            count = 0

        count += 1

        try:
            header = PacketHeader.parse(camera.recv_bytes(8, blocking=False))
            if header.type != PACKET_TYPE_HEARTBEAT:
                s = camera.recv_bytes(header.length)

                res = json.loads(s[0:s.index(0x00) - 1].decode('gb2312'))['PlateResult']
                result = PlateResult(
                    license=res['license'],
                )

                camera.emit('ivsresult', result)
        except BlockingIOError:
            ...

        time.sleep(1)
