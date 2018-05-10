from fake_oauth2_server import serve_forever
from integration_server import run_auth_server

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
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

def test_more_users(start_servers):
	driver1 = get_driver(start_servers)
	driver2 = get_driver(start_servers)
	driver1.find_element_by_id("navbar_plugin_oauth2").click()
	driver1.find_element_by_id("loginForm").click()
	driver1.find_element_by_id("confirm").click()
	time.sleep(5)
	driver2.find_element_by_id("navbar_plugin_oauth2").click()
	driver2.find_element_by_id("loginForm").click()
	driver2.find_element_by_id("confirm").click()
