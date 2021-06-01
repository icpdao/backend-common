import requests
import json
import datetime
import jwt


def get_github_org_id(org):
    # curl \
    # -H "Accept: application/vnd.github.v3+json" \
    # https://api.github.com/orgs/<org>
    url = "https://api.github.com/orgs/{}".format(org)
    headers = {
        "Accept": "application/json"
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
