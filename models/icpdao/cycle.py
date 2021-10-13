import enum
import time

from mongoengine import Document, EmbeddedDocument, BooleanField, IntField, StringField, \
    EmbeddedDocumentListField, ListField

from ..extension.decimal128_field import Decimal128Field


class CycleVoteType(enum.Enum):
    PAIR = 0
    ALL = 1


class CycleVoteConfirmStatus(enum.Enum):
    WAITING = 0
    CONFIRM = 1


class VoteResultTypeAllResultType(enum.Enum):
    YES = 0
    NO = 1


class CycleVotePairTaskStatus(enum.Enum):
    INIT = 0
    PAIRING = 1
    SUCCESS = 2
    FAIL = 3


class CycleVoteResultStatTaskStatus(enum.Enum):
    INIT = 0
    STATING = 1
    SUCCESS = 2
    FAIL = 3


class CycleVoteResultPublishTaskStatus(enum.Enum):
    INIT = 0
    RUNNING = 1
    SUCCESS = 2
    FAIL = 3


class VoteResultTypeAll(EmbeddedDocument):
    voter_id = StringField(required=True)
    result = IntField(
        required=True,
        choices=[i.value for i in list(VoteResultTypeAllResultType)]
    )

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class Cycle(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle'
    }
    """
    16-00 - 15-24 计算job 范围
    16-12 - 17-24 owner 配对时间范围
    18-00 - 19-12 投票时间范围

    for wu
    job vote_type
    cycle_vote table name
    """
    dao_id = StringField(required=True)
    time_zone = IntField(required=True, default=480)

    begin_at = IntField(required=True, default=time.time)
    end_at = IntField(required=True, default=time.time)

    pair_begin_at = IntField(required=True, default=time.time)
    pair_end_at = IntField(required=True, default=time.time)

    vote_begin_at = IntField(required=True, default=time.time)
    vote_end_at = IntField(required=True, default=time.time)

    paired_at = IntField()
    vote_result_stat_at = IntField()
    vote_result_published_at = IntField()

    token_released_at = IntField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class CycleIcpperStat(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_icpper_stat'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)
    user_id = StringField(required=True)

    job_count = IntField(required=True, default=0)
    # all merged job size
    job_size = Decimal128Field(required=True, precision=1, default="0")
    # get size
    size = Decimal128Field(required=True, precision=1, default="0")
    income = Decimal128Field(required=True, precision=3, default="0")
    # at the vote end , not voted all vote
    un_voted_all_vote = BooleanField()
    # have two times lt 0.8
    have_two_times_lt_08 = BooleanField()
    # have two times lt 0.4
    have_two_times_lt_04 = BooleanField()

    vote_ei = Decimal128Field(precision=2)
    owner_ei = Decimal128Field(precision=2)
    ei = Decimal128Field(precision=2)

    # current cycle have warning review user id list
    be_reviewer_has_warning_user_ids = ListField(default=[])
    # review 扣除的 size
    be_deducted_size_by_review = Decimal128Field(precision=2)

    # user_id 在 dao_id 中的上一个 cycle_icpper_stat.id
    last_id = StringField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class CycleVote(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_vote'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)

    left_job_id = StringField(required=True)
    right_job_id = StringField(required=True)

    vote_type = IntField(
        required=True,
        default=CycleVoteType.PAIR.value,
        choices=[i.value for i in list(CycleVoteType)]
    )

    # type pair
    vote_job_id = StringField()
    voter_id = StringField()

    # type all
    # TODO 并发是否有问题
    vote_result_type_all = EmbeddedDocumentListField(VoteResultTypeAll)
    vote_result_stat_type_all = IntField()  # 赞同的百分比

    is_result_public = BooleanField(required=True, default=False)

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class CycleVoteConfirm(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_vote_confirm'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)
    voter_id = StringField(required=True)

    signature_address = StringField()
    signature_msg = StringField()
    signature = StringField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)

    status = IntField(
        required=True,
        default=CycleVoteConfirmStatus.WAITING.value,
        choices=[i.value for i in list(CycleVoteConfirmStatus)]
    )


class CycleVotePairTask(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_vote_pair_task'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)

    status = IntField(
        required=True,
        default=CycleVotePairTaskStatus.INIT.value,
        choices=[i.value for i in list(CycleVotePairTaskStatus)]
    )

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class CycleVoteResultStatTask(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_vote_result_stat_task'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)

    status = IntField(
        required=True,
        default=CycleVoteResultStatTaskStatus.INIT.value,
        choices=[i.value for i in list(CycleVoteResultStatTaskStatus)]
    )

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class CycleVoteResultPublishTask(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'cycle_vote_result_publish_task'
    }

    dao_id = StringField(required=True)
    cycle_id = StringField(required=True)

    status = IntField(
        required=True,
        default=CycleVoteResultPublishTaskStatus.INIT.value,
        choices=[i.value for i in list(CycleVoteResultPublishTaskStatus)]
    )

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)
