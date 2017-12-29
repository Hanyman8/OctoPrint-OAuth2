
from flask.ext.login import UserMixin
from flask.ext.principal import Identity

import logging
import os
import yaml
import uuid


from octoprint.users import UserManager
from octoprint.settings import settings
from octoprint.users import User
from octoprint.users import UnknownUser
from octoprint.users import UserAlreadyExists

from octoprint.util import atomic_write, to_str, deprecated


#def user_factory_hook(components, settings, *args, **kwargs):
#	return FilebasedUserManager

class FilebasedUserManager(UserManager):
	def __init__(self):

		print("222222")
		logging.getLogger(__name__).info("#######2222######")
		UserManager.__init__(self)

		userfile = settings().get(["accessControl", "userfile"])
		if userfile is None:
			userfile = os.path.join(settings().getBaseFolder("base"), "users.yaml")
		self._userfile = userfile
		self._users = {}
		self._dirty = False

		self._customized = None
		self._load()

	def _load(self):
		if os.path.exists(self._userfile) and os.path.isfile(self._userfile):
			self._customized = True
			with open(self._userfile, "r") as f:
				data = yaml.safe_load(f)
				for name in data.keys():
					attributes = data[name]
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

	def addUser(self, username, password, active=False, roles=None, apikey=None, overwrite=False):
		if not roles:
			roles = ["user"]

		if username in self._users.keys() and not overwrite:
			raise UserAlreadyExists(username)

		self._users[username] = User(username, UserManager.createPasswordHash(password), active, roles, apikey=apikey)
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

	def findUser(self, userid=None, apikey=None, session=None):
		user = UserManager.findUser(self, userid=userid, session=session)

		if user is not None:
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

	def getAllUsers(self):
		return map(lambda x: x.asDict(), self._users.values())

	def hasBeenCustomized(self):
		return self._customized
