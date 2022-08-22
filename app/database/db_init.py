# 初始化数据库
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from test_models import *
from sqlalchemy.exc import IntegrityError

# Gunicorn uWsgi
manager = Manager(app)
# 第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
migrate = Migrate(app, db)
# manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db', MigrateCommand)


def make_database():
    """重建数据库"""
    # 清除数据库里的所有数据
    db.drop_all()
    # 创建所有的表
    db.create_all(bind='server')


def add_table():
    """添加数据"""
    # 添加数据
    try:
        user = SystemUsers(account='admin', password='admin', name='admin')
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


if __name__ == '__main__':
    make_database()
    add_table()
