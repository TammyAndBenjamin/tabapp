"""Add urls table

Revision ID: 519d34d9435
Revises: 583a441f53f
Create Date: 2014-11-04 16:26:43.127590

"""

# revision identifiers, used by Alembic.
revision = '519d34d9435'
down_revision = '583a441f53f'

from alembic import op
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.create_table('url',
        sa.Column('id', sa.Integer(), sa.Sequence('core_seq_general'), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False, default=datetime.now),
        sa.Column('version', sa.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('long_url', sqlalchemy_utils.URLType(), nullable=False),
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False, default=datetime.now),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('url_click',
        sa.Column('id', sa.Integer(), sa.Sequence('core_seq_general'), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False, default=datetime.now),
        sa.Column('version', sa.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('ip_address', sqlalchemy_utils.IPAddressType(), nullable=True),
        sa.Column('url_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['url_id'], ['url.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('url_click')
    op.drop_table('url')
