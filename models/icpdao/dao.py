import time

from mongoengine import Document, StringField, IntField, SequenceField


class DAO(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'dao'
    }
    # DAO unique counter
    number = SequenceField(required=True, unique=True, db_alias='icpdao')

    name = StringField(required=True, unique=True)
    logo = StringField()
    desc = StringField()
    # DAO owner user id
    owner_id = StringField(required=True)
    # github owner id
    github_owner_id = IntField(required=True)
    # github owner name
    github_owner_name = StringField(required=True)

    # 创建时间
    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class DAOFollow(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'dao_follow'
    }

    dao_id = StringField(required=True)
    user_id = StringField(required=True)
    create_at = IntField(required=True, default=time.time)


class DAOGithub(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'dao_github'
    }

    dao_id = StringField(required=True)
    installation_id = StringField(required=True)


class DAOJobConfig(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'dao_job_config'
    }

    dao_id = StringField(required=True)
    time_zone = IntField(required=True, default=480)
    time_zone_region = StringField(required=True, default='Asia/Shanghai')
    deadline_day = IntField(required=True, max_value=28, min_value=1, default=1)
    deadline_time = IntField(required=True, max_value=24, min_value=0, default=12)

    pair_begin_day = IntField(required=True, max_value=28, min_value=1, default=1)
    pair_begin_hour = IntField(required=True, max_value=24, min_value=0, default=12)
    pair_end_day = IntField(required=True, max_value=28, min_value=1, default=2)
    pair_end_hour = IntField(required=True, max_value=24, min_value=0, default=12)

    voting_begin_day = IntField(required=True, max_value=28, min_value=1, default=1)
    voting_begin_hour = IntField(required=True, max_value=24, min_value=0, default=12)
    voting_end_day = IntField(required=True, max_value=28, min_value=1, default=2)
    voting_end_hour = IntField(required=True, max_value=24, min_value=0, default=12)

    # 创建时间
    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)
