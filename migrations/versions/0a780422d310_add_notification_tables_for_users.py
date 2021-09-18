"""Add notification tables for users

Revision ID: 0a780422d310
Revises: 413f28323455
Create Date: 2021-08-15 13:24:24.095427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a780422d310'
down_revision = '413f28323455'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('club_id', sa.Integer(), nullable=True),
    sa.Column('club_user_id', sa.Integer(), nullable=True),
    sa.Column('notify_type', sa.Enum('info', 'warning', 'error', name='notificationtype'), nullable=False),
    sa.Column('notify_text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['club_id'], ['club.id'], ),
    sa.ForeignKeyConstraint(['club_user_id'], ['club_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification_view',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('notification_id', sa.Integer(), nullable=False),
    sa.Column('club_user_id', sa.Integer(), nullable=True),
    sa.Column('viewed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['club_user_id'], ['club_user.id'], ),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification_view')
    op.drop_table('notification')
    # ### end Alembic commands ###