# coding=utf-8
from __future__ import absolute_import

from octoprint_oauthfit.oauth_user_manager import OAuthbasedUserManager
import octoprint.plugin
import logging


class HelloWorldPlugin(octoprint.plugin.StartupPlugin,
					   octoprint.plugin.TemplatePlugin,
					   octoprint.plugin.OctoPrintPlugin):
	def on_after_startup(self):
		self._logger.info("############# Hello World FIT OAuth 0003!")
		#hooks = self._plugin_manager.get_hooks("octoprint.plugin.octoprint_oauthfit")
		#for name, hook in hooks.items():
		#	hook()

	#def on_after_startup(self):
	#	self._logger.info("############### Order Test Plugin: StartupPlugin.on_after_startup called")

def user_factory_hook(components, settings, *args, **kwargs):
	logging.getLogger("octoprint.plugins." + __name__).info("#######111111######")
	return OAuthbasedUserManager()

__plugin_name__ = "OAuth"
__plugin_implementation__ = HelloWorldPlugin()
__plugin_hooks__ = {
	"octoprint.users.factory" : user_factory_hook
}
