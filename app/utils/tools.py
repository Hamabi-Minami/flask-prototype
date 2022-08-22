# 工具类
from flask.globals import request
import jwt
import functools
from sqlalchemy.orm import class_mapper
from flask import current_app, make_response, jsonify, session, g
import random, string
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from werkzeug.routing import BaseConverter

import redis
from config import Config

r = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=1)


# 定义正则转换器
class ReConverter(BaseConverter):
    """获取get中url任意正则的转换器"""

    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(BaseConverter, self).__init__()
        # 保存正则表达式
        self.regex = regex


# 封装各项工具
class Tools:
    # 数据库结果重组
    # orm 数据序列化
    # jwt生成
    # jwt解析
    # 哈希密码生成
    # 哈希密码解析

    #  sql 格式化结果集
    def dictfetch(desc):
        # 重组结果
        return [dict(row) for row in desc]

    # orm 数据序列化
    def serialize(model):
        if type(model) == list:
            datalist = []
            for m in model:
                columns = [c.key for c in class_mapper(m.__class__).columns]
                data = dict((c, getattr(m, c)) for c in columns)
                datalist.append(data)
            return datalist
        else:
            columns = [c.key for c in class_mapper(model.__class__).columns]
            return dict((c, getattr(model, c)) for c in columns)


class imageCode():
    '''
    验证码处理
    '''

    def rndColor(self):
        '''随机颜色'''
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    def geneText(self):
        '''生成4位验证码'''
        return ''.join(random.sample(string.ascii_letters + string.digits, 4))  # ascii_letters是生成所有字母 digits是生成所有数字0-9

    def drawLines(self, draw, num, width, height):
        '''划线'''
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    def getVerifyCode(self):
        '''生成验证码图形'''
        code = self.geneText()
        # 图片大小120×50
        width, height = 120, 50
        # 新图片对象
        im = Image.new('RGB', (width, height), 'white')
        # 字体
        font = ImageFont.truetype('app/static/arial.ttf', 40)
        # draw对象
        draw = ImageDraw.Draw(im)
        # 绘制字符串
        for item in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * item, 5 + random.randint(-3, 3)),
                      text=code[item], fill=self.rndColor(), font=font)
        # 划线
        self.drawLines(draw, 2, width, height)
        return im, code

    def getImgCode(self):
        image, code = self.getVerifyCode()
        # 图片以二进制形式写入
        buf = BytesIO()
        image.save(buf, 'jpeg')
        buf_str = buf.getvalue()
        # 把buf_str作为response返回前端，并设置首部字段
        response = make_response(buf_str)
        response.headers['Content-Type'] = 'image/gif'
        # 将验证码字符串储存在session中
        session['imageCode'] = code
        return response


# 生成token
def generate_token(payload):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期
    :param secret: 密钥
    :return: jwt
    """
    secret = current_app.config['JWT_SECRET']
    expiry = current_app.config['JWT_EXPIRY']
    _payload = {'exp': expiry}
    _payload.update(payload)

    token = jwt.encode(_payload, secret, algorithm='HS256')
    return token.decode()


# 解析token
def verify_token(token):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload, err
    """
    secret = current_app.config['JWT_SECRET']
    try:
        err = None
        payload = jwt.decode(token, secret, algorithm=['HS256'])
    except jwt.ExpiredSignatureError as e1:
        payload = None
        err = {'code': 20001, 'msg': '签名过期', 'err': e1.args}
    except jwt.DecodeError as e2:
        payload = None
        err = {'code': 20002, 'msg': '签名解析错误', 'err': e2.args}
    return payload, err


# 接口访问次数统计
def request_counter(view_func):
    def wrapper(*args, **kwargs):
        user_ip = request.remote_addr
        r.incr(user_ip, amount=1)

        print(f'用户{user_ip}访问次数:', r.get(user_ip).decode())

        return view_func(*args, **kwargs)

    return wrapper


# 接口访问次数限制,可以限制ip一分钟内多次请求,如上传大文件等
def request_filter(view_func):
    def wrapper(*args, **kwargs):

        user_ip = request.remote_addr
        query_times = redis.Redis.get(r, user_ip)
        if not query_times:
            redis.Redis.incr(r, user_ip, amount=1)  # 自增操作
            redis.Redis.expire(r, user_ip, 60 * 1)  # 设置过期时间
        elif int(query_times) > 5:
            return jsonify({'code': 4003, 'msg': '访问次数过多,请一分钟后再试'})
        else:
            redis.Redis.incr(r, user_ip)
        return view_func(*args, **kwargs)

    return wrapper


# 登录验证,通过解析jwt
def login_required(view_func):
    from app.database.models import SystemUsers
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        token = request.headers.get('token', None)
        payload, err = verify_token(token)
        if err != None:
            return make_response(jsonify(err))
        account = payload['account']
        try:
            user_info = SystemUsers.query.filter_by(account=account).first()
        except:
            return jsonify({'code': 20000, 'msg': '签名信息有误'})
        else:
            user_id = user_info.id
        if user_id:
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，则返回错误码
            return jsonify(errno='403', errmsg='用户未登录')

    return wrapper


# 权限装饰器,如果不具有管理员权限,直接返回403
def permission(names):
    def power_auth(view_func):
        from app.database.models import UserRoles, RolePermissions
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):

            user_id = session.get('uid')
            try:
                ur = UserRoles.query.filter_by(user_id=user_id).first()
                rps = RolePermissions.query.filter_by(role_id=ur.role_id).all()
                pnames = [rp.permission.name for rp in rps]
            except Exception as e:
                return jsonify(errno='403', errmsg='非法用户,err:{}'.format(e.args))
            else:
                if set(pnames).issubset(set(names)):
                    return view_func(*args, **kwargs)
                else:
                    return jsonify(errno='403', errmsg='此用户未或得此权限')

        return wrapper

    return power_auth
