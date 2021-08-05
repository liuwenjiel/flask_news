from info import redis_store
# from info.modules.index import index_blue
from . import index_blue
import logging
from flask import current_app, render_template, session, jsonify, request, g

from info.models import User, News, Category
from info.utils.response_code import RET
from info.utils.commons import user_login_data

import random


@index_blue.route('/', methods=['GET', "POST"])
@user_login_data
def show_index():
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

    # # 1. 获取用户的登录信息
    # user_id = session.get("user_id")
    #
    # # 2. 通过user_id取出用户登录对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 3. 查询热门新闻，根据点击量，查询前十条新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4. 将新闻对象列表转成字典列表
    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 5. 查询所有的分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取分类失败")

    # 6. 将分类的对象列表转成对象列表
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 5. 拼接用户数据，渲染页面
    data = {
        "user_info": g.user.to_dict() if g.user else "",
        "news_list": news_list,
        "category_list": category_list
    }

    return render_template("news/index.html", data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon_new.ico')


# 首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid, page, per_page
# 返回值: data数据
@index_blue.route('/newslist')
def newslist():
    """
    1. 获取参数
    2. 参数类型转换
    3. 分页查询
    4. 获取到分页对象中的属性，总页数，当前页，当前页的对象列表
    5. 将对象列表转成字典列表
    6. 携带数据，返回响应
    :return:
    """
    # 1. 获取参数
    cid = request.args.get("cid")
    page = request.args.get("page")
    per_page = request.args.get("per_page")
    # 2. 参数类型转换
    try:
        page = int(page)
        pre_page = int(per_page)
    except Exception as e:
        page = 1
        pre_page = 10

    # 3. 分页查询
    try:
        filters = [News.status == 0]
        # 判断新闻的分类是否为1
        if cid != "1":
            filters.append(News.category_id == cid)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, pre_page, False)

        if cid == "11":
            print("*****")
            from recommender.kernel import create_user_to_news_list
            paginate = create_user_to_news_list()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4. 获取到分页对象中的属性，总页数，当前页，当前页的对象列表
    if cid != "11":
        totalPage = paginate.pages
        currentPage = paginate.page
        items = paginate.items
    else:
        totalPage = 1
        currentPage = 1
        items = paginate

    # 5. 将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6. 携带数据，返回响应
    return jsonify(errno=RET.OK, errmsg="获取新闻成功",
                   totalPage=totalPage, currentPage=currentPage, newsList=news_list)


# 统一的返回404页面
@index_blue.route('/404')
@user_login_data
def page_not_found():
    data = {
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template("news/404.html", data=data)
