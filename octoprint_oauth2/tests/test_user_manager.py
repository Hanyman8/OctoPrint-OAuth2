"""
Unit tests for plugin octoprint-oauth2
"""
import threading

import time
import os
import pytest

from requests_oauthlib import OAuth2Session

from octoprint.users import User, SessionUser
from octoprint_oauth2.tests.constants_for_tests import *
from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
from octoprint_oauth2.tests.fake_oauth2_server import serve_forever



@pytest.fixture(scope='session')
def fake_oauth_server():
    """
    Server fake oauth2 provider fixture
    """
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    try:
        thr = threading.Thread(target=serve_forever, args=[8080])
        thr.daemon = True
        thr.start()
        time.sleep(1)
        yield thr
    finally:
        del os.environ['OAUTHLIB_INSECURE_TRANSPORT']


@pytest.fixture
def user_manager(fake_oauth_server):
    """
    Init OauthbasedUserManager for testing purposes
    """
    user_manager = OAuthbasedUserManager.__new__(OAuthbasedUserManager)
    user_manager.token_headers = {"Accept": "application/json"}
    user_manager.username_key = GOOD_USERNAME_KEY
    user_manager.access_token_query_key = GOOD_ACCESS_TOKEN_QUERY_KEY
    user_manager.path_user_info = PATH_USER_INFO
    user_manager.path_for_token = PATH_FOR_TOKEN

    # Mock some OctoPrint values, cleanup session needs callable
    user_manager._cleanup_sessions = lambda: True
    user_manager._session_users_by_session = {}
    user_manager._sessionids_by_userid = {}
    user_manager._users = {}
    user_manager._save = lambda: True
    user_manager.addUser = lambda x, y, z, k: True
    return user_manager

@pytest.fixture
def oauth2_session(user_manager):
    """
    Fixture to make OAuth2 session
    """
    return OAuth2Session(CLIENT_ID, redirect_uri=GOOD_REDIRECT_URI)


def test_get_access_token_good(oauth2_session, user_manager):
    access_token = user_manager.get_token(oauth2_session, GOOD_CODE, CLIENT_ID, CLIENT_SECRET)
    assert access_token == GOOD_ACCESS_TOKEN


def test_get_access_token_bad(oauth2_session, user_manager):
    access_token = user_manager.get_token(oauth2_session, BAD_CODE, CLIENT_ID, CLIENT_SECRET)
    assert access_token == None


def test_get_username_good(oauth2_session, user_manager):
    oauth2_session.access_token = GOOD_ACCESS_TOKEN
    username = user_manager.get_username(oauth2_session)
    print(username)
    assert username == GOOD_USERNAME


def test_get_username_bad_access_token(oauth2_session, user_manager):
    oauth2_session.access_token = BAD_ACCESS_TOKEN
    username = user_manager.get_username(oauth2_session)
    assert username is None


def test_get_username_bad_query_key(oauth2_session, user_manager):
    user_manager.access_token_query_key = BAD_ACCESS_TOKEN_QUERY_KEY
    oauth2_session.access_token = GOOD_ACCESS_TOKEN
    username = user_manager.get_username(oauth2_session)
    print username
    assert username is None


def test_login_session(user_manager):
    user = User(GOOD_USERNAME, "1234", 1, ["user"])
    # make session
    user = SessionUser(user)
    user_check = user_manager.login_user(user)
    assert isinstance(user_check, SessionUser)
    assert isinstance(user_check, User)
    assert user_check.get_id() == GOOD_USERNAME
    assert user_check.get_id() != BAD_USERNAME
    assert user.is_user() is True


def test_oauth2_login_good(user_manager):
    # code and redirect_uri is passed as argument from server api
    params = {'code': GOOD_CODE,
              'redirect_uri': GOOD_REDIRECT_URI}
    user = User(params, "1234", 1, ["user"])

    # mock settings from config.yaml
    user_manager.oauth2 = {GOOD_REDIRECT_URI: {"client_id": CLIENT_ID,
                                               "client_secret": CLIENT_SECRET}}
    # user is not instance of SessionUser
    assert not isinstance(user, SessionUser)

    user_check = user_manager.login_user(user)
    assert user_check.get_id() == GOOD_USERNAME
    # user should have session
    assert isinstance(user_check, SessionUser)
    assert user_check.get_id() != BAD_USERNAME
    assert user_check.get_id() is not None
