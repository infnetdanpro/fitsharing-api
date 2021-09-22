"""Add is_qr logic

Revision ID: 22290a433b3d
Revises: fc766a8b9d3a
Create Date: 2021-09-22 20:32:53.986005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22290a433b3d'
down_revision = 'fc766a8b9d3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('is_qr', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.alter_column('order', 'time_to_come',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('order', 'confirmation_code',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order', 'confirmation_code',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.alter_column('order', 'time_to_come',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('order', 'is_qr')
    # ### end Alembic commands ###
