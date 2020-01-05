$(function() {

    // function to parse URL
    function parseUrl(url) {
        const parser = document.createElement('a');
        parser.href = url;
        return parser;
    }

    // source: https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
    function guid() {
      function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1);
      }
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
    }

    // source: https://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }


    function OAuthLoginModel(parameters) {
        var self = this;


        $(".dropdown-menu").click(function (e) {
            e.stopPropagation();
        });

        self.loginState = parameters[0];
        self.settings = parameters[1];
        self.control = parameters[2];


        self.loginState.login = function () {

            const oauth_plugin_settings = self.settings.settings.plugins.oauth2;

            const redirect_uri = parseUrl(window.location.href).origin + "/";

            const client_id = oauth_plugin_settings[redirect_uri].client_id();
            const login_path = oauth_plugin_settings.login_path();

            if(!client_id || !login_path){
                alert("Probably bad configuration file");
            }

            const state = guid();
            // setting state to local storage
            localStorage.setItem("state", state);

            const params = ['response_type=code', 'client_id=' + client_id, 'redirect_uri=' + redirect_uri, 'state=' + state];
            const query = params.join('&');
            const url = login_path + "?" + query;

            window.location.replace(url);
        };

        self.loginState.logout = function() {
            var provider = parseUrl(self.settings.settings.plugins.oauth2.login_path()).host;

            return OctoPrint.browser.logout()
                .done(function(response) {

                    new PNotify({title: gettext("Logout from OctoPrint successful"), text: gettext("You are now logged out"), type: "success"});
                    new PNotify({title: gettext("OAuth 2.0 Logout"), text: gettext("To log out completely, make sure to log out from OAuth 2.0 provider: " + provider), hide: false});

                    self.loginState.fromResponse(response);
                })
                .fail(function(error) {
                    if (error && error.status === 401) {
                         self.loginState.fromResponse(false);
                    }
                });
        };



        self.loginState.userMenuText = ko.pureComputed(function () {
           if (self.loginState.loggedIn()){
               return self.loginState.username();
           }
           else {
               return gettext("Login via OAuth 2.0");
           }
        });

        const code = getParameterByName("code",window.location.href);
        const stateFromOAuth = getParameterByName("state",
            window.location.href);


        if(!!stateFromOAuth && !!code){
            const state = localStorage.getItem("state");
            localStorage.removeItem("state");
            if (stateFromOAuth != state) {
                alert("State sent to oauth server is not same. Possible attack");
                return;
            }

            const url = parseUrl(window.location.href).origin + "/";
            const parameters = {"code": code,
                                "redirect_uri": url};

            // for each user we need to send specific redirect uri,
            // this parametr we need to in user manager method login_user
            // which is called in server/api (called by browser.login)
            // so we send this in dict and parse it later
            OctoPrint.browser.login(parameters, "unused", false)
                .done(function (response) {
                    new PNotify({
                        title: gettext("Login OK"),
                        text: _.sprintf(gettext('OAuth 2.0 Logged as "%(username)s"'),
                            {username: response.name}), type:"success"});
                    self.loginState.fromResponse(response);
                    self.loginState.loginUser("");
                    self.loginState.loginPass("");
                    self.loginState.loginRemember(false);

                if (history && history.replaceState) {
                        history.replaceState({success: true}, document.title, window.location.pathname);
                    }
                })
                .fail(function(response) {
                    switch(response.status) {
                        case 401: {
                            new PNotify({
                                title: gettext("Login failed"),
                                text: gettext("User unknown or wrong password"),
                                type: "error"
                            });
                            break;
                        }
                        case 403: {
                            new PNotify({
                                title: gettext("Login failed"),
                                text: gettext("Your account is deactivated"),
                                type: "error"
                            });
                            break;
                        }
                    }
                });
        }
    }


    self.onStartup = function () {
        self.elementOAuthLogin = $("#oauth_login");
    };


    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push({
        // This is the constructor to call for instantiating the plugin
        construct: OAuthLoginModel,

        // This is a list of dependencies to inject into the plugin, the order which you request
        // here is the order in which the dependencies will be injected into your view model upon
        // instantiation via the parameters argument
        dependencies: ["loginStateViewModel", "settingsViewModel", "controlViewModel"],

        // Finally, this is the list of selectors for all elements we want this view model to be bound to.
        // elements: ["#tab_plugin_oauthfit"]
    });
});
