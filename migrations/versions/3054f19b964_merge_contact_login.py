"""Merge Contact/Login

Revision ID: 3054f19b964
Revises: 528b5919261
Create Date: 2015-02-18 08:23:56.307561

"""

# revision identifiers, used by Alembic.
revision = '3054f19b964'
down_revision = '528b5919261'

from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
import sqlalchemy as sa
import sqlalchemy_utils

def upgrade():
    op.add_column('contact', sa.Column('username', sa.String(), nullable=True))
    op.add_column('contact', sa.Column('password', sqlalchemy_utils.PasswordType(), nullable=True))
    connection = op.get_bind()
    t = text('''
        UPDATE contact
        SET username = login.username, password = login.password
        FROM login
        WHERE login.contact_id = contact.id
    ''')
    connection.execute(t)
    op.create_index(op.f('ix_contact_username'), 'contact', ['username'], unique=True)
    op.drop_table('login')


def downgrade():
    op.create_table('login',
        sa.Column('id', sa.INTEGER(), sa.Sequence('core_seq_general'), autoincrement=False, nullable=False),
        sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False, default=func.now()),
        sa.Column('version', postgresql.TIMESTAMP(), autoincrement=False, nullable=False, default=func.now()),
        sa.Column('enabled', sa.BOOLEAN(), autoincrement=False, nullable=False, default=True),
        sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('password', sqlalchemy_utils.PasswordType(), autoincrement=False, nullable=True),
        sa.Column('contact_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], name='login_contact_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='login_pkey')
    )
    connection = op.get_bind()
    t = text('''
        INSERT INTO login(id, created, version, enabled, username, password, contact_id)
        SELECT nextval('core_seq_general'), now(), now(), true, contact.username, contact.password, contact.id
        FROM contact
    ''')
    connection.execute(t)
    op.drop_index(op.f('ix_contact_username'), table_name='contact')
    op.drop_column('contact', 'username')
    op.drop_column('contact', 'password')
