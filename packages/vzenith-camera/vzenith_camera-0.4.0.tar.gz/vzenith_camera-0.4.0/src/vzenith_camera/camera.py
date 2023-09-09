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
from .exceptions import BadPacketHeader, BadResponse, BadRequest, Unauthorized, NotFound, \
    MethodNotAllowed, RequestTimeout, InternalServerError
from .types import PlateResult

PACKET_TYPE_DATA = 0
PACKET_TYPE_HEARTBEAT = 1
PACKET_TYPE_BINARY = 2

DATA_ENCODING = 'gb2312'


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


class BaseCamera(Emitter):
    socket: socket

    name: str
    host: str
    port: int

    enable_thread_keepalive: bool
    enable_thread_ivsresult: bool

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.socket = socket(AF_INET, SOCK_STREAM)

    def connect(self, host: str, port: int = 8131, keepalive: bool = False):
        logging.debug('connect to %s (%s:%d)', self.name, host, port)
        self.socket.connect((host, port))

        self.host = host
        self.port = port
        self.enable_thread_keepalive = keepalive

        if keepalive:
            Thread(target=_thread_keepalive, name=f'thread-keepalive:{self.name}', args=(self,)).start()

    def send_bytes(self, s: bytes):
        logging.debug('send: %s to (%s:%d)', s, self.host, self.port)
        self.socket.send(s)

    def send_request(self, req: dict):
        data = json.dumps(req, ensure_ascii=False).encode(DATA_ENCODING)

        header = PacketHeader(PACKET_TYPE_DATA, len(data))

        s = header.to_bytes() + data
        self.send_bytes(s)

    def recv_bytes(self, n: int, blocking: bool = True) -> Optional[bytes]:
        self.socket.setblocking(blocking)
        s = self.socket.recv(n)
        logging.debug('recv: %s from (%s:%d)', s, self.host, self.port)

        return s

    def recv_response(self, blocking: bool = True) -> Optional[bytes]:
        s = self.recv_bytes(8, blocking)

        header = PacketHeader.parse(s)

        if header.type == PACKET_TYPE_HEARTBEAT:
            return None

        if header.type == PACKET_TYPE_DATA:
            return self.recv_bytes(header.length)

        raise NotImplementedError()

    def heartbeat(self):
        self.send_bytes(PacketHeader(PACKET_TYPE_HEARTBEAT, 0).to_bytes())

    @staticmethod
    def check_response(res: dict):
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


class SmartCamera(BaseCamera):
    def cmd_getsn(self) -> str:
        self.send_request({'cmd': 'getsn'})

        res = json.loads(self.recv_response().decode(DATA_ENCODING))
        self.check_response(res)

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
            self.enable_thread_ivsresult = True
            Thread(target=_thread_ivsresult, name=f'thread-ivsresult:{self.name}', args=(self,)).start()

    def cmd_getivsresult(self, image: bool = False, result_format: str = 'json'):
        self.send_request({'cmd': 'getivsresult', 'image': image, 'format': result_format})
        s = self.recv_response()
        res = json.loads(s[0:s.index(0x00) - 1].decode('gb2312'))['PlateResult']

        return PlateResult(
            license=res['license']
        )


def _thread_ivsresult(camera: SmartCamera):
    while camera.enable_thread_ivsresult:
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


def _thread_keepalive(camera: SmartCamera, interval: float = 5.0):
    while camera.enable_thread_keepalive:
        camera.heartbeat()
        time.sleep(interval)
