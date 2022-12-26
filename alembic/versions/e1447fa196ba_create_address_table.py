"""create address table

Revision ID: e1447fa196ba
Revises: 6c731f376645
Create Date: 2022-12-08 14:41:14.574106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1447fa196ba'
down_revision = '6c731f376645'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer, nullable=False, primary_key=True),
                    sa.Column('address1', sa.String, nullable=False),
                    sa.Column('address2', sa.String, nullable=False),
                    sa.Column('city', sa.String, nullable=False),
                    sa.Column('state', sa.String, nullable=False),
                    sa.Column('country', sa.String, nullable=False),
                    sa.Column('postalcode', sa.String, nullable=False),
                    )


def downgrade() -> None:
    op.drop_table('address')
