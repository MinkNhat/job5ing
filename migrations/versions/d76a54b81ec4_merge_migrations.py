"""merge migrations

Revision ID: d76a54b81ec4
Revises: b27c448aebf4, f9c799218f76
Create Date: 2026-05-08 01:28:09.452445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd76a54b81ec4'
down_revision = ('b27c448aebf4', 'f9c799218f76')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
