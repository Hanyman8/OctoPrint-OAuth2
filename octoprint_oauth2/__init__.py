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
        self._logger.info("************ Template configs *************")
        return [
            dict(type="navbar", template="oauth2_login.jinja2", custom_bindings=False, replaces="login"),
            dict(type="settings", custom_bindings=False)
        ]

    # Asset plugin mixin
    def get_assets(self):
        self._logger.info("****** getting Assets ******")
        return dict(
            js=["js/oauth2.js"],
            css=["css/oauth2.css"]
        )

    def get_settings_restricted_paths(self):
        return dict(admin=[["plugins", "oauth2"],])


def user_factory_hook(components, settings, *args, **kwargs):
    logging.getLogger("octoprint.plugins." + __name__).info("#######111111######")
    return OAuthbasedUserManager(components, settings)


__plugin_name__ = "OAuth"
__plugin_implementation__ = OAuth2Plugin()
__plugin_hooks__ = {
    "octoprint.users.factory": user_factory_hook
}
