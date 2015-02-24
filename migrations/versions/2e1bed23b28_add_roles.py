"""Add roles

Revision ID: 2e1bed23b28
Revises: 3054f19b964
Create Date: 2015-02-18 10:28:52.810037

"""

# revision identifiers, used by Alembic.
revision = '2e1bed23b28'
down_revision = '3054f19b964'

from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY
import sqlalchemy as sa


def upgrade():
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('version', sa.DateTime(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    connection = op.get_bind()
    t = text('''
        INSERT INTO role(id, created, version, enabled, name)
        VALUES (nextval('core_seq_general'), now(), now(), true, 'admin')
    ''')
    connection.execute(t)
    op.add_column('contact', sa.Column('roles', ARRAY(sa.Integer())))
    t = text('''
        UPDATE contact
        SET roles = (SELECT array_agg(id) FROM role)
    ''')
    connection.execute(t)


def downgrade():
    op.drop_column('contact', 'roles')
    op.drop_table('role')
