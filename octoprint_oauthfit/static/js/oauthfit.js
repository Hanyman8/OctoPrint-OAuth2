$(function() {
    var CLIENT_ID = "26cc1117-f7b5-4781-af91-ba7baecb47c4";
    var CLIENT_SECRET = "3zjAAtVhWNsXFgF83eH41J6YgNrvVekQ";
    var REDIRECT_URI = "http://0.0.0.0:5000/";
    var PATH = "https://auth.fit.cvut.cz/oauth/authorize?";

    function guid() {
      function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1);
      }
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
    }


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

        // self.loginState.loginUser = ko.observable(false);
        // self.loginState = ko.observable(false);

        self.loginState.userMenuText = ko.pureComputed(function () {
           if (self.loginState.loggedIn()){
               return self.loginState.username();
           }
           else {
               return gettext("Login_from_model");
           }
        });

        var code = getParameterByName("code",window.location.href);
        var stateFromOAuth = getParameterByName("state", window.location.href);
        //var remember = true; // tmp true

        if(!!stateFromOAuth && !!code){
            window.alert("cond ok, state=" + stateFromOAuth + "   code=" + code);
            var tmp = window.location.host;
           // window.alert(tmp);


            OctoPrint.browser.login(code, stateFromOAuth, false)
                .done(function (response) {
                    new PNotify({
                        title: gettext("Login OK"),
                        text: _.sprintf(gettext('OAuth Logged as "%(username)s"'),
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


            // window.location.replace("http://"+ tmp);

        }




        self.loginState.login = function (u, p, r) {

            var state = guid();

            var params = ['response_type=code', 'client_id=' + CLIENT_ID, 'redirect_uri=' + REDIRECT_URI, 'state=' + state];
            var query = params.join('&');
            var url = PATH + query;
            var href = window.location.href;

          //  window.alert("0000");

            window.location.replace(url);


        }


    };

    // this will hold the URL currently displayed by the iframe
    self.currentUrl = ko.observable();

    // this will hold the URL entered in the text field
    self.newUrl = ko.observable();



    // this will be called when the user clicks the "Go" button and set the iframe's URL to
    // the entered URL
    self.goToUrl = function() {
        self.currentUrl(self.newUrl());
    };

    self.onStartup = function () {
        self.elementOAuthLogin = $("#oauth_login");
    };


    // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
    // dependencies have already been initialized. It is especially guaranteed that this method
    // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
    // the SettingsViewModel been properly populated.
    self.onBeforeBinding = function() {
        self.newUrl(self.settings.settings.plugins.oauthfit.url());
        self.goToUrl();
    };


  //  OAuthViewModel.myMessage("Nazdar");

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
        elements: ["#tab_plugin_oauthfit"]
    });
});
