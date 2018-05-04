import time
import threading
import pytest
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
from octoprint_oauth2.fake_oauth2_server import serve_forever


CLIENT_ID = "abc"
CLIENT_SECRET = "xyz"
REDIRECT_URI = "http://0.0.0.0:5000/"

GOOD_USERNAME = "good"
BAD_USERNAME = "bad"

GOOD_CODE = "goodcode"
BAD_CODE = "badcode"

GOOD_ACCESS_TOKEN = "goodAT"
BAD_ACCESS_TOKEN = "badAT"


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
	access_token = OAuthbasedUserManager.get_token(user_manager, GOOD_CODE)
	assert access_token == GOOD_ACCESS_TOKEN
	assert access_token != None
	assert access_token != BAD_ACCESS_TOKEN

def test_get_access_token_bad():
	user_manager = init_usermanager()
	access_token = OAuthbasedUserManager.get_token(user_manager, BAD_CODE)
	assert access_token == None
	assert access_token != GOOD_ACCESS_TOKEN
	assert access_token != ""












