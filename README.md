# OctoPrint-OAuthFIT

Plugin provides logging into OctoPrint via authorization protocol OAuth 2.0. Now this plugin overrides default logging in.
Default login is now provided by github and everybody logged in by this plugin has admin role. Possible configuration is below. 

## Setup

Install via the bundled [Plugin Manager](http://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/Hanyman8/OctoPrint-OAuthFIT/archive/master.zip

**TODO:** Describe how to install your plugin, if more needs to be done than just installing it via pip or through
the plugin manager.

## Configuration

If you want to be logged in via github api, you need to provide your CLIENT_ID, CLIENT_SECRET, and REDIRECTION_URI.
Both are now stored in config.yaml file.

Default settings is my CLIENT_ID, CLIENT_SECRET, and REDIRECTION_URI is set to "http://0.0.0.0:5000"

# OctoPrint-OAuthFIT
