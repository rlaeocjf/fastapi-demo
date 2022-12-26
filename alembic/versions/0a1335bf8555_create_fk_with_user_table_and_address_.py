"""create fk with user table and address table

Revision ID: 0a1335bf8555
Revises: e1447fa196ba
Create Date: 2022-12-08 14:52:09.974726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a1335bf8555'
down_revision = 'e1447fa196ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('address_id', sa.Integer, nullable=True))
    op.create_foreign_key('address_users_fk', source_table="users", referent_table="address",
                          local_cols=['address_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('address_users_fk', table_name="users")
    op.drop_column('user', 'address_id')
