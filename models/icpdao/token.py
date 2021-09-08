import enum
import time

from mongoengine import EmbeddedDocument, Document, EmbeddedDocumentListField, StringField, IntField, EnumField, DecimalField, ListField, BooleanField


class TokenTransferEventLog(EmbeddedDocument):
    to_address = StringField(required=True)
    value = DecimalField(required=True)


class MintIcpperRecord(EmbeddedDocument):
    user_id = StringField(required=True)
    user_eth_address = StringField(required=True)
    user_radio = DecimalField(required=True)  # size * 10000 * 0.95

    level_1_mentor_id = StringField()
    level_1_mentor_eth_address = StringField()
    level_1_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.5

    level_2_mentor_id = StringField()
    level_2_mentor_eth_address = StringField()
    level_2_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.25

    level_3_mentor_id = StringField()
    level_3_mentor_eth_address = StringField()
    level_3_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.13

    level_4_mentor_id = StringField()
    level_4_mentor_eth_address = StringField()
    level_4_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.06

    level_5_mentor_id = StringField()
    level_5_mentor_eth_address = StringField()
    level_5_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.03

    level_6_mentor_id = StringField()
    level_6_mentor_eth_address = StringField()
    level_6_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.02

    level_7_mentor_id = StringField()
    level_7_mentor_eth_address = StringField()
    level_7_mentor_radio = DecimalField()  # size * 10000 * 0.05 * 0.01


class MintRecordStatusEnum(enum.Enum):
    INIT = 0
    PENDING = 1
    SUCCESS = 2
    FAIL = 3


class TokenMintRecord(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'token_mint_record'
    }
    dao_id = StringField(required=True)
    token_contract_address = StringField(required=True)

    status = IntField(
        required=True,
        default=MintRecordStatusEnum.INIT.value,
        choices=[i.value for i in list(MintRecordStatusEnum)]
    )
    stated = BooleanField()
    mint_icpper_records = EmbeddedDocumentListField(MintIcpperRecord)
    token_transfer_event_logs = EmbeddedDocumentListField(TokenTransferEventLog)

    # mint params
    mint_token_address_list = ListField(StringField())
    mint_token_amount_ratio_list = ListField(IntField())
    start_timestamp = IntField(required=True, default=time.time)
    end_timestamp = IntField(required=True, default=time.time)
    tick_lower = IntField(required=True)
    tick_upper = IntField(required=True)

    # mint result
    mint_value = DecimalField()

    # eth
    mint_tx_hash = StringField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)


class TokenMintMentorRewardStat(Document):
    """
    icpper 和 icpper 以下的六级 icpper
    一共给 mentor 这个人贡献的 $token 类型代币 数量是多少
    """
    meta = {
        'db_alias': 'icpdao',
        'collection': 'token_mint_mentor_reward_stat'
    }
    mentor_id = StringField(required=True)
    icpper_id = StringField(required=True)
    relation = BooleanField(required=True, default=True)  # mentor icpper 关系是否还在保持
    dao_id = StringField(required=True)
    token_contract_address = StringField(required=True)
    token_name = StringField(required=True)
    total_value = DecimalField(required=True)
