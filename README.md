# OctoPrint-OAuth2

Plugin provides logging into OctoPrint via authorization protocol OAuth 2.0. Now this plugin overrides default logging in.
Default login is now provided by github and everybody logged in by this plugin has admin role. Possible configuration is below. 

## Setup

Install via the bundled [Plugin Manager](http://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/Hanyman8/OctoPrint-OAuth2/archive/master.zip

You can install it via pip.

After installing plugin, you also need to configure your config.yaml and users.yaml
files. They are stored configuration folder (e.g. `~/.octoprint/` on Linux)`

## Configuration

If you want to be logged in via github api, you need to provide your
CLIENT_ID and CLIENT_SECRET into your .
Both are should be stored in config.yaml file. Under plugins section,
there should be list od your plugins, and now you need to put there
also configuration for plugin OAuth2.

### config.yaml

```yaml
plugins:
  oauth2:
```
Under `oauth2` plugin, there is `active_client`, and servers,
that can use OAuth2 authentication. `active_client` says which one
should be used for authentication.
```yaml
plugins:
  oauth2:
    active_client: github
    github: ...
    google: ...
    facebook: ...
```
Under your client, there have to be basic information about,
where to log in via OAuth2 used by `login_path`, then url where
the access token should be obtained in value `token_path`.  In `user_info_path`
has to be url, where information about user is stored. This information
from access token has to be in JSON therefore you can also set some headers for
plugin obtaining access token.

```yaml
active_client: github
github:
  login_path: https://github.com/login/oauth/authorize?
  token_path: https://github.com/login/oauth/access_token
  user_info_path: https://api.github.com/user?access_token=
  token_headers: # plugin needs access token in JSON, on some servers we need to configure it.
    Accept: application/json
google: ...
facebook: ...
```
Finnaly every client needs redirection_uri, client_id and client_secret.
Because one client application has only one redirection_uri, we need to specific
this in config file. OctoPrint can for example run on `0.0.0.0:5000` and
if we want to redirect back after authorization to `0.0.0.0:5000` and
not `localhost:5000` we have to specify that.

```yaml
active_client: github
github:
  login_path: https://github.com/login/oauth/authorize?
  token_path: https://github.com/login/oauth/access_token
  user_info_path: https://api.github.com/user?access_token=
  token_headers: # plugin needs access token in JSON, on some servers we need to configure it.
    Accept: application/json
  http://localhost:5000/: #redirect_uri
    client_id: 5944a4d751a567c31 #example of client_id
    client_secret: 3a9314582de82304faq5865a2d565734 #example of secret
google: ...
facebook: ...
```

Anf finally here is an example of config.yaml configuration using more redirect_uris
on active client github.
```yaml
plugins:
  oauth2:
    active_client: github
    github: #server that is used
      login_path: https://github.com/login/oauth/authorize?
      token_path: https://github.com/login/oauth/access_token
      user_info_path: https://api.github.com/user?access_token=
      token_headers: # plugin needs access token in JSON, on some servers we need to configure it.
        Accept: application/json
      http://localhost:5000/: #redirect_uri from
        client_id: 5944a4d751a567c31 #example of client_id
        client_secret: 3a9314582de82304faq5865a2d565734 #example of secret
      http://0.0.0.0:5000/:
        client_id: 1cbef6227fa4b23ff
        client_secret: 9a6541ee16c6c0c3fe65825ff5c7df25
    google: #inactive server
      login_path: google_login_url
      token_path: google_url_to_get_access_token
      user_info_path: google_url_to_get_user_data
      192.168.0.1:
        client_id: 1234
        client_secret: qwert


```
Note: this is not valid client_id and client_secret :+1:

### users.yaml

For congiguration users.yaml you have to set a user with admin role.
This user needs to have same username as the username from server, for example:
```yaml
YourUsername1234:
  active: true
  apikey: null
  password: ''
  roles:
  - user
  - admin
  settings: {}
```
Every other user, who is logged via OAuth2 authentication isstored to users.yaml
file with role user. Through user interace admin can set his role to user later.

# OctoPrint-OAuth2
