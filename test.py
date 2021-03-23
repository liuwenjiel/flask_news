"""
1. python中的三元运算
    "语句1" if 条件A else "语句2"
    执行特点:
        如果条件A为True, 那么返回语句1, 否则返回语句2


2. 使用g对象配合装饰器使用
    装饰器作用: 给已经存在的方法,添加额外的功能, 而不应该改变原有函数的结构
    解决办法: 不改变原有函数的结构,functools. wraps可以解决该问题

    如果不使用wraps修饰函数,那么报错
     View function mapping is overwriting an existing endpoint function: wrapper

"""
#1. python中的三元运算
"""
a = "hello" if False else "world"
print(a) #world

b = "hello" if "" else "world"
print(b)

c = "hello" if [] else "world"
print(c)

d = "hello" if None else "world"
print(d)

e = "hello" if [1,2,3] else "world"
print(e)
"""

from functools import wraps
from flask import Flask

haha = Flask(__name__)

#2.定义装饰器
def user_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        """wrapper..doc"""
        print("我是装饰器,给已经存在的函数添加了额外的功能")
        return view_func(*args,**kwargs)
    return wrapper


@haha.route("/index1")
@user_data
def test1():
    """test1..doc"""
    print("test1")

@haha.route("/index2")
@user_data
def test2():
    """test2..doc"""
    print("test2")

print(test1.__name__)
print(test1.__doc__)

print(test2.__name__)
print(test2.__doc__)


# test1()

#1.导入常见的时间类
import time
from datetime import datetime,timedelta,date

#2.将时间戳,格式化成为本地的时间(可以非常方便的表示,年,月,日,时分秒,今天是本周的第几天,今天是今年的第几天)
localtime = time.localtime()
# print(localtime.tm_year)
# print(localtime.tm_mday)
# print(localtime.tm_mday)

#3.datetime.now(), 获取本地系统的当前时间(可以非常方便的表示,年,月,日,时分秒)
now_time = datetime.now()

#4.timedelta(),时间跨度
days_time = timedelta(days=2)

#5.date(), 可以使用指定的时间来创建一个日期对象
date_time = date(2018,1,1)

#6.strptime作用,将时间的字符串,转成时间对象 (str-->时间对象)
month_start_time_str = "2017-11-11"
#参数1: 时间的字符串, 参数2: 表示格式化符号
month_start_time_date = datetime.strptime(month_start_time_str,"%Y-%m-%d")
print(month_start_time_date)

#7.strftime (时间对象-->str)
date_str = datetime.strftime(month_start_time_date,"%Y-%m-%d")
# begin_date.strftime("%Y-%m-%d")
print(date_str)
print(type(date_str))
