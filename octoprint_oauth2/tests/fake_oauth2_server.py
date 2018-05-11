# coding=utf-8
'''
Fake OAuth2 provider
Inspired by Miro Hroncok
'''
from __future__ import print_function

import SocketServer
import json
import socket
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler

from octoprint_oauth2.tests.constants_for_tests import CLIENT_ID, GOOD_CODE, GOOD_ACCESS_TOKEN, \
    GOOD_ACCESS_TOKEN_QUERY_KEY, GOOD_USERNAME_KEY, GOOD_USERNAME, \
    BAD_ACCESS_TOKEN_QUERY_KEY


def parse_info(info):
    """
    Parse info
    """
    print("parser")
    parsed = urlparse.urlparse(info)
    data = dict(urlparse.parse_qsl(parsed.query))
    print(data)
    return data


def fake_resource_server(info):
    """
    Simulate fake resource server for integration tests
    """
    print(info)

    TokenHandler.connected_clients += 1
    print(TokenHandler.connected_clients)

    # hack for testing to add roles to test_user in test_integration.py
    if TokenHandler.connected_clients < 4:
        data = {'username': 'test_admin'}
    else:
        data = {'username': 'test_user'}

    return data


def fake_access_token(info):
    """
    Simulate authorization server
    """
    print("Making fake access_token")

    # check code presence
    try:
        code = info['code']
    except KeyError:
        data = {'error': 'code missing',
                'error_description': 'code missing'}
        return data

    # check if good code is sent
    if code == GOOD_CODE:
        print("Sending good acces_token, code OK")
        data = {'access_token': GOOD_ACCESS_TOKEN}
    else:
        print("Sending error, code not OK")
        data = {'error': 'invalid_code',
                'error_description': 'invalid_code'}
    return data


def fake_user_info(info):
    """
    Simulate resource server for unit tests
    """
    try:
        if info[GOOD_ACCESS_TOKEN_QUERY_KEY] == GOOD_ACCESS_TOKEN:
            print("Token and key is OK")
            data = {GOOD_USERNAME_KEY: GOOD_USERNAME}
            return data
    except KeyError:
        try:
            if info[BAD_ACCESS_TOKEN_QUERY_KEY] is not None:
                print("Bad access token query key")
                return None
        except KeyError:
            print("Bad access token")
            return None


def authorize(info):
    """
    Simulate login user on third party server
    """
    print(info['client_id'])
    try:
        if info['client_id'] == CLIENT_ID:
            return {'code': GOOD_CODE}
    except ValueError:
        pass

    return {'error': 'invalid_id',
            'error_description': 'invalid client id'}


class TokenHandler(BaseHTTPRequestHandler):
    """
    TokenHandler
    """
    # hack for fake resource server
    connected_clients = 0

    def _set_headers(self):
        """
        Set headers
        :return:
        """
        self.send_response(200)
        self.send_header('Content-Type', 'application/json;charset=UTF-8')
        self.end_headers()

    def do_POST(self):
        """
        Do POST method
        """
        self._set_headers()

        if self.path.startswith('/token'):
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data_string = "/token?" + data_string
            # print("datastring = " + data_string )
            info = parse_info(data_string)
            data = fake_access_token(info)
        else:
            data = {"error": "no url here"}

        # print("POST sending data:")
        # print(data)
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """
        Do GET method
        """
        self._set_headers()
        if self.path.startswith('/authorize'):
            info = parse_info(self.path)
            data = authorize(info)
        elif self.path.startswith('/user'):
            # print("-----2222------")
            # print(self.path)
            info = parse_info(self.path)
            data = fake_user_info(info)

        # this server as fake resource server for selenium integration tests
        elif self.path.startswith('/api/login'):

            print("-----api/user------")
            info = parse_info(self.path)
            data = fake_resource_server(info)
        else:
            # print("-----3333------")
            print(self.path)
            data = None

        # print("GET sending data:")
        # print(data)
        self.wfile.write(json.dumps(data).encode())


class TCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def serve_forever(port=8080):
    print("starting server on port " + str(port))
    tokenserver = TCPServer(('', port), TokenHandler)
    tokenserver.serve_forever()


if __name__ == '__main__':
    serve_forever()
