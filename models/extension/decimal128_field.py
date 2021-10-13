# from: https://github.com/MongoEngine/mongoengine/pull/2521
# proposal: implement Decimal128Field
import decimal

from bson.decimal128 import Decimal128, create_decimal128_context
from mongoengine.fields import BaseField


def any_to_decimal(value):
    if isinstance(value, Decimal128):
        return value.to_decimal()
    if isinstance(value, int):
        value = str(value)
    if isinstance(value, float):
        value = str(value)
    return decimal.Decimal(value)


class Decimal128Field(BaseField):
    """

    128-bit decimal-based floating-point field capable of emulating decimal
    rounding with exact precision. Stores the value as a `Decimal128`
    intended for monetary data, such as financial, tax, and scientific
    computations.
    """

    DECIMAL_CONTEXT = create_decimal128_context()

    def __init__(self,
         min_value=None,
         max_value=None,
         precision=2,
         rounding=decimal.ROUND_HALF_UP,
         **kwargs
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision
        self.rounding = rounding
        super().__init__(**kwargs)

    def to_mongo(self, value):
        if value is None:
            return None
        if isinstance(value, Decimal128):
            return value
        if not isinstance(value, decimal.Decimal):
            with decimal.localcontext(self.DECIMAL_CONTEXT) as ctx:
                value = ctx.create_decimal(value)
        value = value.quantize(
            decimal.Decimal(".%s" % ("0" * self.precision)), rounding=self.rounding
        )
        return Decimal128(value)

    def to_python(self, value):
        if value is None:
            return None
        value = self.to_mongo(value).to_decimal()
        return value.quantize(
            decimal.Decimal(".%s" % ("0" * self.precision)), rounding=self.rounding
        )

    def validate(self, value):
        if not isinstance(value, Decimal128):
            try:
                if isinstance(value, int):
                    value = str(value)
                if isinstance(value, float):
                    value = str(value)
                value = Decimal128(value)
            except (TypeError, ValueError, decimal.InvalidOperation) as exc:
                self.error("Could not convert value to Decimal128: %s" % exc)

        if self.min_value is not None and value.to_decimal() < self.min_value:
            self.error("Decimal value is too small")

        if self.max_value is not None and value.to_decimal() > self.max_value:
            self.error("Decimal value is too large")

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, self.to_mongo(value))
