"""
This file manages OAuthbasedUserManager. A hook for OctoPrint plugin.
"""
import logging

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MissingTokenError


from octoprint.users import FilebasedUserManager, User, UserManager, LocalProxy, SessionUser


class OAuthbasedUserManager(FilebasedUserManager):
    """
    OAuthbasedUserManager replaces OctoPrints FilebasedUserManager
    """
    logger = logging.getLogger("octoprint.plugins." + __name__)

    def __init__(self, components, settings):
        OAuthbasedUserManager.logger.info("Initializing OAuthbasedUserManager")
        self._components = components
        self._settings = settings

        # Get data from config file
        self.oauth2 = self._settings.get(["plugins", "oauth2"])
        self.path_for_token = self.oauth2["token_path"]
        self.path_user_info = self.oauth2["user_info_path"]
        self.username_key = self.oauth2["username_key"]
        self.access_token_query_key = self.oauth2["access_token_query_key"]
        try:
            self.token_headers = self.oauth2["token_headers"]
        except KeyError:
            self.token_headers = None

        # Init FilebasedUserManager, other methods are needed for OctoPrint
        FilebasedUserManager.__init__(self)

    def logout_user(self, user):
        """
        Prints log into console, then uses UserManager.logout_user

        :param user:
        :return:
        """
        OAuthbasedUserManager.logger.info("OAuth Logging out")
        UserManager.logout_user(self, user)

    def get_token(self, oauth2_session, code, client_id, client_secret):
        """
        This method use oauth2_session to fetch access token from authorization server.
        if the token_json contains 'access_token' then it returns it.

        :param oauth2_session:
        :param code:
        :param client_id:
        :param client_secret:
        :return: access_token
        """

        try:
            token_json = oauth2_session.fetch_token(self.path_for_token,
                                                    authorization_response="authorization_code",
                                                    code=code,
                                                    client_id=client_id,
                                                    client_secret=client_secret,
                                                    headers=self.token_headers)

            try:
                # token is OK
                access_token = token_json["access_token"]
                return access_token
            except KeyError:
                try:
                    error = token_json["error"]
                    OAuthbasedUserManager.logger.error("Error of access token: %s", error)
                except KeyError:
                    OAuthbasedUserManager.logger.error("Error of access token, "
                                                       "error message not found")

        except MissingTokenError:
            OAuthbasedUserManager.logger.error("Bad authorization_code")

        return None

    def get_username(self, oauth2_session):
        """
        This method make a request to resource server.
        Then tries if specific username_key is OK and return username.

        :param oauth2_session:
        :return: username
        """

        try:
            # GET user data from resource server
            params = {
                self.access_token_query_key: oauth2_session.access_token
            }
            response = requests.get(self.path_user_info, params=params)
            data = response.json()

            # Try if data contains username_key from config file
            try:
                login = data[self.username_key]
                return login
            except KeyError:
                OAuthbasedUserManager.logger.error("User data does not contain username key,"
                                                   "you can try to find it here:")
                OAuthbasedUserManager.logger.error(data)
        except requests.RequestException:
            OAuthbasedUserManager.logger.error(
                "error")

        return None

    def login_user(self, user):
        """
        This method logs in the user into OctoPrint using authorization OAuth2.
        Users user.get_id() should be dict containing redirect_uri and code.
        It is obtained by view model in static/js folder.
        Method gets specified data from config yaml - client_id and client_secret, then
        start OAuth2Session from requests_oauthlib library. Using the library method
        fetch the access token using method get_token.
        After that, user is added into users.yaml config file.

        :param user:
        :return: user
        """
        self._cleanup_sessions()

        if user is None:
            return

        if isinstance(user, LocalProxy):
            user = user._get_current_object()
            return user

        if not isinstance(user, User):
            return None

        if not isinstance(user, SessionUser):

            # from get_id we get for each user his redirect uri and code
            try:
                redirect_uri = user.get_id()['redirect_uri']
                code = user.get_id()['code']
            except KeyError:
                OAuthbasedUserManager.logger.error("Code or redirect_uri not found")
                return None

            client_id = self.oauth2[redirect_uri]["client_id"]
            client_secret = self.oauth2[redirect_uri]["client_secret"]
            oauth2_session = OAuth2Session(client_id,
                                           redirect_uri=redirect_uri)
            access_token = self.get_token(oauth2_session, code, client_id, client_secret)

            if access_token is None:
                return None

            username = self.get_username(oauth2_session)
            if username is None:
                OAuthbasedUserManager.logger.error("Username none")
                return None
            user = FilebasedUserManager.findUser(self, username)

            if user is None:
                self.addUser(username, "", True, ["user"])
                user = self.findUser(username)

        if not isinstance(user, SessionUser):
            user = SessionUser(user)

        self._session_users_by_session[user.session] = user

        user_id = user.get_id()
        if user_id not in self._sessionids_by_userid:
            self._sessionids_by_userid[user_id] = set()

        self._sessionids_by_userid[user_id].add(user.session)
        return user

    def checkPassword(self, username, password):
        """
        Override checkPassword method. Return always true. Use authorization of OAuth 2.0 instead

        :param username:
        :param password:
        :return: True
        """
        OAuthbasedUserManager.logger.info("Logging in via OAuth 2.0")
        return True

    def findUser(self, userid=None, apikey=None, session=None):
        """
        Find user using FilebasedUserManager, else set temporary user.
        This is beacuse of implementation of server/api.

        :param userid:
        :param apikey:
        :param session:
        :return: user
        """
        user = FilebasedUserManager.findUser(self, userid, apikey, session)
        if user is not None:
            return user

        # making temporary user because of implementation of api
        # and we need to pass our code from OAuth to login_user
        # api login could be found in server/api/__init__.py
        user = User(userid, "", 1, ["user"])
        return user
