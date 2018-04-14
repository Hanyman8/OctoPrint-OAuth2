
from octoprint.users import *


class OAuthbasedUserManager(FilebasedUserManager):
	def __init__(self):

		logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
		FilebasedUserManager.__init__(self)


	def login_user(self, user):
		self._cleanup_sessions()

		logging.getLogger("octoprint.plugins." + __name__).info("#######5555 - My login ######")
		print(" MY LOGIN user = ")
		if user is None:
			print("User none")
			return

		print("2222")
		if isinstance(user, LocalProxy):
			user = user._get_current_object()

		print("333")
		if not isinstance(user, User):
			print("not instance")
			return None

		print("444")
		if not isinstance(user, SessionUser):
			user = SessionUser(user)

		self._session_users_by_session[user.session] = user

		userid = user.get_id()
		print("userid = " + userid)
		if not userid in self._sessionids_by_userid:
			self._sessionids_by_userid[userid] = set()

		self._sessionids_by_userid[userid].add(user.session)
		logging.getLogger("octoprint.plugins." + __name__).info("#######6666 - My login ######")
		print("MYLOGIN2")

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
