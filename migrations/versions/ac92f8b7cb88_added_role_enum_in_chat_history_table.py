"""Added role enum in chat_history table

Revision ID: ac92f8b7cb88
Revises: 7053e306d452
Create Date: 2025-03-24 08:44:09.361763

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ac92f8b7cb88'
down_revision = '7053e306d452'
branch_labels = None
depends_on = None

# Define the ENUM type
role_enum = postgresql.ENUM('Human', 'AI', name='role_enum')

def upgrade():
    # Create the ENUM type in PostgreSQL
    role_enum.create(op.get_bind())

    # Alter the column to use the ENUM
    with op.batch_alter_table('chat_history', schema=None) as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=sa.VARCHAR(length=10),
            type_=role_enum,
            postgresql_using="role::role_enum",  # 👈
            existing_nullable=False
        )

def downgrade():
    # Revert the column back to VARCHAR
    with op.batch_alter_table('chat_history', schema=None) as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=role_enum,
            type_=sa.VARCHAR(length=10),
            postgresql_using="role::varchar",  # optional for downgrade clarity
            existing_nullable=False
        )

    # Drop the ENUM type
    role_enum.drop(op.get_bind())

