import threading

import os
from requests_oauthlib import OAuth2Session

from constants_for_tests import *
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
from octoprint_oauth2.tests.fake_oauth2_server import serve_forever
from octoprint.users import *
import octoprint.server
from  pytest_mock import mocker


# time.sleep(1)

class TestUserManager:
	@classmethod
	def setup_class(cls):
		os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
		thr = threading.Thread(target=serve_forever, args=[8080])
		thr.daemon = True
		thr.start()

	def tmp(self):
		return True

	def init_user_manager(self):
		user_manager = OAuthbasedUserManager.__new__(OAuthbasedUserManager)
		user_manager.REDIRECT_URI = GOOD_REDIRECT_URI
		user_manager.CLIENT_ID = CLIENT_ID
		user_manager.CLIENT_SECRET = CLIENT_SECRET
		user_manager.TOKEN_HEADERS = {"Accept": "application/json"}
		user_manager.USERNAME_KEY = GOOD_USERNAME_KEY
		user_manager.ACCESS_TOKEN_QUERY_KEY = GOOD_ACCESS_TOKEN_QUERY_KEY
		user_manager.PATH_USER_INFO = PATH_USER_INFO
		user_manager.PATH_FOR_TOKEN = PATH_FOR_TOKEN

		# mock some OctoPrint values, cleanup session needs callable
		user_manager._cleanup_sessions = self.tmp
		user_manager._session_users_by_session = {}
		user_manager._sessionids_by_userid = {}
		user_manager._users = {}
		user_manager._save = self.tmp
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

	def test_passing_redirect_uri(self):
		user_manager = self.init_user_manager()

		# set temporarily bad redirect URI
		user_manager.REDIRECT_URI = BAD_REDIRECT_URI
		assert user_manager.REDIRECT_URI == BAD_REDIRECT_URI

		# use checkPassword method to set good redirect URI
		assert user_manager.checkPassword("not_used", GOOD_REDIRECT_URI) is True
		assert user_manager.REDIRECT_URI == GOOD_REDIRECT_URI
		assert user_manager.REDIRECT_URI != BAD_REDIRECT_URI

		# set it back to bad
		assert user_manager.checkPassword("not_used", BAD_REDIRECT_URI)
		assert user_manager.REDIRECT_URI != GOOD_REDIRECT_URI
		assert user_manager.REDIRECT_URI == BAD_REDIRECT_URI

	def test_login_session(self):
		user_manager = self.init_user_manager()
		user = User(GOOD_USERNAME, "1234", 1, ["user"])
		# make session
		user = SessionUser(user)
		user_check = user_manager.login_user(user)
		assert isinstance(user_check, SessionUser)
		assert isinstance(user_check, User)
		assert user_check.get_id() == GOOD_USERNAME
		assert user_check.get_id() != BAD_USERNAME
		assert user.is_user() is True

	def test_oauth2_login_good(self):
		user_manager = self.init_user_manager()
		# code is passed as argument from server api
		user = User(GOOD_CODE, "1234", 1, ["user"])

		# mock settings from config.yaml
		user_manager.oauth2 = {GOOD_REDIRECT_URI: {"client_id": CLIENT_ID,
												   "client_secret": CLIENT_SECRET}}
		# user is not instance of SessionUser
		assert not isinstance(user, SessionUser)

		user_check = user_manager.login_user(user)
		assert user_check.get_id() == GOOD_USERNAME
		# user should have session
		assert isinstance(user_check, SessionUser)
		assert user_check.get_id() != BAD_USERNAME
		assert user_check.get_id() is not None
