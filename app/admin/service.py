from app.models import User

def get_users(page=1, keyword=None, role=None, status=None):
    query = User.query

    if keyword:
        query = query.filter(User.email.contains(keyword))

    if role and role != "all":
        query = query.filter(User.role == role)

    if status and status != "all":
        query = query.filter(User.status == status)

    return query.paginate(page=page, per_page=5)