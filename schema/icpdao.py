from graphene import List
from graphene_mongo import MongoengineObjectType

from .incomes import TokenIncomeSchema
from ..models.icpdao.job import Job, JobPR
from ..models.icpdao.token import TokenMintRecord
from ..models.icpdao.user import User as UserModel
from ..models.icpdao.dao import DAO as DAOModel, \
    DAOJobConfig as DAOJobConfigModel, DAOFollow, DAOToken
from ..models.icpdao.cycle import Cycle, CycleIcpperStat, CycleVote
from ..utils.route_helper import get_custom_attr_by_graphql, get_current_user_by_graphql

# 在 引入 graphene_mongo 以后，引入补丁，不要去掉，更不要改变循序
from ..models.extension.graphene_decimal128 import convert_field_to_float_1


class UserSchema(MongoengineObjectType):
    class Meta:
        model = UserModel


class DAOSchema(MongoengineObjectType):
    class Meta:
        model = DAOModel
        exclude_fields = ['token_chain_id', 'token_address', 'token_name', 'token_symbol']


class DAOTokenSchema(MongoengineObjectType):
    class Meta:
        model = DAOToken


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
    incomes = List(TokenIncomeSchema)

    class Meta:
        model = Job
        exclude_fields = ['incomes', 'income']

    def resolve_incomes(self, info):
        return [TokenIncomeSchema(
            token_chain_id=income.token_chain_id,
            token_address=income.token_address,
            token_symbol=income.token_symbol,
            income=income.income
        ) for income in self.incomes]


class JobPRSchema(MongoengineObjectType):
    class Meta:
        model = JobPR


class CycleSchema(MongoengineObjectType):
    class Meta:
        model = Cycle
        exclude_fields = ['token_released_at']


class CycleIcpperStatSchema(MongoengineObjectType):
    incomes = List(TokenIncomeSchema)

    class Meta:
        model = CycleIcpperStat
        exclude_fields = ['incomes', 'income']

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

    def resolve_incomes(self, info):
        return [TokenIncomeSchema(
            token_chain_id=income.token_chain_id,
            token_address=income.token_address,
            token_symbol=income.token_symbol,
            income=income.income
        ) for income in self.incomes]


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

        dao_owner_id = DAOModel.objects(id=cycle_vote.dao_id).first().owner_id
        if cycle_vote.is_repeat is True and dao_owner_id == str(current_user.id):
            return True

        return False

    @staticmethod
    def have_view_voter_id_role(info, cycle_vote):
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


class TokenMintRecordSchema(MongoengineObjectType):
    class Meta:
        model = TokenMintRecord
