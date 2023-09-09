from collections import namedtuple
from dataclasses import dataclass
from typing import Literal

import orjson as json

from panther._utils import read_multipart_form_data


@dataclass(frozen=True)
class Headers:
    accept_encoding: str
    content_length: int
    authorization: str
    content_type: str
    user_agent: str
    connection: str
    accept: str
    host: str


Address = namedtuple('Client', ['ip', 'port'])


class Request:
    def __init__(self, scope: dict):
        """{'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.3'},
        'http_version': '1.1', 'server': ('127.0.0.1', 8000), 'client': ('127.0.0.1', 35064),
        'scheme': 'http', 'root_path': '', 'headers': [
            (b'content-type', b'application/json'),
            (b'user-agent', b'PostmanRuntime/7.29.2'),
            (b'accept', b'*/*'),
            (b'postman-token', b'3e78fbf3-df2f-41bd-bedc-cf6027fa4fe6'),
            (b'host', b'127.0.0.1:8000'),
            (b'accept-encoding', b'gzip, deflate, br'),
            (b'connection', b'keep-alive'),
            (b'content-length', b'55')
        ],
        'method': 'GET', 'path': '/list/', 'raw_path': b'/list/', 'query_string': b''}.
        """
        self.scope = scope
        self._data = None
        self._validated_data = None
        self._user = None
        self._headers: Headers | None = None
        self._params: dict | None = None

    @property
    def headers(self):
        _headers = {header[0].decode('utf-8'): header[1].decode('utf-8') for header in self.scope['headers']}
        if self._headers is None:
            self._headers = Headers(
                accept_encoding=_headers.pop('accept-encoding', None),
                content_length=_headers.pop('content_length', None),
                authorization=_headers.pop('authorization', None),
                content_type=_headers.pop('content-type', None),  # Handle content-type & boundary together
                user_agent=_headers.pop('user-agent', None),
                connection=_headers.pop('connection', None),
                accept=_headers.pop('accept', None),
                host=_headers.pop('host', None),
                # TODO: Others ...
            )
        return self._headers

    @property
    def query_params(self) -> dict:
        if self._params is None:
            self._params = dict()
            if (query_string := self.scope['query_string']) != b'':
                query_string = query_string.decode('utf-8').split('&')
                for param in query_string:
                    k, *_, v = param.split('=')
                    self._params[k] = v
        return self._params

    @property
    def method(self) -> Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        return self.scope['method']

    @property
    def path(self) -> str:
        return self.scope['path']

    @property
    def server(self) -> Address:
        return Address(*self.scope['server'])

    @property
    def client(self) -> Address:
        return Address(*self.scope['client'])

    @property
    def http_version(self) -> str:
        return self.scope['http_version']

    @property
    def scheme(self) -> str:
        return self.scope['scheme']

    @property
    def pure_data(self) -> dict | bytes:
        """Data before validation"""

        if self._data is None:
            match (self.headers.content_type or '').split('; boundary='):
                case ['application/json']:
                    self._data = json.loads(self.__body)
                case ['multipart/form-data', boundary]:
                    self._data = read_multipart_form_data(boundary=boundary, body=self.__body)
                case _:
                    # We don't know the `content-type` so just pass the payload to user
                    self._data = self.__body
        return self._data

    @property
    def data(self):
        """
        Return The Validated Data
        It has been set on API.validate_input() while request is happening.
        """
        return self._validated_data

    def set_validated_data(self, validated_data) -> None:
        self._validated_data = validated_data

    def set_body(self, body: bytes):
        self.__body = body

    @property
    def user(self):
        return self._user

    def set_user(self, user) -> None:
        self._user = user
