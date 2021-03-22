from flask import Blueprint

# 1.创建用户蓝图对象
profile_blue = Blueprint("profile", __name__, url_prefix="/user")

# 2.装饰视图函数
from . import views
