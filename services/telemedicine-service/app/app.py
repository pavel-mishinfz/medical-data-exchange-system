from fastapi import FastAPI, Request
import requests
import requests.auth
from urllib import parse

from . import config


description = """"""

tags_metadata = [
    {
        "name": "chats",
        "description": "Операции с чатом",
    },
    {
        "name": "consultations",
        "description": "Организация видеоконсультаций",
    }
]

app_config: config.Config = config.load_config()

app = FastAPI(title='Telemedicine Service',
              description=description,
              openapi_tags=tags_metadata)


@app.get(
    '/consultations/auth',
    response_model=str,
    summary='Возращает ссылку для авторизации в приложении zoom',
    tags=['consultations']
)
def make_authorization_url():
    params = {"client_id": app_config.CLIENT_ID,
              "response_type": "code",
              "redirect_uri": app_config.REDIRECT_URI.unicode_string()}
    url = "https://zoom.us/oauth/authorize?" + parse.urlencode(params)
    return url


@app.get(
    '/consultations/callback',
    response_model=str,
    summary='Возвращает ссылку для подключения',
    tags=['consultations']
)
def make_meeting_url(request: Request):
    code = request.query_params['code']
    access_token = get_token(code)
    return get_username(access_token)['personal_meeting_url']


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(
        app_config.CLIENT_ID, app_config.CLIENT_SECRET.get_secret_value()
    )
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": app_config.REDIRECT_URI.unicode_string()}

    response = requests.post("https://zoom.us/oauth/token",
                             auth=client_auth,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]


def get_username(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get("https://api.zoom.us/v2/users/me", headers=headers)
    data = response.json()
    return data

