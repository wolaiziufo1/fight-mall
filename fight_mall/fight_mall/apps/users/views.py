from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from users.serializers import UserSerializer
from rest_framework.generics import RetrieveAPIView
from .serializers import UserDetailSerializer


# Create your views here.
# 判断用户名是否存在
class UserNameCountView(APIView):
    def get(self, request, username):
        # 查询用户数量
        count = User.objects.filter(username=username).count()
        return Response({
            'username': username,
            'count': count,
        })


# 判断手机号是否存在
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response({
            'mobile': mobile,
            'count': count,
        })


# 注册保存数据
class UserView(CreateAPIView):
    serializer_class = UserSerializer
    # 获取前段数据
    # 校验数据
    # 保存数据
    # 返回结果


class UserDetailView(RetrieveAPIView):

    serializer_class = UserDetailSerializer

    def get_object(self):
        # print(self.request.user)
        return self.request.user