from django.db import models
from fight_mall.utils.models import BaseModel


# Create your models here.
class OAuthQQUser(BaseModel):
    """
    QQ登陆用户数据
    """
    user = models.ForeignKey('users.User',on_delete=models.CASCADE,
                             verbose_name='用户')
    openid = models.CharField(max_length=64,verbose_name='openid',db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登陆用户数据'
        verbose_name_plural = verbose_name