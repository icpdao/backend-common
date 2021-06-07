import time
import iso8601
import datetime
import jwt
import requests
from mongoengine import Document, StringField, IntField


class GithubAppToken(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'github_app_token'
    }
    dao_name = StringField(required=True)
    token = StringField(required=True)
    expires_at = IntField(required=True)

    @classmethod
    def get_token(cls, app_id: str, app_private_key: str, dao_name: str):
        token_record = cls.objects(dao_name=dao_name).first()
        if token_record and token_record.expires_at > (int(time.time()) - 10):
            return token_record.token
        new_token = cls.__req_token(app_id, app_private_key, dao_name)
        if not new_token:
            return None
        expired_time = iso8601.parse_date(new_token['expires_at'])
        expires_at = int(
            expired_time.replace(tzinfo=datetime.timezone.utc).timestamp())
        if token_record:
            token_record.token = new_token['token']
            token_record.expires_at = expires_at
        else:
            token_record = cls(
                token=new_token['token'], expires_at=expires_at,
                dao_name=dao_name)
        token_record.save()
        return token_record.token

    @classmethod
    def __req_token(cls, app_id: str, app_private_key: str, dao_name: str):
        token = cls.__get_icp_app_jwt(app_id, app_private_key)

        installed = requests.get(
            f'https://api.github.com/orgs/{dao_name}/installation',
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        if installed.status_code != 200:
            return {}
        ret = requests.post(
            installed.json()['access_tokens_url'],
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        if ret.status_code == 201:
            return ret.json()
        return {}

    @staticmethod
    def __get_icp_app_jwt(github_app_id, github_app_private_key):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2*60),
            'iat': datetime.datetime.utcnow(),
            'iss': github_app_id
        }
        tok = jwt.encode(payload, github_app_private_key, algorithm='RS256')
        if isinstance(tok, bytes):
            tok = tok.decode('utf8')
        return tok
