"""
相关配置
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from config import Config

app = Flask(__name__)

# 加载配置类
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