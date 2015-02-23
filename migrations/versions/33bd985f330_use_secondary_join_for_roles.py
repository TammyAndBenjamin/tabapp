"""Use secondary join for roles

Revision ID: 33bd985f330
Revises: 548635f9ae6
Create Date: 2015-02-23 15:38:37.041528

"""

# revision identifiers, used by Alembic.
revision = '33bd985f330'
down_revision = '548635f9ae6'

from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

def upgrade():
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
    t = text('SELECT id, roles FROM contact')
    for contact_id, role_ids in connection.execute(t):
        for role_id in role_ids:
            t = text('''
                INSERT INTO contact_role(id, created, version, enabled, contact_id, role_id)
                VALUES (nextval('core_seq_general'), now(), now(), true, :contact_id, :role_id)
            ''').bindparams(
                contact_id=contact_id,
                role_id=role_id
            )
            connection.execute(t)
    op.drop_column('contact', 'roles')


def downgrade():
    op.add_column('contact', sa.Column('roles', postgresql.ARRAY(INTEGER()), autoincrement=False, nullable=True))
    connection = op.get_bind()
    t = text('SELECT contact_id, array_agg(role.id) FROM contact_role GROUP BY 1')
    for contact_id, role_ids in connection.execute(t):
        t = text('''
            UPDATE contact
            SET roles = :roles
            WHERE id = :contact_id
        ''').bindparams(
            contact_id=contact_id,
            roles=role_ids
        )
        connection.execute(t)
    op.drop_table('contact_role')
