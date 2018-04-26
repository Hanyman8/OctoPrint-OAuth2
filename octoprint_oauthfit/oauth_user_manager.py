from octoprint.users import *
import requests
import requests.auth
import urllib, json

CLIENT_ID = "1cb4ca8a2734ba9723ff"
CLIENT_SECRET = "678089f05cb59c524febf431e00837bb8f70a01d"
REDIRECT_URI = "http://0.0.0.0:5000/"
PATH_FOR_TOKEN = "https://github.com/login/oauth/access_token"
# "https://auth.fit.cvut.cz/oauth/token"
# token info ttps://api.github.com/user?access_token=
username=""


def get_token(code):
    # headers={'Accept':'application/json'}
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI
                 } #json required

    # site_session = requests.Session()
    # _ = site_session.get('https://api.github.com/')

    response = requests.post(PATH_FOR_TOKEN,
                             auth=client_auth,
                             data=post_data,
                             headers={'Accept': 'application/json'})

    print (response.text)

    token_json = response.json()


    # token_json = json.loads(response.text)



    print(token_json)

    return token_json["access_token"]


def get_username(access_token):
    # header = {"Authorization": "token %s" % }


    params = {
        'token': access_token
    }
    #
    #https://auth.fit.cvut.cz/oauth/api/v1/tokeninfo?
    # url = 'https://api.github.com/user?access_token=' + urllib.urlencode(params)
    url = 'https://api.github.com/user?access_token=' + access_token
    print("=====1111====" + url)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    print("-------------------------")
    print(data)
    print("-----------2222----------")
    # print(data["user_id"])

    return data["login"]


class OAuthbasedUserManager(FilebasedUserManager):
    def __init__(self):
        logging.getLogger("octoprint.plugins." + __name__).info("#######2222######")
        FilebasedUserManager.__init__(self)

    def logout_user(self, user):
        global username
        username = ""
        print(">>>>>>>>My logout")
        UserManager.logout_user(self, user)

    def login_user(self, user):
        global username
        self._cleanup_sessions()

        logging.getLogger("octoprint.plugins." + __name__).info("#######5555 - My login ######")
        print(" MY LOGIN user = ")

        tokenGot = False

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

        print("code = " + user.get_id() + "    " + user.get_name())
        print("username = " + username)

        # if username == "" and username != user.get_id() and not isinstance(user, LocalProxy):


        if not isinstance(user, SessionUser):
            print ("NEW USER--------")
            code = user.get_id()
            print ("logincode = " + code)
            access_token = get_token(code)
            # admin role tmp
            username = get_username(access_token)
            print(username)
            user = User(username, "", True, "admin")
            print("444")
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
        print("Logging in via OAuth")
        # print("username = " + username + "    pass = " + password)
        #
        # code = username
        # state = password
        #
        # access_token = get_token(code)
        # print("Your name is: %s" % get_username(access_token))

        return True

    #

    # user = self.findUser(username)
    # if not user:
    # 	print("Not user")
    # 	return False
    #
    # if user.check_password(password):
    # 	# new hash matches, correct password
    # 	return True
    # else:
    # 	return False

    def findUser(self, userid=None, apikey=None, session=None):

        # # making temporary user because of implementation of api
        #
        # if userid is not None:
        # 	print("userid=code= " + userid)
        #
        # 	code = userid
        #
        # 	access_token = get_token(code)
        #
        # 	username = get_username(access_token)
        #
        # 	# is admin? into settings

        user = User(userid, "", 1, "admin")
        # else:
        # 	return None

        # print("My find user" + username)
        #	tmp = "tmp"

        return user

    # if user is not None:
    # 	return user
    #
    # if userid is not None:
    # 	if userid not in self._users.keys():
    # 		return None
    # 	return self._users[userid]
    #
    # elif apikey is not None:
    # 	for user in self._users.values():
    # 		if apikey == user._apikey:
    # 			return user
    # 	return None
    #
    # else:
    # 	return None
