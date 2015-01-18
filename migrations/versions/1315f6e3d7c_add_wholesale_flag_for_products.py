"""Add wholesale flag for products

Revision ID: 1315f6e3d7c
Revises: 53f2384e764
Create Date: 2015-01-18 19:20:59.612858

"""

# revision identifiers, used by Alembic.
revision = '1315f6e3d7c'
down_revision = '53f2384e764'

from alembic import op
from sqlalchemy import text
import sqlalchemy as sa


def upgrade():
    op.add_column('product', sa.Column('is_wholesale', sa.Boolean()))
    connection = op.get_bind()
    t = text('SELECT id, title FROM product')
    for product_id, product_title in connection.execute(t):
        t = text('''
            UPDATE product
            SET is_wholesale = :is_wholesale
            WHERE id = :product_id
        ''').bindparams(
            product_id=product_id,
            is_wholesale=product_title.startswith('WH -')
        )
        connection.execute(t)
    op.alter_column('product', 'is_wholesale', nullable=False)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'is_wholesale')
    ### end Alembic commands ###
