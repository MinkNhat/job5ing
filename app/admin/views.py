from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask import redirect, url_for


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Senior Tip: Để True khi dev, nhưng nhớ thêm logic check role khi deploy nhé!
        return True


class UserAdminView(ModelView):
    column_list = ('id', 'email', 'is_admin', 'is_employer', 'is_active', 'created_at')

    column_labels = {
        'id': 'ID',
        'email': 'Tên đăng nhập (Email)',
        'is_admin': 'Quyền Quản trị',
        'is_employer': 'Là Nhà tuyển dụng',
        'is_active': 'Trạng thái hoạt động',
        'created_at': 'Ngày tham gia'
    }

    column_formatters = {
        'id': lambda v, c, m, p: f"{m.id:03d}"
    }

class PostAdminView(ModelView):
    column_list = ('id', 'title', 'status', 'is_pinned', 'created_at')
    column_editable_list = ('status', 'is_pinned')
    column_filters = ('status', 'is_pinned')
    column_searchable_list = ('title',)

    column_labels = {
        'id': 'Mã tin',
        'title': 'Tiêu đề',
        'status': 'Trạng thái',
        'is_pinned': 'Ghim lên đầu',
        'created_at': 'Ngày đăng'
    }