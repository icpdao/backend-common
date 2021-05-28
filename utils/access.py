from app.common.models.icpdao.dao import DAO
from app.common.models.icpdao.user import UserStatus


def is_dao_owner(user, dao_id=None, dao=None):
    if dao_id:
        dao = DAO.objects(id=dao_id).first()
    if not dao or not user:
        return False, ValueError('NOT FOUND USER OR DAO')
    if dao.owner_id != str(user.id):
        return False, PermissionError('NOT RIGHT OWNER ACCESS')
    return True, None


def check_is_dao_owner(user, dao_id=None, dao=None):
    judge, err = is_dao_owner(user, dao_id, dao)
    if judge:
        return True
    raise err


def check_is_not_dao_owner(user, dao_id=None, dao=None):
    judge, err = is_dao_owner(user, dao_id, dao)
    if not judge:
        return True
    raise PermissionError('NOT RIGHT NOT OWNER ACCESS')


def check_is_icpper(user):
    if not user:
        raise ValueError('NOT FOUND DAO')
    if user.status != UserStatus.ICPPER.value:
        raise PermissionError('NOT RIGHT ICPPER ACCESS')
    return True
