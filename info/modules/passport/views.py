import json
import re
from flask import request, current_app, make_response, jsonify
from . import passport_blue
from info.utils.captcha.captcha import captcha
from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP


# 功能：获取图片验证码
# 请求路径：/passport/image_code
# 请求方式：get
# 携带参数：cur_id, pre_id
# 返回值：图片
@passport_blue.route('/image_code')
def image_code():
    # 获取前端传递的参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    # 调用generate_captcha获取图片验证码编号，值，图片（二进制）
    _, text, image_data = captcha.generate_captcha()

    # 将图片验证码的值保存redis
    try:
        # 参数 key， value， 有效期
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

        # 判断是否有上一次的图片验证码
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return "获取图片验证码失败"

    # 返回图片
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/png"
    return response


# 获取短信验证码
# 请求路径：/passport/sms_code
# 请求方式：POST
# 请求参数：moblie, image_code, image_code_id
# 返回值：errno, errmsg
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    # 1.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2.校验参数，图片验证码
    # 从redis中取出图片验证码
    redis_image_code = redis_store.get("image_code:%s"%image_code_id)

    if image_code != redis_image_code:
        return jsonify(errno=10000, errmsg="图片验证码错误")

    # 3.校验参数，手机号格式
    if not re.match("1[3-9]\d{9}", mobile):
        return jsonify(errno=20000, errmsg="手机号格式错误")

    # 4.发送短信，调用封装好的cpp
    ccp = CCP()
    result = ccp.send_template_sms(mobile, ['1234', 5], 1)

    if result == -1:
        return jsonify(errno=30000, errmsg="短信发送失败")

    # 5.返回发送的状态
    return jsonify(errno=0, errmsg="短信发送成功")