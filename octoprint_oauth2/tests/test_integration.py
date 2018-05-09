from fake_oauth2_server import serve_forever
from integration_server import oauth_serve

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from constants_for_tests import *

import threading
import os
import time
import pytest


@pytest.fixture(scope='session')
def start_servers():
	print ("starting servers")
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	try:
		# start provider
		oauth_provider = threading.Thread(target=oauth_serve(), args=[8282])
		oauth_provider.daemon = True
		oauth_provider.start()
		# start resource server
		resource_server = threading.Thread(target=serve_forever(), args=[8080])
		resource_server.daemon = True
		resource_server.start()

		# sleep so server can startup
		time.sleep(1)
		yield oauth_provider, resource_server
	finally:
		del os.environ['OAUTHLIB_INSECURE_TRANSPORT']

@pytest.fixture
def driver(start_servers):
	# temporary for testing of testing
	driver = webdriver.Chrome(executable_path="/home/hany/Downloads/geckodriver")
	driver.implicitly_wait(10)
	return driver


def test_login(driver):
	print ("TEST SELENIUM")
	driver.find_element_by_id("navbar_plugin_oauth2").click()
	driver.find_element_by_id("loginForm").click()
	driver.get("http://0.0.0.0:5000/")
