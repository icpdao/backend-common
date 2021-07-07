import time
import datetime
import iso8601
import requests
import base64

from app.common.models.icpdao.job import JobPRStatusEnum


class GithubAPIRequest:
    rest_api = 'https://api.github.com'

    def __init__(self, token: str):
        self.req = requests
        self.normal = {
            'headers': {
                "Accept": "application/json",
                "Authorization": f"token {token}"
            },
            'timeout': 10
        }

    @staticmethod
    def __get_return(ret):
        try:
            data = ret.json()
            if isinstance(data, list):
                return True, data
            if data.get('message') is None:
                return True, data
            return False, data
        except Exception as e:
            return False, {}

    def get(self, url, **kwargs):
        ret = self.req.get(self.rest_api + url, **self.normal, **kwargs)
        return self.__get_return(ret)

    def post(self, url, json, **kwargs):
        ret = self.req.post(
            self.rest_api + url, json=json, **self.normal, **kwargs)
        return self.__get_return(ret)

    def put(self, url, json, **kwargs):
        ret = self.req.put(
            self.rest_api + url, json=json, **self.normal, **kwargs)
        return self.__get_return(ret)

    def patch(self, url, json, **kwargs):
        ret = self.req.patch(
            self.rest_api + url, json=json, **self.normal, **kwargs)
        return self.__get_return(ret)

    def delete(self, url):
        ret = self.req.delete(
            self.rest_api + url, **self.normal)
        return self.__get_return(ret)


class GithubAppClient:
    auto_content_path = 'file_bot'

    def __init__(self, token: str, repo_owner: str):
        self.request = GithubAPIRequest(token)
        self.repo_owner = repo_owner

    def create_comment(self, repo_name, pr_number, body):
        return self.__create_comment(repo_name, pr_number, body)

    def update_comment(self, repo_name, comment_id, body):
        return self.__update_comment(repo_name, comment_id, body)

    def delete_comment(self, repo_name, comment_id):
        return self.__delete_comment(repo_name, comment_id)

    def get_issue(self, repo_name, issue_number):
        return self.__get_issue(repo_name, issue_number)

    def get_repo(self, repo_name):
        return self.__get_repo(repo_name)

    def get_pr(self, repo_name, pr_number):
        success, res = self.__get_pr(repo_name, pr_number)
        if not success:
            return False, res.get('message')
        can_link_github_user_id_list = set()
        success, revs = self.__get_pr_reviews(repo_name, pr_number)
        if success:
            for re in revs:
                if re.get('state') in ['APPROVE', 'REQUEST_CHANGES', 'COMMENT']:
                    can_link_github_user_id_list.add(re.get('user', {}).get('id'))
        can_link_github_user_id_list.add(res.get('user', {}).get('id'))
        merged_user_github_user_id = None
        if res.get('merged_by'):
            can_link_github_user_id_list.add(res.get('merged_by').get('id'))
            merged_user_github_user_id = res.get('merged_by').get('id')
        merged_at = res.get('merged_at')
        if merged_at:
            merged_at = iso8601.parse_date(res['merged_at'])
            merged_at = int(
                merged_at.replace(tzinfo=datetime.timezone.utc).timestamp())
        return True, {
            'id': res['id'],
            'node_id': res['node_id'],
            'number': res['number'],
            'state': JobPRStatusEnum.MERGED.value if res.get('merged') else JobPRStatusEnum.AWAITING_MERGER.value,
            'title': res['title'],
            'created_at': res['created_at'], 'updated_at': res['updated_at'],
            'closed_at': res.get('closed_at'), 'merged_at': merged_at,
            'user_login': res['user']['login'],
            'can_link_github_user_id_list': can_link_github_user_id_list,
            'merged_user_github_user_id': merged_user_github_user_id
        }

    def create_pr(self, link, repo_name, issue_number, github_login):
        branch_key = f'icpdao/bot_{github_login}'
        success, base_sha = self.__create_or_get_auto_branch(
            repo_name, branch_key)
        if not success:
            return False, "CAN'T CREATE AUTO BRANCH"
        tmp_branch = f'icpdao/bot_{github_login}_{int(time.time())}'
        success, new_refs = self.__create_refs(
            repo_name, f'refs/heads/{tmp_branch}', base_sha)
        if not success:
            return False, "CAN'T CREATE TMP BRANCH"
        success, res = self.__create_update_file(
            repo_name, issue_number, github_login, tmp_branch, link)
        if not success:
            return False, "CAN'T CREATE UPDATE FILE"
        pr_title = f'feat: #{issue_number} @{github_login} auto pr by @icpdao'

        success, res = self.__create_pr(
            repo_name, tmp_branch, branch_key, pr_title)
        if not success:
            return False, "CAN'T CREATE PR"
        if not success:
            return False, "CAN'T ADD COMMENT"
        return True, {
            'id': res['id'],
            'node_id': res['node_id'],
            'number': res['number'],
            'state': JobPRStatusEnum.AWAITING_MERGER.value,
            'title': res['title'],
        }

    def __init_repo_file(self, repo_name):
        url = f"/repos/{self.repo_owner}/{repo_name}/contents/{self.auto_content_path}/README.md"
        success, res = self.request.put(url, {
            "message": 'init icpdao file by bot',
            "content": self.__encode_base64_content(
                'this is icpdao bot auto file.'),
        })
        return res.get('commit', {}).get('sha')

    def __create_update_file(
            self, repo_name, issue_number, github_login, branch, link):
        url = f"/repos/{self.repo_owner}/{repo_name}/contents/{self.auto_content_path}/{github_login}_{issue_number}_{int(time.time())}.md"
        return self.request.put(url, {
            "message": f'for {self.repo_owner}/{repo_name}#{issue_number} by @{github_login}',
            "content": self.__encode_base64_content(link),
            "branch": branch
        })

    def __create_or_get_auto_branch(
            self, repo_name, branch_key):
        success, branch_record = self.__get_branch(repo_name, branch_key)
        if success:
            return True, branch_record.get('commit', {}).get('sha')

        base_branch = self.__get_repo(repo_name).get('default_branch')
        success, base_branch_record = self.__get_branch(
            repo_name, base_branch)
        base_sha = base_branch_record.get('commit', {}).get('sha')
        if base_sha is None:
            base_sha = self.__init_repo_file(repo_name)
        if base_sha is None:
            return False, "CAN'T INIT REPO OR GET REPO SHA"

        success, new_refs = self.__create_refs(
            repo_name, f'refs/heads/{branch_key}', base_sha)
        if success:
            return True, new_refs.get('object', {}).get('sha')
        return False, "CAN'T CREATE AUTO BRANCH"

    def __get_repo(self, repo_name):
        url = f'/repos/{self.repo_owner}/{repo_name}'
        success, res = self.request.get(url)
        return res

    def __get_branch(self, repo_name, branch):
        url = f'/repos/{self.repo_owner}/{repo_name}/branches/{branch}'
        return self.request.get(url)

    def __create_refs(self, repo_name, ref, sha):
        url = f'/repos/{self.repo_owner}/{repo_name}/git/refs'
        return self.request.post(url, {'ref': ref, 'sha': sha})

    def __create_pr(self, repo_name, head, base, title):
        url = f'/repos/{self.repo_owner}/{repo_name}/pulls'
        return self.request.post(url, {
            'head': head, 'base': base, 'title': title})

    def __create_comment(self, repo_name, pr_number, body):
        url = f'/repos/{self.repo_owner}/{repo_name}/issues/{pr_number}/comments'
        return self.request.post(url, {'body': body})

    def __update_comment(self, repo_name, comment_id, new_body):
        url = f'/repos/{self.repo_owner}/{repo_name}/issues/comments/{comment_id}'
        return self.request.patch(url, {'body': new_body})

    def __delete_comment(self, repo_name, comment_id):
        url = f'/repos/{self.repo_owner}/{repo_name}/issues/comments/{comment_id}'
        return self.request.delete(url)

    def __get_pr(self, repo_name, pr_number):
        url = f'/repos/{self.repo_owner}/{repo_name}/pulls/{pr_number}'
        return self.request.get(url)

    def __get_pr_reviews(self, repo_name, pr_number):
        url = f'/repos/{self.repo_owner}/{repo_name}/pulls/{pr_number}/reviews'
        return self.request.get(url)

    def __get_issue(self, repo_name, issue_number):
        url = f'/repos/{self.repo_owner}/{repo_name}/issues/{issue_number}'
        return self.request.get(url)

    @staticmethod
    def __encode_base64_content(content: str):
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')

    def __pr_comment(self, repo_name, issue_number, github_login):
        return f'for {self.repo_owner}/{repo_name}#{issue_number} by @{github_login} & @icpdao'
