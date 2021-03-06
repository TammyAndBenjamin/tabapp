"""Add product_order table

Revision ID: 528b5919261
Revises: 1315f6e3d7c
Create Date: 2015-01-18 20:44:00.146456

"""

# revision identifiers, used by Alembic.
revision = '528b5919261'
down_revision = '1315f6e3d7c'

from datetime import datetime
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY
import decimal
import sqlalchemy as sa
import tabapp.utils


def upgrade():
    op.create_table('product_order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('version', sa.DateTime(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('remote_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('shipping_country', sa.String(), nullable=False),
        sa.Column('date', sa.Date()),
        sa.Column('financial_status', sa.String(), nullable=False),
        sa.Column('subtotal_price', sa.Numeric(), nullable=False),
        sa.Column('total_tax', sa.Numeric(), nullable=False),
        sa.Column('total_price', sa.Numeric(), nullable=False),
        sa.Column('transaction_ids', ARRAY(sa.Integer), nullable=False),
        sa.Column('paid_price', sa.Numeric(), nullable=False),
        sa.Column('refunded_price', sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    fields = [
        'id',
        'name',
        'shipping_address',
        'financial_status',
        'subtotal_price',
        'total_tax',
        'total_price',
    ]
    resource = 'orders'
    params = '?page={{page}}&limit={{limit}}&fields={fields}'.format(**{
        'fields': ','.join(fields),
    })
    product_orders = tabapp.utils.list_from_resource(resource, params, limit=250, _url='https://3adfb09ddcdbafd4851e294634b8af9a:9f67e06ae055c0c11dba39df4650d0ff@tammyandbenjamin.myshopify.com/admin/')
    connection = op.get_bind()
    for product_order in product_orders:
        if product_order.get('financial_status') not in ['paid', 'partially_refunded', 'partially_paid']:
            continue
        fields = [
            'id',
            'kind',
            'status',
            'amount',
            'created_at',
        ]
        resource = 'orders/{}/transactions'.format(product_order.get('id'))
        params = '?page={{page}}&limit={{limit}}&fields={fields}'.format(**{
            'fields': ','.join(fields),
        })
        transactions = tabapp.utils.list_from_resource(resource, params, key='transactions', page=1, _url='https://3adfb09ddcdbafd4851e294634b8af9a:9f67e06ae055c0c11dba39df4650d0ff@tammyandbenjamin.myshopify.com/admin/')
        date = None
        transaction_ids = []
        paid_price = 0
        refunded_price = 0
        for transaction in transactions:
            if not transaction.get('status') == 'success':
                continue
            if transaction.get('kind') in ['authorization', 'void']:
                continue
            transaction_ids.append(transaction.get('id'))
            date = date if date else transaction.get('created_at')
            if transaction.get('kind') in ['capture', 'sale']:
                paid_price += decimal.Decimal(transaction.get('amount'))
            if transaction.get('kind') in ['refund']:
                refunded_price += decimal.Decimal(transaction.get('amount'))
        shipping_address = product_order.get('shipping_address')
        t = text('''
            INSERT INTO product_order(id, created, version, enabled, remote_id, name, shipping_country, date, financial_status, subtotal_price, total_tax, total_price, transaction_ids, paid_price, refunded_price)
            VALUES (:id, :created, :version, :enabled, :remote_id, :name, :shipping_country, :date, :financial_status, :subtotal_price, :total_tax, :total_price, :transaction_ids, :paid_price, :refunded_price)
        ''').bindparams(
            id=connection.execute(sa.Sequence('core_seq_general')),
            created=datetime.now(),
            version=datetime.now(),
            enabled=True,
            remote_id=product_order.get('id'),
            name=product_order.get('name'),
            shipping_country=shipping_address['country_code'] if shipping_address else 'FR',
            date=date,
            financial_status=product_order.get('financial_status'),
            subtotal_price=decimal.Decimal(product_order.get('subtotal_price', '0')),
            total_tax=decimal.Decimal(product_order.get('total_tax', '0')),
            total_price=decimal.Decimal(product_order.get('total_price', '0')),
            transaction_ids=transaction_ids,
            paid_price=paid_price,
            refunded_price=refunded_price
        )
        connection.execute(t)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_order')
    ### end Alembic commands ###
