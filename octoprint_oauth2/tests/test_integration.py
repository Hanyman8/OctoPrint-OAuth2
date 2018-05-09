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
	try:
		# start resource server
		resource_server = threading.Thread(target=serve_forever, args=[8181])
		resource_server.daemon = True
		resource_server.start()
		# # start provider
		oauth_provider = threading.Thread(target=run_auth_server, args=[8282])
		oauth_provider.daemon = True
		oauth_provider.start()
		# sleep so server can startup
		time.sleep(1)
		yield oauth_provider
	finally:
		print ("321")

@pytest.fixture
def driver(start_servers):
	# temporary for testing of testing
	print ("setting driver")
	driver = webdriver.Firefox(executable_path="/home/hany/Downloads/geckodriver")
	driver.implicitly_wait(10)
	return driver

#
def test_login(driver):
	driver.get("http://0.0.0.0:5000/")
	print ("TEST SELENIUM")
	driver.find_element_by_id("navbar_plugin_oauth2").click()
	driver.find_element_by_id("loginForm").click()
#
# def test_bla(driver):
# 	print ("1234")
