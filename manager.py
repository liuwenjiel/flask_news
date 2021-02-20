"""
相关配置
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from info import create_app, db, models  # 导入models的作用是让应用程序知道有这个东西的存在
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 调用方法，获取app
app = create_app("develop")

# 创建manager对象，管理app
manager = Manager(app)

# 使用Migrate关联app，db
Migrate(app, db)

# 给manager添加一条操作命令
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()
