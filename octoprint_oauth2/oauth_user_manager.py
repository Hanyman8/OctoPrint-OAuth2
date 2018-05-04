from octoprint.users import *
import octoprint.settings
import octoprint
import requests
import requests.auth
import urllib, json


class OAuthbasedUserManager(FilebasedUserManager):
	def __init__(self, components, settings):
		logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
		self._components = components
		self._settings = settings
		self.oauth2 = self._settings.get(["plugins", "oauth2"])
		FilebasedUserManager.__init__(self)
		FilebasedUserManager.__init__(self)

	def logout_user(self, user):
		logging.getLogger("octoprint.plugins." + __name__).info("OAuth Logging out")
		UserManager.logout_user(self, user)

	def get_token(self, code):

		post_data = {"grant_type": "authorization_code",
					 "code": code,
					 "redirect_uri": self.REDIRECT_URI,
					 "client_id": self.CLIENT_ID,
					 "client_secret": self.CLIENT_SECRET
					 }  # json required

		response = requests.post(self.PATH_FOR_TOKEN,
								 data=post_data,
								 headers=self.TOKEN_HEADERS)

		try:
			token_json = response.json()
		except ValueError:
			logging.getLogger("octoprint.plugins." + __name__).error("JSON required, perhaps you forgot to specific it with token headers")
			return None

		try:
			# token is OK
			access_token = token_json["access_token"]
			return access_token
		except KeyError:
			try:
				error = token_json["error"]
				logging.getLogger("octoprint.plugins." + __name__).error("Error of access token: " + error)
			except:
				logging.getLogger("octoprint.plugins." + __name__).error("Error of access token, error message not found")

		return None

	def get_username(self, access_token):

		params = {
			"access_token": access_token
		}

		response = requests.get(self.PATH_USER_INFO,
								params=params)

		data = response.json()

		try:
			login = data[self.USERNAME_KEY]
			return login
		except KeyError:
			pass

		return None

	def login_user(self, user):

		self._cleanup_sessions()

		if user is None:
			return

		# LocalProxy.

		if isinstance(user, LocalProxy):
			user = user._get_current_object()
			return user

		if not isinstance(user, User):
			return None


		if not isinstance(user, SessionUser):
			code = user.get_id()

			self.CLIENT_ID = self.oauth2[self.REDIRECT_URI]["client_id"]
			self.CLIENT_SECRET = self.oauth2[self.REDIRECT_URI]["client_secret"]
			self.PATH_FOR_TOKEN = self.oauth2["token_path"]
			self.PATH_USER_INFO = self.oauth2["user_info_path"]
			self.USERNAME_KEY = self.oauth2["username_key"]
			try:
				self.TOKEN_HEADERS = self.oauth2["token_headers"]
			except KeyError:
				self.TOKEN_HEADERS = None
			access_token = self.get_token(code)

			if access_token is None:
				return None

			username = self.get_username(access_token)
			user = FilebasedUserManager.findUser(self,username)
			if username is None:
				logging.getLogger("octoprint.plugins." + __name__).error("Username none")
				return None

			if user is None:
				self.addUser(username, "", True, ["user"])
				user = self.findUser(username)


		if not isinstance(user, SessionUser):
			user = SessionUser(user)

		self._session_users_by_session[user.session] = user

		userid = user.get_id()
		if not userid in self._sessionids_by_userid:
			self._sessionids_by_userid[userid] = set()

		self._sessionids_by_userid[userid].add(user.session)
		return user

	def addUser(self, username, password, active=False, roles=None, apikey=None, overwrite=False):
		if not roles:
			roles = ["user"]

		if username in self._users.keys() and not overwrite:
			raise UserAlreadyExists(username)

		self._users[username] = User(username, password, active, roles, apikey=apikey)
		self._dirty = True
		self._save()

	def checkPassword(self, username, password):
		logging.getLogger("octoprint.plugins." + __name__).info("Logging in via OAuth 2.0")
		self.REDIRECT_URI = password
		return True

	def findUser(self, userid=None, apikey=None, session=None):

		user = FilebasedUserManager.findUser(self, userid, apikey, session)
		if user is not None:
			return user

		# making temporary user because of implementation of api
		# and we need to pass our code from OAuth to login_user
		# api login could be found in server/api/__init__.py
		user = User(userid, "", 1, ["user"])
		return user
