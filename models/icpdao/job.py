import enum
import time


from mongoengine import Document, StringField, IntField, EnumField, DecimalField


class JobStatusEnum(enum.Enum):
    AWAITING_MERGER = 0
    MERGED = 1
    AWAITING_VOTING = 2
    WAITING_FOR_TOKEN = 3
    TOKEN_RELEASED = 4


class JobPRStatusEnum(enum.Enum):
    OPEN = 0
    MERGED = 1
    CLOSED = 2


class Job(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'job'
    }
    dao_id = StringField(required=True)
    user_id = StringField(required=True)

    title = StringField(required=True)
    body_text = StringField()
    size = DecimalField(required=True, precision=1)

    github_repo_owner = StringField(required=True)
    github_repo_name = StringField(required=True)
    github_issue_number = IntField(required=True)

    bot_comment_database_id = IntField(required=True)
    status = EnumField(JobStatusEnum, default=JobStatusEnum.AWAITING_MERGER)

    # income should be a separate table

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)

    @classmethod
    def generate_bot_comment_body(cls, user_name):
        body = """
Job status: %s
Job user: %s
Job size: %s
""" % (JobStatusEnum[cls.status], user_name, cls.size)
        return body


class JobPR(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'job_pr'
    }

    job_id = StringField(required=True)
    title = StringField(required=True)

    github_repo_owner = StringField(required=True)
    github_repo_name = StringField(required=True)
    github_issue_number = IntField(required=True)

    bot_comment_database_id = IntField(required=True)

    status = EnumField(JobPRStatusEnum, default=JobPRStatusEnum.OPEN)

    merged_user_github_login = StringField()
    merged_at = IntField()
