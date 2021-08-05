import numpy as np
import re
import jieba.analyse
from info.models import User, News, Category
import recommender.config
from flask import current_app, render_template, session, jsonify, request, g
import random
from info import redis_store, constants, db
import copy


def bit_product_sum(x, y):
    return sum([item[0] * item[1] for item in zip(x, y)])


def cosine_similarity(x, y, norm=False):
    """ 计算两个向量x和y的余弦相似度 """
    assert len(x) == len(y), "len(x) != len(y)"
    zero_list = [0] * len(x)
    if x == zero_list or y == zero_list:
        return float(1) if x == y else float(0)

    # method 1
    res = np.array([[x[i] * y[i], x[i] * x[i], y[i] * y[i]] for i in range(len(x))])
    cos = sum(res[:, 0]) / (np.sqrt(sum(res[:, 1])) * np.sqrt(sum(res[:, 2])))

    # method 2
    # cos = bit_product_sum(x, y) / (np.sqrt(bit_product_sum(x, x)) * np.sqrt(bit_product_sum(y, y)))

    # method 3
    # dot_product, square_sum_x, square_sum_y = 0, 0, 0
    # for i in range(len(x)):
    #     dot_product += x[i] * y[i]
    #     square_sum_x += x[i] * x[i]
    #     square_sum_y += y[i] * y[i]
    # cos = dot_product / (np.sqrt(square_sum_x) * np.sqrt(square_sum_y))

    return 0.5 * cos + 0.5 if norm else cos  # 归一化到[0, 1]区间内


def transformation_matrix(x, y):
    matrix_1 = []
    matrix_2 = []
    all = set(list(x.keys()) + list(y.keys()))
    for i in all:
        if x.get(i):
            matrix_1.append(x[i])
        else:
            matrix_1.append(0)
        if y.get(i):
            matrix_2.append(y[i])
        else:
            matrix_2.append(0)
    return matrix_1, matrix_2


def similarity(x, y):
    a, b = transformation_matrix(x, y)
    return cosine_similarity(a, b)


def get_category_dict():
    categories = Category.query.all()
    category_dict = {}
    for category in categories:
        if category.id != 1 and category.id != 11:
            category_dict[category.id] = category.name
    return category_dict


def add_news_label(item, category_dict):
    pattern = re.compile(r'<[^>]+>', re.S)
    result = pattern.sub('', item.content)
    temp = {x: w for x, w in jieba.analyse.extract_tags(result, topK=20, withWeight=True)}
    temp[category_dict[int(item.category_id)]] = temp.get(category_dict[int(item.category_id)], 0.0) + recommender.config.INIT_CATEGORY_WEIGHT
    item.news_label = temp


def init_news_label(news):
    category_dict = get_category_dict()
    for item in news:
        add_news_label(item, category_dict)
        # print(item.news_label, len(item.news_label))


def add_user_label(item, category_dict):
    temp = {}
    for category in category_dict:
        temp[category_dict[category]] = 1.0 / len(category_dict)
    item.user_label = temp


def init_user_label(users):
    category_dict = get_category_dict()
    for item in users:
        add_user_label(item, category_dict)
        # print(item.user_label)


def update_user_label(news, type, sign=1):
    # 1.从session中取出用户的user_id, 获取新闻标签
    user_id = session.get("user_id")
    if sign:
        item_label = news.news_label
    else:
        item_label = news.user_label

    print('label', item_label)

    # 2.通过user_id取出用户对象
    user = None
    if user_id:
        try:
            from info.models import User
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    else:
        return

    # 将用户浏览过的新闻添加到redis数据库
    if type == 'VIEW_NEWS':
        try:
            if redis_store.get("%s_%s" % (user.id, news.id)):
                return
            redis_store.set("%s_%s" % (user.id, news.id), 1, recommender.config.USER_NEWS_TIME_VALUE)
        except Exception as e:
            current_app.logger.error(e)

    weight = recommender.config.USER_BEHAVIOR_WEIGHT[type]
    u_label = copy.deepcopy(user.user_label)
    print(u_label)

    for i in item_label:
        u_label[i] = u_label.get(i, 0)
        if u_label[i] > 1: continue
        u_label[i] = max(0, (u_label[i] + item_label[i] * weight * recommender.config.WEIGHT_CONTROL))

    u_label_len = len(u_label)
    if u_label_len > 200:
        u_items = list[u_label.items()]
        u_items.sort(key=lambda x: x[1])
        for _ in range(u_label_len - 200):
            del u_label[u_items[0]]

    # 用户兴趣随时间减弱
    try:
        # print(redis_store.get("user_label_half:%s" % user.id))
        if not redis_store.get("user_label_half:%s" % user.id):
            for v in u_label:
                u_label[v] = u_label[v] / 2
            # print('----------------------')
            redis_store.set("user_label_half:%s" % user.id, 1, recommender.config.USER_LABEL_HALF_TIME)
    except Exception as e:
        current_app.logger.error(e)

    user.user_label = u_label
    print(user.user_label)


def create_user_to_news_list():
    # 1.从session中取出用户的user_id
    user_id = session.get("user_id")

    # 2.通过user_id取出用户对象
    user = None
    if user_id:
        try:
            from info.models import User
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            print("error")

    filters = [News.status == 0]
    news = News.query.filter(*filters).all()
    news_list = []
    if user is not None:
        print("user is not None")
        u_label = user.user_label
        for item in news:
            n_label = item.news_label
            similarity_value = similarity(u_label, n_label)
            if similarity_value > recommender.config.CRISIS_VALUE and (not redis_store.get("%s_%s" % (user.id, item.id))):
                news_list.append(item)
                item.similarity_value = similarity_value
        news_list.sort(key=lambda x: x.similarity_value, reverse=True)
        news_list = news_list[:20]
    else:
        print("user is None")
        for item in news:
            if random.random() > recommender.config.RANDOM_CRISIS_VALUE:
                news_list.append(item)
        news_list = news_list[:20]

    return news_list
