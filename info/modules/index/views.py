from info import redis_store
# from info.modules.index import index_blue
from . import index_blue
import logging
from flask import current_app, render_template, session, jsonify

from info.models import User, News
from info.utils.response_code import RET


@index_blue.route('/', methods=['GET', "POST"])
def hello_world():
    # 测试redis存数据,使用print不方便控制
    # redis_store.set('name', 'laowang')
    # print(redis_store.get('name'))

    # # 测试session存取
    # session['name'] = 'zhangsan'
    # print(session.get('name'))

    # 使用日志记录方法loggin进行输出可控
    # logging.debug("输入调试信息")
    # logging.info("输入详细信息")
    # logging.warning("输入警告信息")
    # logging.error("输入错误信息")

    # 也可以使用current_app来输出日志信息
    # current_app.logger.debug("输入调试信息")
    # current_app.logger.info("输入详细信息")
    # current_app.logger.warning("输入警告信息")
    # current_app.logger.error("输入错误信息")

    # 1. 获取用户的登录信息
    user_id = session.get("user_id")

    # 2. 通过user_id取出用户登录对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 3. 查询热门新闻，根据点击量，查询前十条新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 将新闻对象列表转成字典列表
    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 5. 拼接用户数据，渲染页面
    data = {
        "user_info": user.to_dict() if user else "",
        "news_list": news_list
    }

    return render_template("news/index.html", data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')
