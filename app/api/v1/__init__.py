from flask import Blueprint

# 创建蓝图
b_user = Blueprint('user', __name__) # 定义用户蓝图

from . import user