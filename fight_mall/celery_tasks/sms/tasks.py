from fight_mall.libs.yuntongxun.sms import CCP
from celery_tasks.main import app
from fight_mall.utils.exceptions import logger


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, '5'], 1)
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, '5'], 1)
    # except Exception as e:
    #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    # else:
    #     if result == 0:
    #         logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
    #     else:
    #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)

