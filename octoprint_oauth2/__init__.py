# coding=utf-8
from __future__ import absolute_import

from octoprint_oauth2.oauth_user_manager import OAuthbasedUserManager
import octoprint.plugin
import logging


class OAuth2Plugin(octoprint.plugin.StartupPlugin,
				   octoprint.plugin.TemplatePlugin,
				   octoprint.plugin.SettingsPlugin,
				   octoprint.plugin.AssetPlugin
				   ):
	# Template plugin mixin
	def get_template_configs(self):
		"""
		Plugin sets used templates

		:return:
		"""
		self._logger.info("OAuth 2.0 get template configs")
		return [dict(type="navbar", template="oauth2_login.jinja2", custom_bindings=False, replaces="login")]

	# Asset plugin mixin
	def get_assets(self):
		"""
		Plugin sets assets

        :return: dict
        """

		self._logger.info("OAuth 2.0 get assets")
		return dict(
			js=["js/oauth2.js"],
		)

	def get_settings_restricted_paths(self):
		"""
        Plugin set restricted paths of config.yaml

        :return: dict
        """

		return dict(admin=[["plugins", "oauth2"], ])


def user_factory_hook(components, settings, *args, **kwargs):
	"""
    User factory hook, to inititialize OAuthBasedUserManager, which controls login users

    :param components:
    :param settings:
    :param args:
    :param kwargs:
    :return: OAuthbasedUserManager
    """

	logging.getLogger("octoprint.plugins." + __name__).info("OAuth 2.0 hooking OAuthBasedUserManager")
	return OAuthbasedUserManager(components, settings)


__plugin_name__ = "OAuth"
__plugin_implementation__ = OAuth2Plugin()
__plugin_hooks__ = {
	"octoprint.users.factory": user_factory_hook
}
