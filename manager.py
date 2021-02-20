"""
相关配置
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from info import create_app

# 调用方法，获取app
app = create_app("develop")


@app.route('/', methods=['GET', "POST"])
def hello_world():
    # # 测试redis存数据
    # redis_store.set('name', 'laowang')
    # print(redis_store.get('name'))
    #
    # # 测试session存取
    # session['name'] = 'zhangsan'
    # print(session.get('name'))

    return 'hello world'


if __name__ == '__main__':
    app.run()
