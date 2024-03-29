"""Add service type

Revision ID: bf7d8a3cced8
Revises: 90e5d231bd3a
Create Date: 2021-08-08 14:58:27.432655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf7d8a3cced8'
down_revision = '90e5d231bd3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.get_bind().execute("""
        CREATE TYPE servicetype AS ENUM ('main', 'additional');
    """)
    op.add_column('club_service', sa.Column('service_type', sa.Enum('main', 'additional', name='servicetype'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('club_service', 'service_type')
    # ### end Alembic commands ###
