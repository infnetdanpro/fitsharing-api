"""Add max_price for each order

Revision ID: 504482fe74a7
Revises: f163b2eea97d
Create Date: 2021-10-03 17:10:58.042215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '504482fe74a7'
down_revision = 'f163b2eea97d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('max_minutes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'max_minutes')
    # ### end Alembic commands ###