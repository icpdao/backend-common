from ..icpdao.user import User, UserStatus
from ..icpdao.icppership import Icppership


def pre_icpper_to_icpper(user_id):
    user = User.objects(id=user_id).first()
    if user.status == UserStatus.PRE_ICPPER.value:
        user.update_to_icpper()
        user_is = Icppership.objects(icpper_user_id=str(user_id)).first()
        user_is.update_to_icpper()
