from bson import Decimal128
from graphene_mongo.converter import convert_mongoengine_field
from graphene_mongo.utils import get_field_description
from graphene.types.scalars import Scalar
from graphql.language.ast import FloatValue, IntValue

from .decimal128_field import Decimal128Field


class Decimal128Float(Scalar):
    """
    The `Float` scalar type represents signed double-precision fractional
    values as specified by
    [IEEE 754](http://en.wikipedia.org/wiki/IEEE_floating_point).
    """

    @staticmethod
    def coerce_float(value):
        # type: (Any) -> float
        try:
            if isinstance(value, Decimal128):
                value = value.to_decimal()
            return float(value)
        except ValueError:
            return None

    serialize = coerce_float
    parse_value = coerce_float

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (FloatValue, IntValue)):
            return float(ast.value)


@convert_mongoengine_field.register(Decimal128Field)
def convert_field_to_float_1(field, registry=None):
    return Decimal128Float(
        description=get_field_description(field, registry), required=field.required
    )
