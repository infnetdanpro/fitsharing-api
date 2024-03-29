"""Fix: add h1

Revision ID: 6f36b123f2b2
Revises: 046e93629028
Create Date: 2021-06-19 19:13:01.464911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f36b123f2b2'
down_revision = '046e93629028'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('page', sa.Column('h1', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'page', ['slug'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('page', 'h1')
    # ### end Alembic commands ###
