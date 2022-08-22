# 配置
import redis
import time


class Config():
    """
    配置文件基类
    """
    SECERT_KEY = 'CODEHAMAL'  # 数据库名称
    # 数据库连接
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost:3306/test?charset=utf8'
    # SQLALCHEMY_BINDS = {
    #     'server': 'mysql://root:123456@localhost:3306/test',
    # }
    # 打开数据库语句自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_SIZE = 50

    JWT_SECRET = 'code_hamal'  # jwt密钥
    JWT_EXPIRY = time.time() + 60 * 60 * 24 * 7  # jwt过期时间

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # # session配置，使用redis
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # SESSION_USE_SIGNER = True  # 对cookie进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400  # 设置有效期 单位秒

    # app_id
    APP_ID = ""


class DevelopmentConfig(Config):
    """开发环境"""
    DEBUG = True


class ProductCofnig(Config):
    pass


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductCofnig
}
