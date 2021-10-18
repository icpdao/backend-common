from typing import List, Optional

from mongoengine import EmbeddedDocument, StringField, QuerySet

from ..extension.decimal128_field import Decimal128Field
from ...schema.incomes import TokenIncomeSchema


class TokenIncome(EmbeddedDocument):
    token_chain_id = StringField(required=True)
    token_address = StringField(required=True)
    income = Decimal128Field(required=True, precision=3, default=0)


class TokenIncomeQuerySet(QuerySet):
    def sum_incomes(self, token_chain_id: str) -> int:
        ret = tuple(self.filter(incomes__token_chain_id=token_chain_id).aggregate([
            {"$unwind": "$incomes"},
            {"$match": {"incomes.token_chain_id": token_chain_id}},
            {"$group": {"_id": "sum", "total": {"$sum": "$incomes.income"}}},
        ]))
        if ret:
            return ret[0]["total"]
        return 0

    def group_incomes(self, group_id: Optional[List[str]] = None, token_chain_id: Optional[str] = None):
        group_key = {
            "token_chain_id": "$incomes.token_chain_id",
            "token_address": "$incomes.token_address"
        }
        if group_id is not None:
            for _id in group_id:
                group_key[_id] = f"${_id}"
        query = self
        agg = [
            {"$unwind": "$incomes"},
            {"$group": {"_id": group_key, "income": {"$sum": "$incomes.income"}}},
        ]
        if token_chain_id is not None:
            query = self.filter(incomes__token_chain_id=token_chain_id)
            agg = [
                {"$unwind": "$incomes"},
                {"$match": {"incomes.token_chain_id": token_chain_id}},
                {"$group": {"_id": group_key, "income": {"$sum": "$incomes.income"}}},
            ]
        ret = tuple(query.aggregate(agg))
        if not ret:
            return []
        schemas = [TokenIncomeSchema(
            token_chain_id=r["_id"]["token_chain_id"],
            token_address=r["_id"]["token_address"],
            income=r["income"]
        ) for r in ret]
        return schemas
