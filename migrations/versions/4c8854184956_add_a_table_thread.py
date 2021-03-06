"""Add a table Thread

Revision ID: 4c8854184956
Revises: 31dffef5e3e2
Create Date: 2021-02-15 02:30:19.827276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c8854184956'
down_revision = '31dffef5e3e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('thread',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('short_name', sa.String(length=32), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('creation_timestamp', sa.DateTime(), nullable=True),
    sa.Column('text', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('short_name')
    )
    op.create_index(op.f('ix_thread_creation_timestamp'), 'thread', ['creation_timestamp'], unique=False)
    op.add_column('post', sa.Column('thread_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'post', 'thread', ['thread_id'], ['id'])
    op.drop_index('ix_users_common_name', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_common_name', 'users', ['common_name'], unique=False)
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.drop_column('post', 'thread_id')
    op.drop_index(op.f('ix_thread_creation_timestamp'), table_name='thread')
    op.drop_table('thread')
    # ### end Alembic commands ###
