"""
相关配置
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from datetime import timedelta

from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect

app = Flask(__name__)


# 设置配置信息
class Config(object):
    # 调试信息
    DEBUG = True
    SECRET_KEY = "gdksjhfksdhfl"

    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/info"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # session配置信息
    SESSION_TYPE = 'redis'  # 设置session存储类型
    SQLALCHEMY_BINDS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True  # 设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)  # 设置session的有效期


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# 创建Session对象，读取App中session配置信息
Session(app)

# 使用CSRFProtect保护app
CSRFProtect(app)


@app.route('/', methods=['GET', "POST"])
def hello_world():
    # 测试redis存数据
    redis_store.set('name', 'laowang')
    print(redis_store.get('name'))

    # 测试session存取
    session['name'] = 'zhangsan'
    print(session.get('name'))

    return 'hello world'


if __name__ == '__main__':
    app.run()
