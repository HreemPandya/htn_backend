"""Add hashed_password to users

Revision ID: f1a38861940f
Revises: 452574f7d87d
Create Date: 2025-02-05 15:30:01.537980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a38861940f'
down_revision: Union[str, None] = '452574f7d87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scans')
    op.drop_table('connections')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('badge_code', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('badge_code', name='users_badge_code_key'),
    sa.UniqueConstraint('email', name='users_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('connections',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id1', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id2', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id1'], ['users.id'], name='connections_user_id1_fkey'),
    sa.ForeignKeyConstraint(['user_id2'], ['users.id'], name='connections_user_id2_fkey'),
    sa.PrimaryKeyConstraint('id', name='connections_pkey')
    )
    op.create_table('scans',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('activity_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('activity_category', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('scanned_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='scans_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='scans_pkey')
    )
    # ### end Alembic commands ###
