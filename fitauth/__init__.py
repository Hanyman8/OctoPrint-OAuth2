CLIENT_ID = "26cc1117-f7b5-4781-af91-ba7baecb47c4"
CLIENT_SECRET = "3zjAAtVhWNsXFgF83eH41J6YgNrvVekQ"
REDIRECT_URI = "http://localhost:65010/oauth_test_callback"

from flask import Flask
from flask import abort, request
import requests
import requests.auth
import urllib, json


app = Flask(__name__)


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with fitauth</a>'
    return text % make_authorization_url()


@app.route('/oauth_test_callback')
def oauth_test_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    # We'll change this next line in just a moment
    access_token = get_token(code)
    return "Your name is: %s" % get_username(access_token)


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    response = requests.post("https://auth.fit.cvut.cz/oauth/token",
                             auth=client_auth,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]


def get_username(access_token):
    params = {
        'token': access_token
    }
    url = 'https://auth.fit.cvut.cz/oauth/api/v1/tokeninfo?' + urllib.urlencode(params)
    print("=====1111====" + url)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    print("-------------------------")
    print(data)
    print("-----------2222----------")
    print(data["user_id"])

    return data["user_id"]


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    params = {"response_type": "code", "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "state": state}
    url = "https://auth.fit.cvut.cz/oauth/authorize?" + urllib.urlencode(params)
   # print(url)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
    pass


def is_valid_state(state):
    return True


if __name__ == '__main__':
    app.run(debug=True, port=65010)
