"""Fix sequences

Revision ID: 61b74d97ff
Revises: 33bd985f330
Create Date: 2015-02-25 08:44:49.366493

"""

# revision identifiers, used by Alembic.
revision = '61b74d97ff'
down_revision = '33bd985f330'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('product_order', 'date', existing_type=sa.DATE(), nullable=False)
    op.alter_column('role', 'id', server_default=sa.text("nextval('core_seq_general')"))
    op.alter_column('lead', 'id', server_default=sa.text("nextval('core_seq_general')"))
    op.alter_column('contact_role', 'id', server_default=sa.text("nextval('core_seq_general')"))
    op.alter_column('role_lineage', 'id', server_default=sa.text("nextval('core_seq_general')"))
    op.alter_column('product_order', 'id', server_default=sa.text("nextval('core_seq_general')"))

    connection = op.get_bind()
    t = sa.text('DROP SEQUENCE IF EXISTS role_id_seq')
    connection.execute(t)
    t = sa.text('DROP SEQUENCE IF EXISTS lead_id_seq')
    connection.execute(t)
    t = sa.text('DROP SEQUENCE IF EXISTS contact_role_id_seq')
    connection.execute(t)
    t = sa.text('DROP SEQUENCE IF EXISTS role_lineage_id_seq')
    connection.execute(t)
    t = sa.text('DROP SEQUENCE IF EXISTS product_order_id_seq')
    connection.execute(t)


def downgrade():
    op.alter_column('product_order', 'date', existing_type=sa.DATE(), nullable=True)
