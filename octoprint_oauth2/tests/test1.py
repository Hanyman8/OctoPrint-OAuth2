import time
import threading
import pytest
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
import octoprint_oauth2.oauth_user_manager
from octoprint_oauth2.fake_oauth2_server import serve_forever
import mock
import flexmock
from octoprint_oauth2 import user_factory_hook

def init_usermanager():
	tmp = OAuthbasedUserManager.__new__(OAuthbasedUserManager)
	tmp.REDIRECT_URI = "tmp"
	tmp.CLIENT_ID = "abc"
	tmp.CLIENT_SECRET = "xyz"
	tmp.TOKEN_HEADERS = ""
	tmp.USERNAME_KEY = "login"
	tmp.PATH_USER_INFO = "http://0.0.0.0:8080/user"
	tmp.PATH_FOR_TOKEN = "http://0.0.0.0:8080/token"
	return tmp

def test_get_access_token_good():
	user_manager = init_usermanager()
	access_token = OAuthbasedUserManager.get_token(user_manager, "goodcode")
	assert "goodAT" in access_token
