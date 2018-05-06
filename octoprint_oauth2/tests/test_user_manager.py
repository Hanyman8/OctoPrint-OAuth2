import threading

import os
from requests_oauthlib import OAuth2Session

from constants_for_tests import *
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
from octoprint_oauth2.tests.fake_oauth2_server import serve_forever
import octoprint_oauth2.tests.constants_for_tests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# time.sleep(1)

class TestUserManager:
	@classmethod
	def setup_class(cls):
		print ("fixture")
		thr = threading.Thread(target=serve_forever, args=[8080])
		thr.daemon = True
		thr.start()

	def init_user_manager(self):
		user_manager = OAuthbasedUserManager.__new__(OAuthbasedUserManager)
		user_manager.REDIRECT_URI = "tmp"
		user_manager.CLIENT_ID = "abc"
		user_manager.CLIENT_SECRET = "xyz"
		user_manager.TOKEN_HEADERS = {"Accept": "application/json"}
		user_manager.USERNAME_KEY = GOOD_USERNAME_KEY
		user_manager.ACCESS_TOKEN_QUERY_KEY = GOOD_ACCESS_TOKEN_QUERY_KEY
		user_manager.PATH_USER_INFO = "http://0.0.0.0:8080/user"
		user_manager.PATH_FOR_TOKEN = "http://0.0.0.0:8080/token"
		return user_manager


	def test_get_access_token_good(self):
		user_manager = self.init_user_manager()
		oauth2_session = OAuth2Session(user_manager.CLIENT_ID, redirect_uri=user_manager.REDIRECT_URI)
		access_token = user_manager.get_token(oauth2_session, GOOD_CODE)
		assert access_token == GOOD_ACCESS_TOKEN
		assert access_token != None
		assert access_token != BAD_ACCESS_TOKEN

	def test_get_access_token_bad(self):
		user_manager = self.init_user_manager()
		oauth2_session = OAuth2Session(user_manager.CLIENT_ID, redirect_uri=user_manager.REDIRECT_URI)
		access_token = user_manager.get_token(oauth2_session, BAD_CODE)
		assert access_token == None
		assert access_token != GOOD_ACCESS_TOKEN
		assert access_token != ""

	def test_get_username_good(self):
		user_manager = self.init_user_manager()
		oauth2_session = OAuth2Session(user_manager.CLIENT_ID, redirect_uri=user_manager.REDIRECT_URI)
		oauth2_session.access_token = GOOD_ACCESS_TOKEN
		username = user_manager.get_username(oauth2_session)
		print(username)
		assert username == GOOD_USERNAME
		assert username != None
		assert username != ""

	def test_get_username_bad_access_token(self):
		user_manager = self.init_user_manager()
		oauth2_session = OAuth2Session(user_manager.CLIENT_ID, redirect_uri=user_manager.REDIRECT_URI)
		oauth2_session.access_token = BAD_ACCESS_TOKEN
		username = user_manager.get_username(oauth2_session)
		assert username is None
		assert username != ""
		assert username != GOOD_USERNAME

	def test_get_username_bad_query_key(self):
		user_manager = self.init_user_manager()
		oauth2_session = OAuth2Session(user_manager.CLIENT_ID, redirect_uri=user_manager.REDIRECT_URI)
		user_manager.ACCESS_TOKEN_QUERY_KEY = BAD_ACCESS_TOKEN_QUERY_KEY
		oauth2_session.access_token = GOOD_ACCESS_TOKEN
		username = user_manager.get_username(oauth2_session)
		assert username is None
		assert username != ""
		assert username != GOOD_USERNAME
