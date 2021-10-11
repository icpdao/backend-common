import time

from ..icpdao.dao import DAOFollow
from ..icpdao.user import User, UserStatus
from ..icpdao.icppership import Icppership, IcppershipProgress, IcppershipStatus
from ..icpdao.user_github_token import UserGithubToken
from ...utils.github_rest_api import refresh_github_access_token


def icppership_accept(icppership, user):
    if icppership.progress != IcppershipProgress.PENDING.value:
        return

    if user.status == UserStatus.NORMAL.value:
        user.status = UserStatus.PRE_ICPPER.value
        user.save()

    icppership.progress = IcppershipProgress.ACCEPT.value
    icppership.icpper_user_id = str(user.id)
    icppership.status = user.status
    icppership.accept_at = int(time.time())
    icppership.save()


def icppership_cancle_accept(icppership):
    if icppership.progress != IcppershipProgress.ACCEPT.value:
        return

    user = User.objects(id=icppership.icpper_user_id).first()
    if user.status == UserStatus.PRE_ICPPER.value:
        user.status = UserStatus.NORMAL.value
        user.save()

    icppership.progress = IcppershipProgress.PENDING.value
    icppership.icpper_user_id = None
    icppership.status = user.status
    icppership.accept_at = None
    icppership.save()


def pre_icpper_to_icpper(user_id):
    user_is = Icppership.objects(
        icpper_user_id=str(user_id),
        status=IcppershipStatus.PRE_ICPPER.value,
        progress=IcppershipProgress.ACCEPT.value
    ).first()
    if user_is:
        user = User.objects(id=user_id).first()
        user.status = UserStatus.ICPPER.value
        user.save()

        user_is.status = IcppershipStatus.ICPPER.value
        user_is.icpper_at = int(time.time())
        user_is.save()


def user_auth_follow_dao(user_id, dao_id):
    df = DAOFollow.objects(user_id=user_id, dao_id=dao_id).first()
    if not df:
        DAOFollow(user_id=user_id, dao_id=dao_id).save()


def check_user_access_token(user, client_id, client_secret):
    ugt = UserGithubToken.objects(github_user_id=user.github_user_id).first()
    expires_at = ugt.token_at + ugt.expires_in
    if expires_at > int(time.time()) + 60 * 60:
        return

    refresh_token_expires_at = ugt.token_at + ugt.refresh_token_expires_in
    if refresh_token_expires_at < int(time.time()):
        return

    try:
        access_token_info = refresh_github_access_token(client_id, client_secret, ugt.refresh_token)
        if access_token_info.get("access_token"):
            ugt.access_token = access_token_info["access_token"]
            ugt.refresh_token = access_token_info["refresh_token"]
            ugt.expires_in = access_token_info["expires_in"]
            ugt.refresh_token_expires_in = access_token_info["refresh_token_expires_in"]
            ugt.token_at = access_token_info["token_at"]
            ugt.save()
    except Exception as ex:
        import traceback
        msg = traceback.format_exc()
        print('exception log_exception' + str(ex))
        print(msg)
