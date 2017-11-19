# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class HelloWorldPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin):
    def on_after_startup(self):
        self._logger.info("Hello World FIT OAuth 0002!")


__plugin_name__ = "OAuth"
__plugin_implementation__ = HelloWorldPlugin()
