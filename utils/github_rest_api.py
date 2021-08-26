import time

import requests
import json
import datetime
import jwt


def get_github_access_token_by_code(client_id, client_secret, code):
    """
    result:
    {
        "access_token": "ghu_16C7e42F292c6912E7710c838347Ae178B4a",
        "expires_in": 28800,
        "refresh_token": "ghr_1B4a2e77838347a7E420ce178F2E7c6912E169246c34E1ccbF66C46812d16D5B1A9Dc86A1498",
        "refresh_token_expires_in": 15811200,
        "scope": "",
        "token_type": "bearer"
    }
    """
    url = "https://github.com/login/oauth/access_token?client_id={}&client_secret={}&code={}".format(
        client_id,
        client_secret,
        code
    )
    headers = {
        "Accept": "application/json"
    }

    res = requests.post(url=url, headers=headers, timeout=10)
    res_dict = json.loads(res.text)
    res_dict["token_at"] = int(time.time()) - 5
    return res_dict


def refresh_github_access_token(client_id, client_secret, refresh_token):
    url = "https://github.com/login/oauth/access_token"
    headers = {
        "Accept": "application/json"
    }
    json_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    res = requests.post(url=url, headers=headers, json=json_data, timeout=10)
    res_dict = json.loads(res.text)
    res_dict["token_at"] = int(time.time()) - 5
    return res_dict


def get_expires_at_by_access_token_info(access_token_info):
    refresh_token_expires_in = access_token_info["refresh_token_expires_in"]
    token_at = access_token_info["token_at"]
    return token_at + refresh_token_expires_in


def get_github_user_info_by_access_token(access_token):
    url = "https://api.github.com/user"
    headers = {
        "Authorization": "token {}".format(access_token)
    }

    res = requests.get(url=url, headers=headers, timeout=10)
    return json.loads(res.text)


def get_github_org_id(access_token, org):
    # curl \
    # -H "Authorization: token <access_token>" \
    # -H "Accept: application/vnd.github.v3+json" \
    # https://api.github.com/orgs/<org>
    url = "https://api.github.com/orgs/{}".format(org)
    headers = {
        "Accept": "application/json",
        "Authorization": "token {}".format(access_token)
    }
    res = requests.get(url=url, headers=headers, timeout=10)
    res_json = json.loads(res.text)
    if res_json.get("message"):
        return None
    return res_json["id"]


def org_member_role_is_admin(access_token, org, username):
    # curl \
    # -H "Authorization: token <access_token>" \
    # -H "Accept: application/vnd.github.v3+json" \
    # https://api.github.com/orgs/<org>/memberships/<username>
    # access_token 是 github app 授权获取的
    # 如果 org 没有安装 github app ，那么访问这个接口会看到
    # You must be a member of <org> to see membership information for <username>
    # 不过不影响整体业务需要
    url = "https://api.github.com/orgs/{}/memberships/{}".format(org, username)
    headers = {
        "Accept": "application/json",
        "Authorization": "token {}".format(access_token)
    }
    res = requests.get(url=url, headers=headers, timeout=10)
    res_json = json.loads(res.text)

    if res_json.get("message"):
        return False
    return res_json["role"] == "admin"


def check_icp_app_installed_status_of_org(jwt, org):
    # curl \
    # -H "Authorization: Bearer <jwt>" \
    # -H "Accept: application/vnd.github.v3+json" \
    # https://api.github.com/orgs/<org>/installation
    url = "https://api.github.com/orgs/{}/installation".format(org)
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(jwt)
    }
    res = requests.get(url=url, headers=headers, timeout=10)
    res_json = json.loads(res.text)

    if res_json.get("message"):
        return False
    return True


def get_icp_app_jwt(github_app_id, github_app_private_key):
    d = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=2*60),
        'iat': datetime.datetime.utcnow(),
        'iss': github_app_id
    }

    tok = jwt.encode(d, github_app_private_key, algorithm='RS256')
    if isinstance(tok, bytes):
        tok = tok.decode('utf8')

    return tok
