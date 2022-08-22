from flask import Flask
from config import config_map
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
from app.utils.tools import ReConverter
from flask_migrate import Migrate
# from flask_admin import Admin


db = SQLAlchemy()  # 定义数据库
migrate = Migrate()
# admin = Admin(name='后台管理', template_mode='bootstrap3')


def create_app(config_name='develop'):
    app = Flask(__name__, template_folder='templates')
    # app.secret_key='shjx'
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)  # 导入配置对象类
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/test?charset=utf8'

    app.config['JSON_AS_ASCII'] = False  # 支持中文

    # 补充csrf保护机制
    # CSRFProtect(app)
    CORS(app, supports_credentials=True)

    # 利用 flask_session 将session保存再redis中
    Session(app)

    # 为flask添加自定义的转换器
    app.url_map.converters['re'] = ReConverter

    db.init_app(app)
    Migrate(app, db)
    # admin.init_app(app)

    from app.admin.controller import admin
    app.register_blueprint(admin)

    # 配置404页面
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title='Page Not Found'), 404

    # 配置500页面
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', title='Server Error'), 500

    app.add_template_filter(do_listreverse, 'listreverse')

    # 用户蓝图
    from app.api.v1 import b_user
    app.register_blueprint(b_user, url_prefix='/user')

    return app


def do_listreverse(li):
    temp_li = list(li)
    temp_li.reverse()
    return temp_li
