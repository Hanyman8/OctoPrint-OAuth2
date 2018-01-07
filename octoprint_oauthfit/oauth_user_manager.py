
from flask.ext.login import UserMixin
from flask.ext.principal import Identity

import logging
import os
import yaml
import uuid

import wrapt

from werkzeug.local import LocalProxy
from octoprint.users import UserManager
from octoprint.settings import settings
from octoprint.users import User
from octoprint.users import UnknownUser
from octoprint.users import UserAlreadyExists

from octoprint.util import atomic_write, to_str, deprecated


#def user_factory_hook(components, settings, *args, **kwargs):
#	return OAuthbasedUserManager

class OAuthbasedUserManager(UserManager):
	def __init__(self):

		logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
		UserManager.__init__(self)

		userfile = settings().get(["accessControl", "userfile"])
		#logging.getLogger("octoprint.plugins." + __name__).info(userfile.items() + "  <<<< Userfile")
		if userfile is None:
			logging.getLogger("octoprint.plugins." + __name__).info("#######3333 - no userfile ######")
			userfile = os.path.join(settings().getBaseFolder("base"), "users2.yaml")
			print(userfile)
		self._userfile = userfile
		self._users = {}
		self._dirty = False

		self._customized = None
		self._load()

	def _load(self):
		if os.path.exists(self._userfile) and os.path.isfile(self._userfile):
			logging.getLogger("octoprint.plugins." + __name__).info("#######4444 - path to new userfile exists ######")
			self._customized = True
			with open(self._userfile, "r") as f:
				data = yaml.safe_load(f)
				for name in data.keys():
					attributes = data[name]
					print(data.items())
					apikey = None
					if "apikey" in attributes:
						apikey = attributes["apikey"]
					settings = dict()
					if "settings" in attributes:
						settings = attributes["settings"]
					self._users[name] = User(name, attributes["password"], attributes["active"], attributes["roles"], apikey=apikey, settings=settings)
					for sessionid in self._sessionids_by_userid.get(name, set()):
						if sessionid in self._session_users_by_session:
							self._session_users_by_session[sessionid].update_user(self._users[name])
		else:
			logging.getLogger("octoprint.plugins." + __name__).info("#######4444 - NOT Exitsting user file ######")
			self._customized = False

	def _save(self, force=False):
		if not self._dirty and not force:
			return

		data = {}
		for name in self._users.keys():
			user = self._users[name]
			data[name] = {
				"password": user._passwordHash,
				"active": user._active,
				"roles": user._roles,
				"apikey": user._apikey,
				"settings": user._settings
			}

		with atomic_write(self._userfile, "wb", permissions=0o600, max_permissions=0o666) as f:
			yaml.safe_dump(data, f, default_flow_style=False, indent="    ", allow_unicode=True)
			self._dirty = False
		self._load()

	def login_user(self, user):
		self._cleanup_sessions()

		logging.getLogger("octoprint.plugins." + __name__).info("#######5555 - My login ######")
		print(" MY LOGIN ")
		if user is None:
			return

		if isinstance(user, LocalProxy):
			user = user._get_current_object()

		if not isinstance(user, User):
			return None

		if not isinstance(user, SessionUser):
			user = SessionUser(user)

		self._session_users_by_session[user.session] = user

		userid = user.get_id()
		if not userid in self._sessionids_by_userid:
			self._sessionids_by_userid[userid] = set()

		self._sessionids_by_userid[userid].add(user.session)
		logging.getLogger("octoprint.plugins." + __name__).info("#######6666 - My login ######")

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

	def changeUserActivation(self, username, active):
		if not username in self._users.keys():
			raise UnknownUser(username)

		if self._users[username]._active != active:
			self._users[username]._active = active
			self._dirty = True
			self._save()

	def changeUserRoles(self, username, roles):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]

		removedRoles = set(user._roles) - set(roles)
		self.removeRolesFromUser(username, removedRoles)

		addedRoles = set(roles) - set(user._roles)
		self.addRolesToUser(username, addedRoles)

	def addRolesToUser(self, username, roles):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		for role in roles:
			if not role in user._roles:
				user._roles.append(role)
				self._dirty = True
		self._save()

	def removeRolesFromUser(self, username, roles):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		for role in roles:
			if role in user._roles:
				user._roles.remove(role)
				self._dirty = True
		self._save()

	def changeUserPassword(self, username, password):
		if not username in self._users.keys():
			raise UnknownUser(username)

		passwordHash = UserManager.createPasswordHash(password)
		user = self._users[username]
		if user._passwordHash != passwordHash:
			user._passwordHash = passwordHash
			self._dirty = True
			self._save()

	def changeUserSetting(self, username, key, value):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		old_value = user.get_setting(key)
		if not old_value or old_value != value:
			user.set_setting(key, value)
			self._dirty = self._dirty or old_value != value
			self._save()

	def changeUserSettings(self, username, new_settings):
		if not username in self._users:
			raise UnknownUser(username)

		user = self._users[username]
		for key, value in new_settings.items():
			old_value = user.get_setting(key)
			user.set_setting(key, value)
			self._dirty = self._dirty or old_value != value
		self._save()

	def getAllUserSettings(self, username):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		return user.get_all_settings()

	def getUserSetting(self, username, key):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		return user.get_setting(key)

	def generateApiKey(self, username):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		user._apikey = ''.join('%02X' % z for z in bytes(uuid.uuid4().bytes))
		self._dirty = True
		self._save()
		return user._apikey

	def deleteApikey(self, username):
		if not username in self._users.keys():
			raise UnknownUser(username)

		user = self._users[username]
		user._apikey = None
		self._dirty = True
		self._save()

	def removeUser(self, username):
		UserManager.removeUser(self, username)

		if not username in self._users.keys():
			raise UnknownUser(username)

		del self._users[username]
		self._dirty = True
		self._save()

	def findUserFromBase(self, userid=None, session=None):
		if session is not None:
			print("OK - session not none")
		else:
			print("BAD - session IS none")

		if session in self._session_users_by_session:
			print("OK - session in users by session")
		else:
			print("BAD - session not in users")

		if session is not None and session in self._session_users_by_session:
			user = self._session_users_by_session[session]
			if userid is None or userid == user.get_id():
				return user

		return None

	def findUser(self, userid=None, apikey=None, session=None):

		user = self.findUserFromBase(userid=userid, session=session)

		print("trying t find user")

		if user is not None:
			print("  *** USER FOUND ***" + user.get_id())
			return user

		if userid is not None:
			if userid not in self._users.keys():
				return None
			return self._users[userid]

		elif apikey is not None:
			for user in self._users.values():
				if apikey == user._apikey:
					return user
			return None

		else:
			return None

	def checkPassword(self, username, password):
		print("Checking password")
		user = self.findUser(username)
		if not user:
			print("Not user")
			return False

		if user.check_password(password):
			# new hash matches, correct password
			return True
		else:
			return False

	def getAllUsers(self):
		return map(lambda x: x.asDict(), self._users.values())

	def hasBeenCustomized(self):
		return self._customized

class SessionUser(wrapt.ObjectProxy):
	def __init__(self, user):
		print(" MAKING session user")
		wrapt.ObjectProxy.__init__(self, user)

		import string
		import random
		import time
		chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
		self._self_session = "".join(random.choice(chars) for _ in range(10))
		self._self_created = time.time()

	@property
	def session(self):
		return self._self_session

	@property
	def created(self):
		return self._self_created

	@deprecated("SessionUser.get_session() has been deprecated, use SessionUser.session instead", since="1.3.5")
	def get_session(self):
		return self.session

	def update_user(self, user):
		self.__wrapped__ = user

	def __repr__(self):
		return "SessionUser({!r},session={},created={})".format(self.__wrapped__, self.session, self.created)

class DummyUser(User):
	def __init__(self):
		User.__init__(self, "dummy", "", True, UserManager.valid_roles)

	def check_password(self, passwordHash):
		return True

class DummyIdentity(Identity):
	def __init__(self):
		Identity.__init__(self, "dummy")

def dummy_identity_loader():
	return DummyIdentity()


##~~ Apiuser object to use when global api key is used to access the API


class ApiUser(User):
	def __init__(self):
		User.__init__(self, "_api", "", True, UserManager.valid_roles)
