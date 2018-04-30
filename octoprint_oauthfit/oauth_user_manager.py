from octoprint.users import *
import octoprint.settings
import octoprint
import requests
import requests.auth
import urllib, json

import pprint

# CLIENT_ID = octoprint.plugin.plugin_settings_for_settings_plugin("oauthfit",)
# print(CLIENT_ID)

# SETTINGS = octoprint.settings.Settings.get(["plugins"])

# CLIENT_ID = SETTINGS.get("plugins")

PATH_FOR_TOKEN = "https://github.com/login/oauth/access_token"
HEADERS_FOR_TOKEN = {'Accept': 'application/json'}
PATH_USER_INFO = "https://api.github.com/user?access_token="


# "https://auth.fit.cvut.cz/oauth/token"
# token info ttps://api.github.com/user?access_token=
# https://auth.fit.cvut.cz/oauth/api/v1/tokeninfo?


class OAuthbasedUserManager(FilebasedUserManager):
	def __init__(self, components, settings):
		logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
		# print("client ID ==========" + CLIENT_ID)
		self.components = components
		self._settings = settings
		self.CLIENT_ID = self._settings.get(["plugins","oauthfit","client_id"])
		self.CLIENT_SECRET = self._settings.get(["plugins", "oauthfit", "client_secret"])
		self.REDIRECT_URI = self._settings.get(["plugins", "oauthfit", "redirect_uri"])
		# print(self.CLIENT_ID)
		# pprint.pprint(self._settings.get(["plugins"]))
		# print("CLient IS = " + self.CLIENT_ID)
		FilebasedUserManager.__init__(self)

	def logout_user(self, user):
		logging.getLogger("octoprint.plugins." + __name__).info("OAuth Logging out")
		UserManager.logout_user(self, user)

	def get_token(self, code):
		client_auth = requests.auth.HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET)
		post_data = {"grant_type": "authorization_code",
					 "code": code,
					 "redirect_uri": self.REDIRECT_URI
					 }  # json required

		response = requests.post(PATH_FOR_TOKEN,
								 auth=client_auth,
								 data=post_data,
								 headers=HEADERS_FOR_TOKEN)

		# print (response.text)

		token_json = response.json()

		# print(token_json)

		try:
			# token is OK
			access_token = token_json["access_token"]
			return access_token
		except KeyError:
			pass

		return None

	def get_username(self, access_token):
		params = {
			'token': access_token
		}

		url = PATH_USER_INFO + access_token
		# print("=====1111====" + url)
		response = urllib.urlopen(url)
		data = json.loads(response.read())

		try:
			# todo function for login, user_id
			login = data["login"]
			return login
		except KeyError:
			pass

		return None

	def login_user(self, user):
		self._cleanup_sessions()

		logging.getLogger("octoprint.plugins." + __name__).info("#######5555 - My login ######")
		# pprint.pprint(SETTINGS)
		# print(SETTINGS)
		# pprint.pprint(self._settings.serial)
		print(" MY LOGIN user ")

		if user is None:
			print("User none")
			return

		# LocalProxy.

		if isinstance(user, LocalProxy):
			print("is instance of localProxy")
			user = user._get_current_object()
			return user

		print("333")
		if not isinstance(user, User):
			print("not instance of User")
			return None

		# print("code = " + user.get_id() + "    " + user.get_name())

		if not isinstance(user, SessionUser):
			# print ("NEW USER--------")
			code = user.get_id()
			print ("logincode = " + code)
			access_token = self.get_token(code)
			if access_token is None:
				return None

			# admin role tmp
			username = self.get_username(access_token)
			# print("adding user=" + username)
			# todo funtion for recognize admin
			user = User(username, "", True, "admin")

		# print("444 token = " + self.tokens[username])

		if not isinstance(user, SessionUser):
			user = SessionUser(user)

		self._session_users_by_session[user.session] = user

		userid = user.get_id()
		# print("userid = " + userid)
		if not userid in self._sessionids_by_userid:
			self._sessionids_by_userid[userid] = set()

		self._sessionids_by_userid[userid].add(user.session)
		logging.getLogger("octoprint.plugins." + __name__).info("#######6666 - OAuth login ######")
		# print("MYLOGIN2")

		self._logger.debug("Logged in user: %r" % user)

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
		return True

	def findUser(self, userid=None, apikey=None, session=None):

		# making temporary user because of implementation of api
		user = User(userid, "", 1, "admin")
		return user
