# coding:utf-8
from .. import db
from datetime import datetime


class BaseModel(object):
    '''
    模型基类，为每个模型补充创建时间与更新时间和逻辑删除符
    '''
    id = db.Column(db.Integer, primary_key=True)  # 主键id
    # 记录创建时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 记录更新时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # 逻辑删除符
    flag = db.Column(db.Boolean, default=True)

    # 根据前端传的值构造对应的对象
    def get_model(self, input_dict):
        temp = self.__class__()
        for k, v in input_dict.items():
            setattr(temp, k, v)
        print('构造对象:', self.__class__.__name__)
        return temp


class SystemUsers(db.Model, BaseModel):
    """用户表"""
    __tablename__ = "system_users"
    # __bind_key__ = 'server'
    account = db.Column(db.String(20), unique=True, nullable=False)  # 账户
    password = db.Column(db.String(120), nullable=False)  # 密码
    name = db.Column(db.String(20), unique=True)  # 名称

    def __repr__(self):
        """可以在显示对象的时候更直观"""
        return "SystemUsers object: id={},name={}".format(str(self.id), self.name)


class Roles(db.Model, BaseModel):
    """角色表"""
    __tablename__ = 'roles'
    # __bind_key__ = 'server'
    name = db.Column(db.String(50), unique=True, nullable=True)  # 角色名称

    def __repr__(self):
        """可以在显示对象的时候更直观"""
        return "Roles object: id={},name={}".format(str(self.id), self.name)


class Permissions(db.Model, BaseModel):
    """权限表"""
    __tablename__ = 'permissions'
    # __bind_key__ = 'server'
    name = db.Column(db.String(50), unique=True, nullable=True)  # 权限名称


class UserRoles(db.Model, BaseModel):
    """用户角色关联表"""
    __tablename__ = 'user_roles'
    # __bind_key__ = 'server'
    user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'))  # 用户id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 角色id
    role = db.relationship('Roles', backref='_role')  # 关联role表
    user = db.relationship('SystemUsers', backref='_user')  # 关联permission表


class RolePermissions(db.Model, BaseModel):
    """角色权限关联表"""
    __tablename__ = 'role_permissons'
    # __bind_key__ = 'server'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 角色id
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))  # 权限id
    role = db.relationship('Roles', backref='role')  # 关联role表
    permission = db.relationship('Permissions', backref='permission')  # 关联permission表


class Operations(db.Model, BaseModel):
    """操作表"""
    __tablename__ = 'operations'
    # __bind_key__ = 'server'
    name = db.Column(db.String(50), unique=True, nullable=True)  # 操作名称
    log_format = db.Column(db.String(250))  # 操作的日志格式


class PerOperations(db.Model, BaseModel):
    """权限操作关联表"""
    __tablename__ = 'permission_operations'
    # __bind_key__ = 'server'
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'))  # 操作id
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))  # 权限id


class Log(db.Model, BaseModel):
    """日志表"""
    __tablename__ = 'logs'
    # __bind_key__ = 'server'
    user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'))  # 用户id
    # type_id = db.Column(db.Integer, db.ForeignKey('log_types.id')) # 日志类型id
    text = db.Column(db.String(250))


class LogType(db.Model, BaseModel):
    """日志类型表"""
    __tablename__ = 'log_types'
    # __bind_key__ = 'server'
    name = db.Column(db.String(20), unique=True)  # 日志类型名称
    description = db.Column(db.String(20), unique=True)  # 类型描述


class Purachase(db.Model, BaseModel):
    """采购表"""
    __tablename__ = 'purchase'
    __bind_key__ = 'server'
    # 采购单号
    purchase_no = db.Column(db.String(20), unique=True, nullable=False)
    # 采购日期
    purchase_date = db.Column(db.DateTime, default=datetime.now)
    # 采购人
    purchase_user = db.Column(db.String(20), nullable=False)
    # 采购人电话
    purchase_phone = db.Column(db.String(20), nullable=False)
    # 采购人邮箱
    purchase_email = db.Column(db.String(20), nullable=False)
    # 采购人地址
    purchase_address = db.Column(db.String(20), nullable=False)
    # 采购人邮编
    purchase_postcode = db.Column(db.String(20), nullable=False)
    # 采购人传真
    purchase_fax = db.Column(db.String(20), nullable=False)
    # 采购人网址
    purchase_website = db.Column(db.String(20), nullable=False)
    # 采购人备注
    purchase_remark = db.Column(db.String(20), nullable=False)
    # 采购人状态
    purchase_status = db.Column(db.String(20), nullable=False)
    # 采购人类型
    purchase_type = db.Column(db.String(20), nullable=False)
    # 采购人类型
    purchase_type = db.Column(db.String(20), nullable=False)


class Employee(db.Model, BaseModel):
    """员工表"""
    __tablename__ = 'employee'
    __bind_key__ = 'server'
    # 员工编号
    employee_no = db.Column(db.String(20), unique=True, nullable=False)
    # 员工姓名
    employee_name = db.Column(db.String(20), nullable=False)
    # 员工性别
    employee_sex = db.Column(db.String(20), nullable=False)