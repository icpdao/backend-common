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
            return None
        if str(current_user.id) != dao_owner_id:
            return None

        return self.vote_ei

    def resolve_owner_ei(self, info):
        dao_owner_id = get_custom_attr_by_graphql(info, 'dao_owner_id')
        current_user = get_current_user_by_graphql(info)
        if not current_user:
            return None
        if str(current_user.id) != dao_owner_id:
            return None

        return self.owner_ei


class CycleVoteSchema(MongoengineObjectType):
    class Meta:
        model = CycleVote
        exclude_fields = ['vote_result_type_all']

    @staticmethod
    def have_view_vote_job_id_role(info, cycle_vote):
        if cycle_vote.is_result_public:
            return True

        current_user = get_current_user_by_graphql(info)
        if current_user and cycle_vote.voter_id and cycle_vote.voter_id == str(current_user.id):
            return True

        return False

    @staticmethod
    def have_view_voter_id_role(info, cycle_vote):
        if cycle_vote.is_result_public:
            return True

        dao_owner_id = get_custom_attr_by_graphql(info, 'dao_owner_id')
        current_user = get_current_user_by_graphql(info)
        if current_user and dao_owner_id == str(current_user.id):
            return True

        if current_user and cycle_vote.voter_id and cycle_vote.voter_id == str(current_user.id):
            return True

        return False

    def resolve_vote_job_id(self, info):
        if CycleVoteSchema.have_view_vote_job_id_role(info, self):
            return self.vote_job_id
        return None

    def resolve_voter_id(self, info):
        if CycleVoteSchema.have_view_voter_id_role(info, self):
            return self.voter_id
        return None
