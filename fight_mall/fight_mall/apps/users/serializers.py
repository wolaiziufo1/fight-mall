import re

from rest_framework import serializers
from users.models import User
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings


class UserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='登陆状态token',read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow','token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
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

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validate_allow(self, value):
        """验证同意协议"""
        if value != 'true':
            raise serializers.ValidationError('协议未同意')
        return value

    def validate(self, attrs):
        """密码验证"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证
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
        return attrs

    def create(self, validated_data):
        """保存"""
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = super().create(validated_data)
        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        # print(user)
        return user
