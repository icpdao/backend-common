from graphene_mongo import MongoengineObjectType

from ..models.icpdao.job import Job, JobPR
from ..models.icpdao.user import User as UserModel
from ..models.icpdao.dao import DAO as DAOModel, \
    DAOJobConfig as DAOJobConfigModel, DAOFollow
from ..models.icpdao.cycle import Cycle, CycleIcpperStat, CycleVote
from ..utils.route_helper import get_custom_attr_by_graphql, get_current_user_by_graphql


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


class CycleSchema(MongoengineObjectType):
    class Meta:
        model = Cycle


class CycleIcpperStatSchema(MongoengineObjectType):
    class Meta:
        model = CycleIcpperStat

    def resolve_vote_ei(self, info):
        dao_owner_id = get_custom_attr_by_graphql(info, 'dao_owner_id')
        current_user = get_current_user_by_graphql(info)
        if not current_user:
            raise PermissionError('NOT LOGIN')
        if str(current_user.id) != dao_owner_id:
            raise PermissionError('NO ROLE')

        return self.vote_ei

    def resolve_owner_ei(self, info):
        dao_owner_id = get_custom_attr_by_graphql(info, 'dao_owner_id')
        current_user = get_current_user_by_graphql(info)
        if not current_user:
            raise PermissionError('NOT LOGIN')
        if str(current_user.id) != dao_owner_id:
            raise PermissionError('NO ROLE')

        return self.owner_ei


class CycleVoteSchema(MongoengineObjectType):
    class Meta:
        model = CycleVote
