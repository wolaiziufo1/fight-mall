from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from fight_mall.libs.yuntongxun.sms import CCP
from rest_framework.response import Response


# Create your views here.
class SMSCodeView(APIView):
    def get(self, request, mobile):
        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        conn = get_redis_connection('verify')
        # 判断60秒
        flag = conn.get('sms_flag_%s' % mobile)
        if flag:
            return Response({'message': '请求过于频繁'})
        print(sms_code)
        # 保存短信验证码
        conn.setex('sms_%s' % mobile, 300, sms_code)
        conn.setex('sms_flag_%s' % mobile, 60, 1)
        # 发送短信验证码
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, '5'], 1)

        # 返回结果
        return Response({'message': 'ok'})
