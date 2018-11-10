import re

from django.contrib.auth.backends import ModelBackend
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 判断username是否是手机号
            if re.match(r'^1[3-9]\d{9}$',username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)

        except:
            user = None
        if user is not None and user.check_password(password):
            return user