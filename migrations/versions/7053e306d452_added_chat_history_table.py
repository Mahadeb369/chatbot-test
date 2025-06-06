"""Added chat_history table

Revision ID: 7053e306d452
Revises: 125dad6e3cdb
Create Date: 2025-03-24 08:27:15.803542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7053e306d452'
down_revision = '125dad6e3cdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # with op.batch_alter_table('media_property_occupancy_report', schema=None) as batch_op:
    #     batch_op.drop_column('net_revenue')
    #     batch_op.drop_column('package_name')

    # with op.batch_alter_table('media_property_occupancy_status', schema=None) as batch_op:
    #     batch_op.drop_column('2nd_blocked_by')
    #     batch_op.drop_column('2nd_blocked_for')
    #     batch_op.drop_column('third_blocked_by')
    #     batch_op.drop_column('1st_blocking_till')
    #     batch_op.drop_column('third_blocked_for')
    #     batch_op.drop_column('third_blocked_till')
    #     batch_op.drop_column('1st_blocked_by')
    #     batch_op.drop_column('2nd_blocking_till')
    #     batch_op.drop_column('1st_blocked_for')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('media_property_occupancy_status', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('1st_blocked_for', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('2nd_blocking_till', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('1st_blocked_by', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('third_blocked_till', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('third_blocked_for', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('1st_blocking_till', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('third_blocked_by', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('2nd_blocked_for', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        # batch_op.add_column(sa.Column('2nd_blocked_by', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        pass

    with op.batch_alter_table('media_property_occupancy_report', schema=None) as batch_op:
        batch_op.add_column(sa.Column('package_name', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('net_revenue', sa.INTEGER(), autoincrement=False, nullable=True))

    op.drop_table('chat_history')
    # ### end Alembic commands ###
