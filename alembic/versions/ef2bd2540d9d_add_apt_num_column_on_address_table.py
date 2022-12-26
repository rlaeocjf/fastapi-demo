"""add apt_num column on address table

Revision ID: ef2bd2540d9d
Revises: 0a1335bf8555
Create Date: 2022-12-08 17:16:24.679016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef2bd2540d9d'
down_revision = '0a1335bf8555'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')

