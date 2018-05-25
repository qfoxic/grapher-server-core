#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The server was intendedly made synchronous to support only peer-to-peer connections.
The idea here is to have only one client per one server script to provide secure one-to-one session
and to avoid complexity.

The server could be run locally:

python3 -m grapher.core.server --port GRAPHER_PORT

Or via a ssh tunnel:

ssh -L LOCAL_PORT:127.0.0.1:GRAPHER_PORT grapher.host -- "python3 -m grapher.core.server --port GRAPHER_PORT"
"""

import argparse
import asyncio
import pkg_resources
import json
import re

from websockets.server import serve

from grapher.core.errors import GraphException
from grapher.core.constants import (
    INCORRECT_PARAMETERS, NOT_FOUND, ALREADY_DONE, DRIVER_NOT_LOADED,
    DONE, LOAD_VERB, UNLOAD_VERB
)


HOST = 'localhost'
PORT = 9999


PLUGINS = {
    entry_point.name: entry_point.load()
    for entry_point
    in pkg_resources.iter_entry_points('grapher.drivers')
}


class WebSocketHandler:
    _driver = None

    def __init__(self, request):
        self.request = request

    @staticmethod
    def _get_verb(line):
        verb = line.strip().split(' ')[0]
        data = line.strip().split(' ')[1:]
        return verb.lower(), ' '.join(data).strip()

    @staticmethod
    def _parse_args(data):
        # Parameters to a command can be passed in this format:
        # DATA types=a,b&&show=False.
        return {
            arg.split('=', maxsplit=1)[0].lower():
                arg.split('=', maxsplit=1)[1]
            for arg in data.split('&&')
        }

    def _call_driver_method(self, method, args):
        # TODO. Find a more elegant way to discover only exposed methods.
        # TODO. Find a more elegant way to pass parameters as a dict.
        return getattr(self._driver, re.sub('[^0-9a-zA-Z]+', '__', method))(**args)

    async def _send_data(self, obj):
        await self.request.send(json.dumps(obj, default=str) + '\n')

    def load_driver(self, name):
        if self._driver is None:
            try:
                self._driver = PLUGINS[name.strip()]()
            except KeyError:
                raise GraphException(NOT_FOUND)
        else:
            raise GraphException(ALREADY_DONE)

    def unload_driver(self):
        if self._driver is not None:
            self._driver = None
        else:
            raise GraphException(ALREADY_DONE)

    async def reply(self, obj):
        try:
            await self._send_data(obj)
        except BaseException as exc:
            print('Socket Error:', exc)

    async def error_reply(self, status):
        await self.reply({'error': status})

    async def info_reply(self, status):
        await self.reply({'info': status})

    async def handle(self, message):
        try:
            verb, data = self._get_verb(message)
            print('GOT REQUEST: verb - {}, data = {}'.format(verb, data))
            if not verb:
                await self.error_reply(NOT_FOUND)
            if verb == LOAD_VERB:
                self.load_driver(data)
                await self.info_reply(DONE)
            elif verb == UNLOAD_VERB:
                self.unload_driver()
                await self.info_reply(DONE)
            elif verb != LOAD_VERB and self._driver is None:
                await self.error_reply(DRIVER_NOT_LOADED)
            else:
                args = {}
                if data:
                    try:
                        args = self._parse_args(data)
                    except IndexError:
                        await self.error_reply(INCORRECT_PARAMETERS)
                try:
                    result = self._call_driver_method(verb, args)
                    if result:
                        async for res in result:
                            if 'error' in res:
                                raise GraphException(res['error'])
                            else:
                                # TODO. That kills browser. We need to send data in batches.
                                await self.reply(res)
                    await self.info_reply(DONE)
                except AttributeError:
                    import traceback
                    print(traceback.format_exc())
                    await self.error_reply(NOT_FOUND)
                except TypeError:
                    import traceback
                    print(traceback.format_exc())
                    await self.error_reply(INCORRECT_PARAMETERS)
        except GraphException as error:
            await self.error_reply(error.message)


async def ws_handler(websocket, path):
    handler = WebSocketHandler(websocket)
    async for command in websocket:
        await handler.handle(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage='Usage: python3 -m grapher.core.server --port PORT_NUMBER',
        description=(
            'Runs a Grapher server on a specified port or 9999 if port number was not provided.'
        )
    )
    parser.add_argument(
        '-p', '--port', dest='port', type=int
    )
    args = parser.parse_args()

    port = args.port or PORT
    asyncio.get_event_loop().run_until_complete(serve(ws_handler, HOST, port))
    asyncio.get_event_loop().run_forever()
