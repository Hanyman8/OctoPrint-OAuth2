# coding=utf-8
'''
The MIT License (MIT)

Copyright (c) 2016 Miro Hrončok <miro@hroncok.cz>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import SocketServer
import urlparse
import pprint
from urlparse import urlparse, parse_qs
from constants_for_tests import *
import requests


def parse_info(info):
	# print("parser")
	parsed = urlparse.urlparse(info)
	data = dict(urlparse.parse_qsl(parsed.query))
	return data


class TokenHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-Type', 'application/json;charset=UTF-8')
		self.end_headers()

	def print_all(self):
		# print(self.client_address)
		print(self.command)

	def authorize(self, info):
		print (info['client_id'])
		try:
			if info['client_id'] == CLIENT_ID:
				return {'code': GOOD_CODE
						# 'state': info['state']
						}
		except:
			pass
		# print(params)

		return {'error': 'invalid_id',
				'error_description': 'invalid client id'}

	def fake_access_token(self, info):
		print("Making fake access_token")

		# check code presence
		try:
			code = info['code']
		except:
			data = {'error': 'code missing',
					'error_description': 'code missing'}
			return data

		# check if good code is sent
		if info['code'] == GOOD_CODE:
			print("Sending good acces_token, code OK")
			data = {'access_token': GOOD_ACCESS_TOKEN
					# 'state': info['state']
					}
		else:
			print("Sending error, code not OK")
			data = {'error': 'invalid_code',
					'error_description': 'invalid_code'}

		return data

	# access token input
	def fake_user_info(self, info):
		# get username
		print("--------info--------")
		print(info)
		print("--------------------")

		data = {'login': GOOD_USERNAME}

		# data = info
		# data = {'username': username}

		return data

	def do_POST(self):
		print("POST method")
		self._set_headers()

		if self.path.startswith('/token'):
			data_string = self.rfile.read(int(self.headers['Content-Length']))
			data_string = "/token?" + data_string
			info = parse_info(data_string)
			data = self.fake_access_token(info)
		else:
			data = {"error": "no url here"}

		print("POST sending data:")
		print(data)
		self.wfile.write(json.dumps(data).encode())

	def do_GET(self):
		print("GET method")
		self._set_headers()
		if self.path.startswith('/authorize'):
			info = parse_info(self.path)
			data = self.authorize(info)
		elif self.path.startswith('/user'):
			print("-----2222------")
			print(self.path)
			print (self.headers)
			query = parse_qs(urlparse(self.path).query)
			print query
			# print (self.responses)
			print (self.connection)
			# length = int(self.headers.getheader('content-length'))
			# print ("length = " + length)
			# data_string = urlparse.parse_qs(self)
			pprint.pprint (self)
			# data_string = self.rfile.read(length)
			# print data_string
			info = parse_info(self.path)
			data = self.fake_user_info(info)
		else:
			print("-----3333------")
			print(self.path)
			data = None

		print("GET sending data:")
		print(data)
		self.wfile.write(json.dumps(data).encode())


class TCPServer(SocketServer.ForkingTCPServer):
	def server_bind(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.server_address)


def serve_forever(port=8080):
	print("starting server on port " + str(port))
	tokenserver = TCPServer(('', port), TokenHandler)
	tokenserver.serve_forever()


if __name__ == '__main__':
	serve_forever()
