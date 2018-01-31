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
import socketserver
import pkg_resources
import json
import re

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


_driver = None


class GraphTCPHandler(socketserver.BaseRequestHandler):
    @staticmethod
    def get_verb(line):
        verb = line.strip().split(b' ')[0]
        data = line.strip().split(b' ')[1:]
        return verb.lower(), b' '.join(data).strip()

    @staticmethod
    def load_driver(name):
        global _driver
        if _driver is None:
            try:
                _driver = PLUGINS[name.strip().decode()]()
            except KeyError:
                raise GraphException(NOT_FOUND)
        else:
            raise GraphException(ALREADY_DONE)

    @staticmethod
    def unload_driver():
        global _driver
        if _driver is not None:
            _driver = None
        else:
            raise GraphException(ALREADY_DONE)

    def load_driver_method(self, verb, data):
        global _driver
        args = {}
        if data:
            try:
                # Parameters to a command can be passed in this format:
                # DATA types=a,b&&show=False.
                args = {
                    arg.decode().split('=', maxsplit=1)[0].lower():
                        arg.decode().split('=', maxsplit=1)[1]
                    for arg in data.split(b'&&')
                }
            except IndexError:
                self.error_reply(INCORRECT_PARAMETERS)
        try:
            # TODO. Find a more elegant way to discover only exposed methods.
            # TODO. Find a more elegant way to pass parameters as a dict.
            response = getattr(_driver, re.sub('[^0-9a-zA-Z]+', '__', verb.decode()))(**args)
            if response:
                for r in response:
                    self.reply(r)
            self.info_reply(DONE)
        except AttributeError:
            self.error_reply(NOT_FOUND)
        except TypeError as e:
            print(e)
            self.error_reply(INCORRECT_PARAMETERS)

    def reply(self, obj):
        self.request.sendall(json.dumps(obj, default=str).encode() + b'\n')

    def error_reply(self, status):
        try:
            self.request.sendall(json.dumps({'error': status.decode()}).encode() + b'\n')
        except BaseException as exc:
            print('Socket Error:', exc)

    def info_reply(self, status):
        try:
            self.request.sendall(json.dumps({'info': status.decode()}).encode() + b'\n')
        except BaseException as exc:
            print('Socket Error:', exc)

    def handle(self):
        while True:
            try:
                line = self.request.recv(1024).strip()
                verb, data = self.get_verb(line)
                print('GOT REQUEST:', verb)
                if not verb:
                    self.error_reply(NOT_FOUND)
                if verb == LOAD_VERB:
                    self.load_driver(data)
                    self.info_reply(DONE)
                elif verb == UNLOAD_VERB:
                    self.unload_driver()
                    self.info_reply(DONE)
                elif verb != LOAD_VERB and _driver is None:
                    self.error_reply(DRIVER_NOT_LOADED)
                else:
                    self.load_driver_method(verb, data)
            except GraphException as error:
                self.error_reply(error.message)


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

    with socketserver.TCPServer((HOST, port), GraphTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
