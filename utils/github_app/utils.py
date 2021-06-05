import enum
from typing import MutableMapping
from urllib.parse import urlparse


class LinkType(enum.Enum):
    other = 0
    issue = 1
    pr = 2


def parse_issue(issue: str, github_repo_owner: str) -> MutableMapping:
    try:
        url_parse = urlparse(issue)
        if url_parse.scheme not in ['http', 'https']:
            return {'success': False, 'msg': 'NOT URL'}
        if url_parse.netloc == 'github.com':
            paths = url_parse.path.split('/')
            if paths[3] != 'issues':
                return {'success': False, 'msg': 'NOT ISSUE'}
            if paths[1] != github_repo_owner:
                return {'success': False, 'msg': 'NOT RIGHT OWNER'}
            return {
                'success': True,
                'type': LinkType.issue,
                'parse': {
                    'github_repo_owner': paths[1],
                    'github_repo_name': paths[2],
                    'github_issue_number': int(paths[4])
                }
            }
        return {'success': False, 'msg': 'PARSE ISSUE ERROR'}
    except Exception as e:
        return {'success': False, 'msg': 'PARSE ISSUE ERROR'}


def parse_pr(pr: str, github_repo_owner: str) -> MutableMapping:
    try:
        url_parse = urlparse(pr)
        if url_parse.scheme not in ['http', 'https']:
            return {'success': False, 'msg': 'NOT URL'}
        if url_parse.netloc == 'github.com':
            paths = url_parse.path.split('/')
            if paths[3] != 'pull':
                return {'success': False, 'msg': 'NOT PR'}
            if paths[1] != github_repo_owner:
                return {'success': False, 'msg': 'NOT RIGHT OWNER'}
            return {
                'success': True,
                'type': LinkType.pr,
                'parse': {
                    'github_repo_owner': paths[1],
                    'github_repo_name': paths[2],
                    'github_pr_number': int(paths[4])
                }
            }
        return {'success': True, 'type': LinkType.other}
    except Exception as e:
        return {'success': False, 'msg': 'PARSE PR ERROR'}


if __name__ == '__main__':
    print(parse_issue(
        'https://github.com/icpdao/icpdao-interface/issues/27', 'icpdao'))
    print(parse_issue(
        'http://github.com/icp1dao/icpdao-interface/issues/27', 'icpdao'))
    print(parse_issue(
        'https://www.figma.com/file/LffQCyu0jaU7KyXyU4VldM/ICPDAO-day?node-id=3669%3A16866', 'icpdao'))
    print(parse_issue(
        'http://www.figma.com/file/LffQCyu0jaU7KyXyU4VldM/ICPDAO-day?node-id=3669%3A16866', 'icpdao'))
    print(parse_issue(
        'xxx', 'icpdao'))
    print(parse_issue(
        'file://xxx', 'icpdao'))
    print(parse_pr(
        'https://github.com/icpdao/icpdao-interface/pull/41', 'icpdao'))

