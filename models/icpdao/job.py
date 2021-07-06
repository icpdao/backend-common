import enum
import time


from mongoengine import Document, StringField, IntField, EnumField, DecimalField, ListField


class JobStatusEnum(enum.Enum):
    AWAITING_MERGER = 0
    MERGED = 1
    AWAITING_VOTING = 2
    WAITING_FOR_TOKEN = 3
    TOKEN_RELEASED = 4


class JobPairTypeEnum(enum.Enum):
    PAIR = 0
    ALL = 1


class JobPRStatusEnum(enum.Enum):
    AWAITING_MERGER = 0
    MERGED = 1


class Job(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'job'
    }
    dao_id = StringField(required=True)
    user_id = StringField(required=True)

    title = StringField(required=True)
    body_text = StringField()
    # TODO 增加 labels 处理
    labels = ListField(StringField())

    size = DecimalField(required=True, precision=1)

    github_repo_owner = StringField(required=True)
    github_repo_name = StringField(required=True)
    github_repo_id = IntField(required=True)
    github_issue_number = IntField(required=True)

    bot_comment_database_id = IntField(required=True)
    status = IntField(required=True,
                      default=JobStatusEnum.AWAITING_MERGER.value,
                      choices=[i.value for i in list(JobStatusEnum)])

    # income only exist in TOKEN_RELEASED
    income = IntField(required=True, default=0)

    # vote type
    pair_type = IntField(required=True,
                         default=JobPairTypeEnum.PAIR.value,
                         choices=[i.value for i in list(JobPairTypeEnum)])

    cycle_id = StringField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class JobPR(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'job_pr'
    }

    # TODO 增加 cycle_id 外键
    job_id = StringField(required=True)
    user_id = StringField(required=True)
    title = StringField(required=True)

    github_repo_owner = StringField(required=True)
    github_repo_name = StringField(required=True)
    github_repo_id = IntField(required=True)
    github_pr_number = IntField(required=True)

    status = IntField(required=True,
                      default=JobPRStatusEnum.AWAITING_MERGER.value,
                      choices=[i.value for i in list(JobPRStatusEnum)])

    merged_user_github_user_id = IntField()

    merged_at = IntField()

    create_at = IntField(required=True, default=time.time)


class JobPRComment(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'job_pr_comment'
    }

    github_repo_id = IntField(required=True)
    github_pr_number = IntField(required=True)
    bot_comment_database_id = IntField(required=True)

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)
