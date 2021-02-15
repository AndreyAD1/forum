"""Add the link between thread status and post status

Revision ID: 176517b0bfc1
Revises: f415d880664f
Create Date: 2021-02-15 04:34:46.973559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '176517b0bfc1'
down_revision = 'f415d880664f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('deleted_by_thread', sa.Boolean(), nullable=True))
    op.add_column('thread', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('thread', 'deleted')
    op.drop_column('post', 'deleted_by_thread')
    # ### end Alembic commands ###