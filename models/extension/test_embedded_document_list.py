from mongoengine import Document, StringField, EmbeddedDocumentListField, EmbeddedDocument, IntField

from .test_decimal128_field import MongoDBTestCase, MONGO_TEST_DB


class TestEmbeddedDocument(EmbeddedDocument):
    key = StringField()
    value = StringField()
    num = IntField()


class TestDocument(Document):
    meta = {
        'db_alias': MONGO_TEST_DB,
    }
    name = StringField()
    embedded_document_list = EmbeddedDocumentListField(TestEmbeddedDocument)


class TestEmbeddedDocumentListField(MongoDBTestCase):
    def test_storage(self):
        TestDocument.drop_collection()
        TestDocument(name="a", embedded_document_list=[
            TestEmbeddedDocument(key="a.1", value="a1", num=1),
            TestEmbeddedDocument(key="a.2", value="a2", num=2),
            TestEmbeddedDocument(key="a.3", value="a3", num=3),
        ]).save()

        assert TestDocument.objects().first().name == "a"
        assert len(TestDocument.objects().first().embedded_document_list) == 3

        assert TestDocument.objects(name="a").first().embedded_document_list.get(key="a.1").value == "a1"
        assert len(TestDocument.objects(name="a").first().embedded_document_list.filter(key="a.1")) == 1
        assert TestDocument.objects(name="a").first().embedded_document_list.filter(key="a.2").first().value == "a2"

        TestDocument(name="a", embedded_document_list=[
            TestEmbeddedDocument(key="a.1", value="a1", num=1),
            # TestEmbeddedDocument(key="a.2", value="a2", num=2),
            TestEmbeddedDocument(key="a.3", value="a3", num=3),
        ]).save()
        TestDocument(name="a", embedded_document_list=[
            TestEmbeddedDocument(key="a.1", value="a1", num=1),
            TestEmbeddedDocument(key="a.2", value="a2", num=2),
            # TestEmbeddedDocument(key="a.3", value="a3", num=3),
        ]).save()

        test_agg = TestDocument.objects(name="a", embedded_document_list__key="a.1").aggregate([
            {"$unwind": "$embedded_document_list"},
            {"$match": {"embedded_document_list.key": "a.1"}},
            {"$group": {"_id": "sum", "total": {"$sum": "$embedded_document_list.num"}}},
        ])
        assert tuple(test_agg)[0]['total'] == 3

        test_agg = TestDocument.objects(name="a", embedded_document_list__key="a.2").aggregate([
            {"$unwind": "$embedded_document_list"},
            {"$match": {"embedded_document_list.key": "a.2"}},
            {"$group": {"_id": "sum", "total": {"$sum": "$embedded_document_list.num"}}},
        ])
        assert tuple(test_agg)[0]['total'] == 4
