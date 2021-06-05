from graphene_mongo import MongoengineObjectType

from ..models.icpdao.job import Job, JobPR
from ..models.icpdao.user import User as UserModel
from ..models.icpdao.dao import DAO as DAOModel, \
    DAOJobConfig as DAOJobConfigModel, DAOFollow


class UserSchema(MongoengineObjectType):
    class Meta:
        model = UserModel


class DAOSchema(MongoengineObjectType):
    class Meta:
        model = DAOModel


class DAOJobConfigSchema(MongoengineObjectType):
    class Meta:
        model = DAOJobConfigModel
        filter_fields = {
            'dao_id': ['exact']
        }


class DAOFollowSchema(MongoengineObjectType):
    class Meta:
        model = DAOFollow


class JobSchema(MongoengineObjectType):
    class Meta:
        model = Job


class JobPRSchema(MongoengineObjectType):
    class Meta:
        model = JobPR
