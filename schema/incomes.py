from graphene import ObjectType, String

from ..models.extension.graphene_decimal128 import Decimal128Float


class TokenIncomeSchema(ObjectType):
    token_chain_id = String()
    token_address = String()
    token_symbol = String()
    income = Decimal128Float()
