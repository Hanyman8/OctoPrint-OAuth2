"""
Integration test for OAuth 2.0 plugin for application OctoPrint
"""
import threading
import time

import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from octoprint_oauth2.tests.constants_for_tests import GOOD_REDIRECT_URI, PATH_TO_GECKO_DRIVER
from octoprint_oauth2.tests.fake_oauth2_server import serve_forever
from octoprint_oauth2.tests.integration_server import run_auth_server


@pytest.fixture(scope='session')
def start_servers():
    """
    Start OAuth provider and fake resource server fixture
    """
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    try:
        # start resource server
        resource_server = threading.Thread(target=serve_forever, args=[8080])
        resource_server.daemon = True
        resource_server.start()
        # # start provider
        oauth_provider = threading.Thread(target=run_auth_server, args=[8282])
        oauth_provider.daemon = True
        oauth_provider.start()
        # sleep so server can startup
        time.sleep(4)
        yield oauth_provider
    finally:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def change_test_user_rights(driver):
    """
    Method for driver to change user permissions in OctoPrint
    """
    driver.find_element_by_id("navbar_settings").click()
    time.sleep(2)
    driver.find_element_by_id("settings_users_link").click()
    try:
        while driver.find_element_by_xpath("//button[contains(.,'Ignore')]") is not None:
            driver.find_element_by_xpath("//button[contains(.,'Ignore')]").click()
    except WebDriverException:
        pass
    driver.find_element_by_xpath(
        "//td//*[contains(text(), 'test_user')]/../following-sibling::td[3]/a[1]").click()
    time.sleep(1)
    driver.find_element_by_id("settings-usersDialogEditUserAdmin").click()
    driver.find_element_by_xpath(
        "//div[@id='settings-usersDialogEditUser']//div[@class='modal-footer']//*[contains(text(),"
        " 'Confirm')]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//button[contains(text(),'Save')]//i/..").click()
    time.sleep(1)
    return driver


def get_driver(start_servers):
    """
    Prepare Selenium driver
    """
    # temporary for testing of testing
    driver = webdriver.Firefox(executable_path=PATH_TO_GECKO_DRIVER)
    driver.implicitly_wait(10)
    driver.get(GOOD_REDIRECT_URI)
    driver.maximize_window()
    return driver


def test_login(start_servers):
    """
    Test login user via Selenium
    """
    driver = get_driver(start_servers)
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("loginForm").click()
    driver.find_element_by_id("confirm").click()
    title = driver.find_element_by_xpath("//*[@title='Logged in as test_admin']")
    assert title is not None
    driver.quit()


def test_logout(start_servers):
    """
    Login, then test logout user
    """
    driver = get_driver(start_servers)
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("loginForm").click()
    driver.find_element_by_id("confirm").click()
    label = "Ignore"
    try:
        while driver.find_element_by_xpath("//button[contains(.,'" + label + "')]") is not None:
            driver.find_element_by_xpath("//button[contains(.,'" + label + "')]").click()
    except WebDriverException:
        pass
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("logout_button").click()
    form = driver.find_element_by_id("loginForm")
    assert form is not None
    driver.quit()


def test_more_users(start_servers):
    """
    Test login more users and add role admin
    """
    driver1 = get_driver(start_servers)
    driver2 = get_driver(start_servers)
    # login admin
    driver1.find_element_by_id("navbar_plugin_oauth2").click()
    driver1.find_element_by_id("loginForm").click()
    driver1.find_element_by_id("confirm").click()
    title = driver1.find_element_by_xpath("//*[@title='Logged in as test_admin']")
    assert title is not None
    time.sleep(2)
    # # login user
    driver2.find_element_by_id("navbar_plugin_oauth2").click()
    driver2.find_element_by_id("loginForm").click()
    driver2.find_element_by_id("confirm").click()
    title2 = driver2.find_element_by_xpath("//*[@title='Logged in as test_user']")
    assert title2 is not None

    # sleep and refresh to fetch settings from users.yaml
    driver1.get(GOOD_REDIRECT_URI)
    time.sleep(2)
    # add admin role to test_user
    change_test_user_rights(driver1)
    driver2.get(GOOD_REDIRECT_URI)
    time.sleep(1)
    settings = driver2.find_element_by_id("navbar_settings")
    assert settings.is_displayed() is True

    # Remove permissions from test_user
    change_test_user_rights(driver1)
    driver2.get(GOOD_REDIRECT_URI)
    settings = driver2.find_element_by_id("navbar_settings")
    assert settings.is_displayed() is False
    driver1.quit()
    driver2.quit()

def test_deny_login(start_servers):
    '''
    Test if user has declined login
    '''
    driver = get_driver(start_servers)
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("loginForm").click()
    driver.find_element_by_id("deny").click()

    # this element should not exist.
    with pytest.raises(NoSuchElementException):
        driver.find_element_by_xpath("//*[@title='Logged in as test_user']")
    driver.quit()
