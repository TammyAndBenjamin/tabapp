"""Implement roles relationship

Revision ID: 548635f9ae6
Revises: 334aa5484b4
Create Date: 2015-02-20 16:48:21.517917

"""

# revision identifiers, used by Alembic.
revision = '548635f9ae6'
down_revision = '334aa5484b4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('role_lineage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('version', sa.DateTime(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('child_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['child_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('role_lineage')
