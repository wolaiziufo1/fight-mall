from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView,CreateAPIView
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from oauth.models import OAuthQQUser
from oauth.serializers import QQAuthUserSerializer

# Create your views here.


class QQAuthURLView(APIView):
    def get(self, request):
        # 获取前段state数据
        state = request.query_params.get('state', None)
        if state is None:
            state = '/'

        # 初始化生成qq对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        # 获取跳转连接
        qq_login_url = oauth.get_qq_url()
        # 返回跳转连接给前端
        return Response({'login_url': qq_login_url})


class QQAuthUserView(CreateAPIView):
    serializer_class = QQAuthUserSerializer
    def get(self, request):
        # 获取code值
        code = request.query_params.get('code', None)
        # 判断code值是否存在
        if not code:
            return Response({'errors': '缺少code值'})
        # 通过code值获取access_token
        state = '/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        access_token = oauth.get_access_token(code)
        # 通过access_token值获取openid
        openid = oauth.get_open_id(access_token)
        # 判断openid是否绑定美多用户对象
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:
            # openid 未绑定用户
            tjs = TJS(settings.SECRET_KEY, 300)
            open_id = tjs.dumps({'openid': openid}).decode()
            return Response({'access_token': open_id})
        else:
            # 已经绑定用户
            # 登陆成功
            # 获取用户对象
            user = qq_user.user
            print(user)
            print(user.username)
            # 生成jwt token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response(
                {
                    'token': token,
                    'user_id': user.id,
                    'username': user.username
                }
            )
