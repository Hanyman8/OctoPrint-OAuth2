import logging
import os
import sys
import urllib
import urlparse
import json
import signal

from multiprocessing.process import Process
from wsgiref.simple_server import make_server, WSGIRequestHandler

from oauth2 import Provider
from oauth2.error import UserNotAuthenticated
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.grant import AuthorizationCodeGrant


class OAuthRequestHandler(WSGIRequestHandler):
	"""
    Request handler that enables formatting of the log messages on the console.
    This handler is used by the python-oauth2 application.
    """

	def address_string(self):
		return "python-oauth2"


class TestSiteAdapter(AuthorizationCodeGrantSiteAdapter):
	"""
    This adapter renders a confirmation page so the user can confirm the auth
    request.
    """

	CONFIRMATION_TEMPLATE = """
<html>
    <body>
        <p>
            <a href="{url}&confirm=1">confirm</a>
        </p>
        <p>
            <a href="{url}&confirm=0">deny</a>
        </p>
    </body>
</html>
    """

	def render_auth_page(self, request, response, environ, scopes, client):
		url = request.path + "?" + request.query_string
		response.body = self.CONFIRMATION_TEMPLATE.format(url=url)

		return response

	def authenticate(self, request, environ, scopes, client):
		if request.method == "GET":
			if request.get_param("confirm") == "1":
				return
		raise UserNotAuthenticated

	def user_has_denied_access(self, request):
		if request.method == "GET":
			if request.get_param("confirm") == "0":
				return True
		return False


def run_auth_server(port=8282):
	print("Starting OAuth2 server on port:" + str(port))

	client_store = ClientStore()
	client_store.add_client(client_id="abc", client_secret="xyz",
							redirect_uris=["http://0.0.0.0:5000/"])

	token_store = TokenStore()

	provider = Provider(
		access_token_store=token_store,
		auth_code_store=token_store,
		client_store=client_store,
		token_generator=Uuid4())
	provider.add_grant(
		AuthorizationCodeGrant(site_adapter=TestSiteAdapter())
	)

	app = Application(provider=provider)

	httpd = make_server('', port, app, handler_class=OAuthRequestHandler)

	httpd.serve_forever()


if __name__ == "__main__":
	run_auth_server()
