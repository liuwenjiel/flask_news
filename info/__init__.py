from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from config import config_dict


# 定义工厂方法
def create_app(config_name):
    app = Flask(__name__)

    # 根据传入的配置类名称取出相应的配置类
    config = config_dict.get(config_name)

    # 加载配置类
    app.config.from_object(config)

    # 创建SQLAlchemy对象，关联app
    db = SQLAlchemy(app)

    # 创建redis对象
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 创建Session对象，读取App中session配置信息
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    return app
