import requests
from requests_oauthlib import OAuth2Session

from octoprint.users import *


class OAuthbasedUserManager(FilebasedUserManager):
	def __init__(self, components, settings):
		logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
		self._components = components
		self._settings = settings

		# Get data from config file
		self.oauth2 = self._settings.get(["plugins", "oauth2"])
		self.PATH_FOR_TOKEN = self.oauth2["token_path"]
		self.PATH_USER_INFO = self.oauth2["user_info_path"]
		self.USERNAME_KEY = self.oauth2["username_key"]
		self.ACCESS_TOKEN_QUERY_KEY = self.oauth2["access_token_query_key"]
		try:
			self.TOKEN_HEADERS = self.oauth2["token_headers"]
		except KeyError:
			self.TOKEN_HEADERS = None

		# These three will be initialized later.
		# CLIENT_ID and CLIENT_SECRET need GOOD_REDIRECT_URI for proper initialization
		self.CLIENT_ID = None
		self.CLIENT_SECRET = None
		self.REDIRECT_URI = None

		# Init FilebasedUserManager, other methods are needed for OctoPrint
		FilebasedUserManager.__init__(self)

	def logout_user(self, user):
		logging.getLogger("octoprint.plugins." + __name__).info("OAuth Logging out")
		UserManager.logout_user(self, user)

	def get_token(self, oauth2_session, code):
		print ("Get access token, code = " + code)
		token_json = oauth2_session.fetch_token(self.PATH_FOR_TOKEN,
												authorization_response="authorization_code",
												code=code,
												client_id=self.CLIENT_ID,
												client_secret=self.CLIENT_SECRET,
												headers=self.TOKEN_HEADERS)

		try:
			print ("1234")

			print token_json
			try:
				# token is OK
				access_token = token_json["access_token"]
				print(access_token)
				return access_token
			except KeyError:
				try:
					error = token_json["error"]
					logging.getLogger("octoprint.plugins." + __name__).error("Error of access token: " + error)
				except:
					logging.getLogger("octoprint.plugins." + __name__).error("Error of access token, error message not found")

		except:
			logging.getLogger("octoprint.plugins." + __name__).error("Bad authorization_code")

		return None

	def get_username(self, oauth2_session):


		try:
			# GET user data from resource server
			params = {
				self.ACCESS_TOKEN_QUERY_KEY: oauth2_session.access_token
			}
			response = requests.get(self.PATH_USER_INFO, params=params)
			data = response.json()

			# Try if data contains USERNAME_KEY from config file
			try:
				login = data[self.USERNAME_KEY]
				return login
			except KeyError:
				logging.getLogger("octoprint.plugins." + __name__).error("User data does not contain username key, you can try to find it here:")
				logging.getLogger("octoprint.plugins." + __name__).error(data)
		except:
			logging.getLogger("octoprint.plugins." + __name__).error(
				"error")

		return None

	def login_user(self, user):
		self._cleanup_sessions()

		if user is None:
			return

		if isinstance(user, LocalProxy):
			user = user._get_current_object()
			return user

		if not isinstance(user, User):
			return None

		if not isinstance(user, SessionUser):
			code = user.get_id()

			self.CLIENT_ID = self.oauth2[self.REDIRECT_URI]["client_id"]
			self.CLIENT_SECRET = self.oauth2[self.REDIRECT_URI]["client_secret"]
			oauth2_session = OAuth2Session(self.CLIENT_ID,
										   redirect_uri=self.REDIRECT_URI)
			access_token = self.get_token(oauth2_session, code)

			if access_token is None:
				return None

			username = self.get_username(oauth2_session)
			user = FilebasedUserManager.findUser(self, username)
			if username is None:
				logging.getLogger("octoprint.plugins." + __name__).error("Username none")
				return None

			if user is None:
				self.addUser(username, "", True, ["user"])
				user = self.findUser(username)

		if not isinstance(user, SessionUser):
			user = SessionUser(user)

		self._session_users_by_session[user.session] = user

		user_id = user.get_id()
		if not user_id in self._sessionids_by_userid:
			self._sessionids_by_userid[user_id] = set()

		self._sessionids_by_userid[user_id].add(user.session)
		return user

	def addUser(self, username, password, active=False, roles=None, apikey=None, overwrite=False):
		if not roles:
			roles = ["user"]

		if username in self._users.keys() and not overwrite:
			raise UserAlreadyExists(username)

		# Add user with password and not creating passwordhash.
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
