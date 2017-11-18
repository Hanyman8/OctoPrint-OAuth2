# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class HelloWorldPlugin(octoprint.plugin.StartupPlugin):
    def on_after_startup(self):
        self._logger.info("Hello World OAuth FIT!")

__plugin_name__ = "OAuth2 FIT CTU"
__plugin_implementation__ = HelloWorldPlugin()
