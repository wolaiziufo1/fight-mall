from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response


# Create your views here.
class QQAuthURLView(APIView):
    def get(self, request):
        # 获取前段state数据
        state = request.query_params.get('state',None)
        if state is None:
            state = '/'

        # 初始化生成qq对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        # 获取跳转连接
        qq_login_url = oauth.get_qq_url()
        # 返回跳转连接给前端
        return Response({'login_url':qq_login_url})
