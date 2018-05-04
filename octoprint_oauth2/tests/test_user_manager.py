import time
import threading
import pytest
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
from octoprint_oauth2.fake_oauth2_server import serve_forever
import octoprint

CLIENT_ID = "abc"
CLIENT_SECRET = "xyz"
REDIRECT_URI = "http://0.0.0.0:5000/"

GOOD_USERNAME = "good"
BAD_USERNAME = "bad"

GOOD_CODE = "goodcode"
BAD_CODE = "badcode"

GOOD_ACCESS_TOKEN = "goodAT"
BAD_ACCESS_TOKEN = "badAT"


	# time.sleep(1)

class TestUserManager:
	@classmethod
	def setup_class(cls):
		print ("fixture")
		thr = threading.Thread(target=serve_forever, args=[8080])
		thr.daemon = True
		thr.start()
		cls.user_manager = OAuthbasedUserManager.__new__(OAuthbasedUserManager)
		cls.user_manager.REDIRECT_URI = "tmp"
		cls.user_manager.CLIENT_ID = "abc"
		cls.user_manager.CLIENT_SECRET = "xyz"
		cls.user_manager.TOKEN_HEADERS = ""
		cls.user_manager.USERNAME_KEY = "login"
		cls.user_manager.PATH_USER_INFO = "http://0.0.0.0:8080/user"
		cls.user_manager.PATH_FOR_TOKEN = "http://0.0.0.0:8080/token"



	def test_get_access_token_good(self):
		access_token = self.user_manager.get_token(GOOD_CODE)
		assert access_token == GOOD_ACCESS_TOKEN
		assert access_token != None
		assert access_token != BAD_ACCESS_TOKEN

	def test_get_access_token_bad(self):
		access_token = self.user_manager.get_token(BAD_CODE)
		assert access_token == None
		assert access_token != GOOD_ACCESS_TOKEN
		assert access_token != ""









