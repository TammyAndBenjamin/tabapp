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
    op.create_table('contact_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('version', sa.DateTime(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    connection = op.get_bind()
    t = text('''
        INSERT INTO role(id, created, version, enabled, name)
        VALUES (nextval('core_seq_general'), now(), now(), true, 'admin')
    ''')
    connection.execute(t)
    t = text('SELECT id FROM role')
    for row in connection.execute(t):
        role_id = row[0]
        t = text('''
            INSERT INTO contact_role(id, created, version, enabled, role_id, contact_id)
            SELECT nextval('core_seq_general'), now(), now(), true, :role_id, contact.id
            FROM contact
        ''').bindparams(role_id=role_id)
        connection.execute(t)



def downgrade():
    op.drop_table('contact_role')
    op.drop_table('role')
