# app/admin/controller.py
from .admin_blueprint import AdminBlueprint, ModelView
from app.database.models import *

admin = AdminBlueprint('admin2', __name__, url_prefix='/admin2', static_folder='static', static_url_path='/static/admin')

admin.add_view(ModelView(SystemUsers, db.session))
admin.add_view(ModelView(Roles, db.session))
admin.add_view(ModelView(Permissions, db.session))
admin.add_view(ModelView(UserRoles, db.session))
