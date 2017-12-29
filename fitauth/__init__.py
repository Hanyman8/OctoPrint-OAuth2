from typing import Dict, Any, List

from requests import HTTPError
from raven.contrib.django.raven_compat.models import client
from social_core.backends.oauth import BaseOAuth2


class NotFoundInUsermapAPI(Exception):
    pass


class FITOAuth2(BaseOAuth2):
    name = 'fit'
    AUTHORIZATION_URL = 'https://auth.fit.cvut.cz/oauth/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://auth.fit.cvut.cz/oauth/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'user_id'
    EXTRA_DATA = [('roles', 'roles')]
    CTU_PARTS = {
        11000: "FSv",
        12000: "FS",
        13000: "FEL",
        14000: "FJFI",
        15000: "FA",
        16000: "FD",
        17000: "FBMI",
        18000: "FIT",
        31000: "KLOK",
        32000: "MÚVS",
        34000: "ÚTVS",
        35000: "ÚTEF",
        36000: "UCEEB",
        37000: "CIIRC",
    }

    def get_user_details(self, response):
        """Return user details from FIT account"""
        return {'username': response.get('user_id'),
                'email': response.get('user_email'),
                'first_name': response.get('firstName'),
                'last_name': response.get('lastName')}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'https://auth.fit.cvut.cz/oauth/api/v1/tokeninfo'
        try:
            data = self.get_json(url, params={'token': access_token})
        except ValueError:
            return None

        usermap_url = 'https://kosapi.fit.cvut.cz/usermap/v1/people/' + data['user_id']
        try:
            usermap = self.get_json(usermap_url, headers={'Authorization': 'Bearer %s' % access_token})
            data.update(usermap)
        except ValueError:
            pass
        except HTTPError as e:
            if e.response.status_code == 404:
                client.captureException()
                raise NotFoundInUsermapAPI()
            raise

        return data


def get_roles(user):
    """Gets latest roles of given user"""
    extra_data = user.social_auth.values("extra_data").latest(field_name='pk')["extra_data"]
    try:
        if extra_data['roles']:
            return extra_data['roles']
    except KeyError:
        pass
    return []


def get_faculties(extra_data: Dict[str, Any]) -> List[str]:
    roles = extra_data.get("roles", [])

    faculties = set()

    for key, value in FITOAuth2.CTU_PARTS.items():
        if "B-{}-STUDENT".format(key) in roles or "B-{}-ZAMESTNANEC".format(key) in roles:
            faculties.add(value)

    return list(faculties)
