from flask import current_app, jsonify, render_template, abort, session
from info.models import News, User
from info.utils.response_code import RET

from . import news_blue


# 请求路径：/news/<int:news_id>
# 请求方式：GET
# 请求参数：new_id
# 返回值：detail.html页面，用户data字典数据
@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    # 0.从session中取出用户的user_id
    user_id = session.get("user_id")

    # 0.1通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 1.根据新闻编号，查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 2.如果新闻对象不存在直接抛出异常
    if not news:
        abort(404)

    # 3.获取前6条热门新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 4.将热门新闻的对象列表转成字典列表
    click_news_list = []
    for item_news in click_news:
        click_news_list.append(item_news.to_dict())

    # 5.携带数据，渲染页面
    data = {
        "news_info": news.to_dict(),
        "user_info": user.to_dict() if user else "",
        "news_list": click_news_list
    }

    return render_template("news/detail.html", data=data)
