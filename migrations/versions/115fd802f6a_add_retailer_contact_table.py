"""Add retailer contact table

Revision ID: 115fd802f6a
Revises: 33bd985f330
Create Date: 2015-02-25 08:25:15.458266

"""

# revision identifiers, used by Alembic.
revision = '115fd802f6a'
down_revision = '61b74d97ff'

from alembic import op
from sqlalchemy import text
from sqlalchemy.sql.expression import func
import sqlalchemy as sa


def upgrade():
    op.alter_column('product_order', 'date',
               existing_type=sa.DATE(),
               nullable=False)

    op.create_table('retailer_contact',
    sa.Column('id', sa.Integer(), sa.Sequence('core_seq_general'), nullable=False),
    sa.Column('created', sa.DateTime, nullable=False, server_default=func.now()),
    sa.Column('version', sa.DateTime, nullable=False, server_default=func.now(), onupdate=func.now()),
    sa.Column('enabled', sa.Boolean, nullable=False, server_default=sa.text('true')),
    sa.Column('retailer_id', sa.Integer(), nullable=False),
    sa.Column('contact_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
    sa.ForeignKeyConstraint(['retailer_id'], ['retailer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('retailer_contact', 'id', server_default=sa.text("nextval('core_seq_general')"))

    connection = op.get_bind()
    t = text('SELECT id, contact_firstname, contact_lastname FROM retailer')
    for retailer_id, contact_firstname, contact_lastname in connection.execute(t):
        t = text('''
            INSERT INTO contact(id, created, version, enabled, firstname, lastname, email)
            VALUES (nextval('core_seq_general'), now(), now(), true, :contact_firstname, :contact_lastname, '')
            RETURNING id
        ''').bindparams(
            contact_firstname=contact_firstname,
            contact_lastname=contact_lastname
        )
        result = connection.execute(t).first()
        t = text('''
            INSERT INTO retailer_contact(retailer_id, contact_id)
            VALUES (:retailer_id, :contact_id)
        ''').bindparams(
            contact_id=result[0],
            retailer_id=retailer_id
        )
        connection.execute(t)

    op.drop_column('retailer', 'contact_lastname')
    op.drop_column('retailer', 'contact_firstname')


def downgrade():
    op.add_column('retailer', sa.Column('contact_firstname', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('retailer', sa.Column('contact_lastname', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('retailer_contact')

    op.alter_column('product_order', 'date',
               existing_type=sa.DATE(),
               nullable=True)
