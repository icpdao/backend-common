import decimal
import enum
import time

from mongoengine import EmbeddedDocument, Document, EmbeddedDocumentListField, StringField, IntField, ListField, BooleanField

from ..extension.decimal128_field import Decimal128Field


class TokenTransferEventLog(EmbeddedDocument):
    to_address = StringField(required=True)
    value = Decimal128Field(required=True)


class MintRadtio:
    ICPPER_RATIO = decimal.Decimal("0.95")
    MENTOR_BASE_ALL_RATIO = decimal.Decimal("0.05")

    MENTOR_7_LELVES_RATIO_LIST = [
        decimal.Decimal("0.5"),
        decimal.Decimal("0.25"),
        decimal.Decimal("0.13"),
        decimal.Decimal("0.06"),
        decimal.Decimal("0.03"),
        decimal.Decimal("0.02"),
        decimal.Decimal("0.01")
    ]


class MintIcpperRecordMeta(EmbeddedDocument):
    """
    level1 size * 10000 * 0.05 * 0.5
    level2 size * 10000 * 0.05 * 0.25
    level3 size * 10000 * 0.05 * 0.13
    level4 size * 10000 * 0.05 * 0.06
    level5 size * 10000 * 0.05 * 0.03
    level6 size * 10000 * 0.05 * 0.02
    level7 size * 10000 * 0.05 * 0.01
    """
    mentor_id = StringField()
    mentor_eth_address = StringField()
    mentor_radio = Decimal128Field()


class MintIcpperRecord(EmbeddedDocument):
    user_id = StringField(required=True)
    user_eth_address = StringField(required=True)
    user_ratio = Decimal128Field(required=True)
    # 按照顺序保存 上级，上上级...上七级
    mentor_list = EmbeddedDocumentListField(MintIcpperRecordMeta)


class MintRecordStatusEnum(enum.Enum):
    INIT = 0
    PENDING = 1
    SUCCESS = 2
    FAIL = 3
    DROPED = 100


class TokenMintRecord(Document):
    meta = {
        'db_alias': 'icpdao',
        'collection': 'token_mint_record'
    }
    dao_id = StringField(required=True)
    token_contract_address = StringField(required=True)
    chain_id = StringField(required=True)
    start_cycle_id = StringField()
    end_cycle_id = StringField()
    cycle_ids = ListField(StringField())

    status = IntField(
        required=True,
        default=MintRecordStatusEnum.INIT.value,
        choices=[i.value for i in list(MintRecordStatusEnum)]
    )
    stated = BooleanField()
    mint_icpper_records = EmbeddedDocumentListField(MintIcpperRecord)
    token_transfer_event_logs = EmbeddedDocumentListField(TokenTransferEventLog)

    total_real_size = Decimal128Field(required=True)
    unit_real_size_value = Decimal128Field()

    # mint params
    mint_token_address_list = ListField(StringField())
    mint_token_amount_ratio_list = ListField(Decimal128Field())
    start_timestamp = IntField(required=True)
    end_timestamp = IntField(required=True)
    tick_lower = IntField(required=True)
    tick_upper = IntField(required=True)

    # mint result
    mint_value = Decimal128Field()

    # eth
    mint_tx_hash = StringField()
    block_number = IntField()

    mint_params_has_diff = BooleanField()

    create_at = IntField(required=True, default=time.time)
    update_at = IntField(required=True, default=time.time)
    drop_at = IntField()
    last_sync_event_at = IntField()


class MentorTokenIncomeStat(Document):
    """
    icpper 和 icpper 以下的六级 icpper
    一共给 mentor 这个人贡献的 $token 类型代币 数量是多少
    """
    meta = {
        'db_alias': 'icpdao',
        'collection': 'mentor_token_income_stat'
    }
    mentor_id = StringField(required=True)
    icpper_id = StringField(required=True)

    dao_id = StringField(required=True)
    token_contract_address = StringField(required=True)
    token_name = StringField(required=True)
    token_symbol = StringField(required=True)
    total_value = Decimal128Field(required=True)
