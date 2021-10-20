from enum import Enum
import time
from mongoengine import Document, StringField, IntField, BooleanField, EmbeddedDocumentListField, EmbeddedDocument


class IcppershipProgress(Enum):
    PENDING     = 0 # 用户收到邀请状态时的值
    ACCEPT      = 1 # 用户接受邀请状态时的值


class IcppershipStatus(Enum):
    # 冗余数据，同步记录 icpper_user.status
    NORMAL      = 0
    PRE_ICPPER  = 1
    ICPPER      = 2


class Icppership(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'icppership'
    }

    # 邀请进度
    progress = IntField(required=True,
        default=IcppershipProgress.PENDING.value,
        choices=[i.value for i in list(IcppershipProgress)])

    # 用户状态
    status = IntField(required=True,
        default=IcppershipStatus.NORMAL.value,
        choices=[i.value for i in list(IcppershipStatus)])

    icpper_github_login = StringField(required=True, max_length=255)

    mentor_user_id = StringField(required=True)
    icpper_user_id = StringField()

    # 创建时间
    create_at = IntField(required=True, default=time.time)

    # 用户接受邀请时的时间
    accept_at = IntField()

    # 用户成为 icpper 的时间
    icpper_at = IntField()


class MentorRelationStatTokenStat(EmbeddedDocument):
    token_chain_id = StringField()
    token_count = IntField()


class MentorRelationStat(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'mentor_relation_stat'
    }
    mentor_id = StringField(required=True)
    icpper_id = StringField(required=True)
    relation = BooleanField(required=True, default=True)  # mentor icpper 关系是否还在保持
    has_reward_icpper_count = IntField()
    token_stat = EmbeddedDocumentListField(MentorRelationStatTokenStat)
    # token_chain_id = StringField()
    # token_count = IntField()


class MentorLevel7IcpperCountStat(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'mentor_level7_icpper_count_stat'
    }

    mentor_id = StringField(required=True)
    level_1_count = IntField(required=True)
    level_2_count = IntField(required=True)
    level_3_count = IntField(required=True)
    level_4_count = IntField(required=True)
    level_5_count = IntField(required=True)
    level_6_count = IntField(required=True)
    level_7_count = IntField(required=True)
