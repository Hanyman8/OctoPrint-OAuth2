from fake_oauth2_server import serve_forever
from integration_server import run_auth_server

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from constants_for_tests import *

import threading
import os, signal
import time
import pytest


@pytest.fixture(scope='session')
def start_servers():
    print ("starting servers")
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


def get_driver(start_servers):
    # temporary for testing of testing
    print ("setting driver")
    driver = webdriver.Firefox(executable_path="/home/hany/Downloads/geckodriver")
    driver.implicitly_wait(10)
    driver.get(GOOD_REDIRECT_URI)
    
    return driver


def test_login(start_servers):
    driver = get_driver(start_servers)
    print ("TEST SELENIUM")
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("loginForm").click()
    driver.find_element_by_id("confirm").click()
    title = driver.find_element_by_xpath("//*[@title='Logged in as test_admin']")
    assert title is not None


def test_logout(start_servers):
    driver = get_driver(start_servers)
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("loginForm").click()
    driver.find_element_by_id("confirm").click()
    label = "Ignore"
    try:
        while driver.find_element_by_xpath("//button[contains(.,'" + label + "')]") is not None:
            driver.find_element_by_xpath("//button[contains(.,'" + label + "')]").click()
    except:
        pass
    driver.find_element_by_id("navbar_plugin_oauth2").click()
    driver.find_element_by_id("logout_button").click()
    form = driver.find_element_by_id("loginForm")
    assert form is not None

def change_test_user_rights(driver):
    driver.find_element_by_id("navbar_settings").click()
    time.sleep(2)
    driver.find_element_by_id("settings_users_link").click()
    try:
        while driver.find_element_by_xpath("//button[contains(.,'Ignore')]") is not None:
            driver.find_element_by_xpath("//button[contains(.,'Ignore')]").click()
    except:
        pass
    element = driver.find_element_by_xpath \
        ("//td//*[contains(text(), 'test_user')]/../following-sibling::td[3]/a[1]").click()
    time.sleep(1)
    driver.find_element_by_id("settings-usersDialogEditUserAdmin").click()
    driver.find_element_by_xpath(
        "//div[@id='settings-usersDialogEditUser']//div[@class='modal-footer']//*[contains(text(), 'Confirm')]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//button[contains(text(),'Save')]//i/..").click()
    time.sleep(1)
    return driver

# Test login more users and add role admin
def test_more_users(start_servers):
    driver1 = get_driver(start_servers)
    driver2 = get_driver(start_servers)
    # login admin
    driver1.find_element_by_id("navbar_plugin_oauth2").click()
    driver1.find_element_by_id("loginForm").click()
    driver1.find_element_by_id("confirm").click()
    title = driver1.find_element_by_xpath("//*[@title='Logged in as test_admin']")
    assert title is not None
    # time.sleep(5)
    # # login user
    driver2.find_element_by_id("navbar_plugin_oauth2").click()
    driver2.find_element_by_id("loginForm").click()
    driver2.find_element_by_id("confirm").click()
    title2 = driver2.find_element_by_xpath("//*[@title='Logged in as test_user']")
    assert title2 is not None
    
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
