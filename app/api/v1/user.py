# 用于用户密码加密与解密
from sqlalchemy.orm.base import EXT_CONTINUE
from werkzeug.security import generate_password_hash
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from flask import session
from flask.views import MethodView

from . import b_user
from app.database.models import *
from app.utils.tools import Tools as tl, generate_token, login_required, verify_token, request_counter, request_filter, \
    imageCode as ic


class SysUser(MethodView):
    """
    系统用户视图
    """

    # 系统用户登录
    # @request_counter # 登录访问统计,按需要添加
    # @request_filter # 登录访问次数限制
    def get(self):
        token = request.headers.get('token', None)
        account = request.args.get('account', None)
        password = request.args.get('password', None)

        if token and (account == None or password == None):
            try:
                payload, err = verify_token(token)
                if err != None:
                    return make_response(jsonify(err))
                account = payload['account']
                password = payload['password']
                try:
                    user_info = SystemUsers.query.filter_by(account=account).first()
                    user_info = tl.serialize(user_info)
                except:
                    return jsonify({'code': 20002, 'msg': '签名信息有误,不存在此用户'})
                if password == user_info['password']:
                    resp = make_response(jsonify({
                        'code': 200,
                        'msg': '登录成功',
                        'user_info': user_info,
                        'token': token,
                    }))
                    resp.set_cookie('id', str(user_info['id']))
                    session['uid'] = user_info['id']
                    return resp
                else:
                    return jsonify({'code': 20002, 'msg': '签名信息有误,密码验证未通过'})
            except Exception as e:
                return jsonify({'code': 20000, 'msg': '签名解析异常', 'err': e.args})
        else:
            try:
                user_info = SystemUsers.query.filter_by(account=account, flag=True).first()
                user_info = tl.serialize(user_info)
            except Exception as e:
                return jsonify({'code': 400, 'msg': '用户名不存在', 'err': e.args})
            if password == user_info['password']:
                payload = {
                    'account': user_info['account'],
                    'password': user_info['password'],
                    'user_id': str(user_info['id'])
                }
                token = generate_token(payload)
                resp = make_response(jsonify({
                    'code': 200,
                    'msg': '登录成功',
                    'user_info': user_info,
                    'token': token,
                }))
                resp.set_cookie('id', str(user_info['id']))
                session['uid'] = user_info['id']
                return resp
            else:
                return jsonify({'code': 400, 'msg': '密码验证错误'})

    # 系统用户注册
    def post(self):
        account = request.json.get('account', None)
        password = request.json.get('password', None)
        name = request.json.get('name', None)
        hash_password = generate_password_hash(password)
        new_user = SystemUsers(account=account, password=hash_password, name=name)
        try:
            db.session.add(new_user)
            db.session.commit()
            user_info = SystemUsers.query.filter_by(account=account).first()

            return jsonify({'code': 200, 'msg': '系统用户注册成功!(*^▽^*)', 'user_info': tl.serialize(user_info)})
        except Exception as e:
            return jsonify({'code': 400, 'msg': '系统用户注册失败!', 'err': e.args})

    # 系统用户信息修改
    @login_required
    def put(self):

        uid = request.args.get('uid', None)  # 要修改用户的id
        password = request.json.get('password', None)  # 新密码
        name = request.json.get('name', None)  # 新的姓名
        if uid:
            if name:
                try:
                    SystemUsers.query.filter_by(id=uid).update({
                        'name': name
                    })
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'code': 400, 'msg': '更新用户姓名异常', 'err': e.args})
                else:
                    db.session.commit()
            if password:
                hash_password = generate_password_hash(password)  # 哈希密码
                try:
                    SystemUsers.query.filter_by(id=uid).update({
                        'password': hash_password
                    })
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'code': 400, 'msg': '更新用户密码异常', 'err': e.args})
                else:
                    db.session.commit()
            user_info = SystemUsers.query.get(uid)
            return jsonify({'code': 200, 'msg': '修改成功', 'user_info': tl.serialize(user_info)})
        else:
            return jsonify({'code': 403, 'msg': '请选择用户'})

    # 系统用户删除
    def delete(self):

        account = request.json.get('account', None)
        try:
            SystemUsers.query.filter_by(account=account).update({
                'flag': False
            })
        except Exception as e:
            return jsonify({'code': 400, 'msg': '删除系统用户异常', 'err': e.args})
        else:
            return jsonify({'code': 200, 'msg': '删除系统用户成功'})


b_user.add_url_rule('guest/', view_func=SysUser.as_view('guest'))


@b_user.route('list/', methods=['GET'])
def UserListView():
    """
    用户列表
    """
    try:
        user_list = SystemUsers.query.filter_by(flag=True).all()
        user_list = tl.serialize(user_list)
        return jsonify({'code': 200, 'msg': '获取用户列表成功', 'user_list': user_list})
    except Exception as e:
        return jsonify({'code': 400, 'msg': '获取用户列表失败', 'err': e.args})


# 返回验证码
@b_user.route('/imgCode')
def get_auth_code():
    return ic().getImgCode()


class UserOperationView(MethodView):
    """
    用户操作
    """

    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass
