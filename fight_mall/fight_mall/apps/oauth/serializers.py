import re

from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.conf import settings
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    # 显示指明字段 不是模型类字段
    sms_code = serializers.CharField(max_length=6,min_length=6,write_only=True)
    access_token = serializers.CharField(write_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('password','mobile','sms_code','access_token',
                  'username','token')
        read_only_fields = ('username',)
        extra_kwargs = {
            'mobile': {
                'min_length': 11,
                'max_length': 11,
                'error_messages': {
                    'min_length': '手机号过短',
                    'max_length': '手机号过长',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # def validate_mobile(self, value):
    #     """验证手机号"""
    #     if not re.match(r'^1[3-9]\d{9}$', value):
    #         raise serializers.ValidationError('手机号格式不正确')
    #     return value

    def validate(self,attrs):

        # access_token验证
        # 解密access_token
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('错误的access_token')
        openid = data.get('openid')
        # attrs添加额外属性　方便保存数据时进行提取
        attrs['openid'] = openid
        # 验证短信
        # 1.建立连接
        conn = get_redis_connection('verify')
        # 2.获取数据
        real_sms_code = conn.get('sms_%s' % attrs['mobile'])
        # print(real_sms_code)
        # 3.判断数据是否超过有效期
        if not real_sms_code:
            raise serializers.ValidationError('短信失效')
        # 4.转换数据
        real_sms_code = real_sms_code.decode()
        # 5.比对验证
        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('短信错误')

        # 验证用户
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            return attrs
        else:
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
            return attrs

    def create(self, validated_data):
        # 获取user数据判断用户是否注册
        user = validated_data.get('user',None)
        if user is None:
            # 说明用户未注册
            user = User.objects.create_user(username=validated_data['mobile'],password=validated_data['password'],
                                     mobile=validated_data['mobile'])
        # 用户注册过,进行绑定
        OAuthQQUser.objects.create(user=user,openid=validated_data['openid'])
        # 生成jwttoken
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 对user对象添加token属性字段
        user.token = token
        return user
