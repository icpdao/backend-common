import json
from os import getenv
import random
import pytest
from decimal import Decimal
import unittest

from bson.decimal128 import Decimal128
from mongoengine import *
from mongoengine.connection import disconnect_all, get_db

from .decimal128_field import Decimal128Field
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.'))

MONGO_TEST_HOST = getenv("ICPDAO_MONGODB_ICPDAO_HOST")
MONGO_TEST_DB = 'mongoenginetest'


class MongoDBTestCase(unittest.TestCase):
    """Base class for tests that need a mongodb connection
    It ensures that the db is clean at the beginning and dropped at the end automatically
    """

    @classmethod
    def setUpClass(cls):
        disconnect_all()
        cls._connection = connect(alias=MONGO_TEST_DB, host=MONGO_TEST_HOST)
        cls._connection.drop_database(MONGO_TEST_DB)
        cls.db = get_db(MONGO_TEST_DB)

    @classmethod
    def tearDownClass(cls):
        cls._connection.drop_database(MONGO_TEST_DB)
        disconnect_all()


def get_as_pymongo(doc):
    """Fetch the pymongo version of a certain Document"""
    return doc.__class__.objects.as_pymongo().get(id=doc.id)


class Decimal128Document(Document):
    meta = {
        'db_alias': MONGO_TEST_DB,
    }
    dec128_fld = Decimal128Field()
    dec128_min_0 = Decimal128Field(min_value=0)
    dec128_max_100 = Decimal128Field(max_value=100)


def generate_test_cls() -> Document:
    Decimal128Document.drop_collection()
    Decimal128Document(dec128_fld=None).save()
    Decimal128Document(dec128_fld=Decimal(1)).save()
    return Decimal128Document


class TestDecimal128Field(MongoDBTestCase):

    def test_decimal128_validation_good(self):
        """Ensure that invalid values cannot be assigned."""

        doc = Decimal128Document()

        doc.dec128_fld = Decimal(0)
        doc.validate()

        doc.dec128_fld = Decimal(50)
        doc.validate()

        doc.dec128_fld = Decimal(110)
        doc.validate()

        doc.dec128_fld = Decimal(110)
        doc.validate()

    def test_decimal128_validation_invalid(self):
        """Ensure that invalid values cannot be assigned."""

        doc = Decimal128Document()

        doc.dec128_fld = "ten"

        with pytest.raises(ValidationError):
            doc.validate()

    def test_decimal128_validation_min(self):
        """Ensure that out of bounds values cannot be assigned."""

        doc = Decimal128Document()

        doc.dec128_min_0 = Decimal(50)
        doc.validate()

        doc.dec128_min_0 = Decimal(-1)
        with pytest.raises(ValidationError):
            doc.validate()

    def test_decimal128_validation_max(self):
        """Ensure that out of bounds values cannot be assigned."""

        doc = Decimal128Document()

        doc.dec128_max_100 = Decimal(50)
        doc.validate()

        doc.dec128_max_100 = Decimal(101)
        with pytest.raises(ValidationError):
            doc.validate()

    def test_eq_operator(self):
        cls = generate_test_cls()
        assert 1 == cls.objects(dec128_fld=1.0).count()
        assert 0 == cls.objects(dec128_fld=2.0).count()

    def test_ne_operator(self):
        cls = generate_test_cls()
        assert 1 == cls.objects(dec128_fld__ne=None).count()
        assert 1 == cls.objects(dec128_fld__ne=1).count()
        assert 1 == cls.objects(dec128_fld__ne=1.0).count()

    def test_gt_operator(self):
        cls = generate_test_cls()
        assert 1 == cls.objects(dec128_fld__gt=0.5).count()

    def test_lt_operator(self):
        cls = generate_test_cls()
        assert 1 == cls.objects(dec128_fld__lt=1.5).count()

    def test_storage(self):
        # from int
        model = Decimal128Document(dec128_fld=100).save()
        assert get_as_pymongo(model) == {
            "_id": model.id,
            "dec128_fld": Decimal128("100"),
        }

        # from float
        model = Decimal128Document(dec128_fld=100.0).save()
        assert get_as_pymongo(model) == {
            "_id": model.id,
            "dec128_fld": Decimal128("100"),
        }

        # from Decimal
        model = Decimal128Document(dec128_fld=Decimal(100)).save()
        assert get_as_pymongo(model) == {
            "_id": model.id,
            "dec128_fld": Decimal128("100"),
        }

        # from Decimal128
        model = Decimal128Document(dec128_fld=Decimal128("100")).save()
        assert get_as_pymongo(model) == {
            "_id": model.id,
            "dec128_fld": Decimal128("100"),
        }

    def test_json(self):
        Decimal128Document.drop_collection()
        f = str(random.random())
        Decimal128Document(dec128_fld=f).save()
        json_str = Decimal128Document.objects.to_json()
        array = json.loads(json_str)
        assert array[0]["dec128_fld"] == {"$numberDecimal": str(f)}

    def test_decimal128_precision(self):
        Decimal128Document.drop_collection()
        model = Decimal128Document(dec128_fld=Decimal("5.9")).save()
        assert model.dec128_fld == Decimal("5.9") == Decimal128("5.9").to_decimal()
        assert Decimal128Document.objects().sum('dec128_fld') == Decimal128("5.9")

    def test_sum_decimal128(self):
        Decimal128Document.drop_collection()
        total = Decimal(0)
        for i in range(1000):
            rd = Decimal(str(random.randint(100000, 200000) / 1000))
            total += rd
            Decimal128Document(dec128_fld=rd).save()
        assert Decimal128Document.objects().sum('dec128_fld').to_decimal() == total
