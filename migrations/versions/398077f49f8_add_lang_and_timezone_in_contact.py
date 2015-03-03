"""Add lang and timezone in Contact

Revision ID: 398077f49f8
Revises: 2f3b806c4ac
Create Date: 2015-03-03 09:47:43.388070

"""

# revision identifiers, used by Alembic.
revision = '398077f49f8'
down_revision = '2f3b806c4ac'

from alembic import op
from sqlalchemy.sql.expression import func
import sqlalchemy as sa


def upgrade():
    op.create_table('locale',
    sa.Column('id', sa.Integer(), nullable=False, server_default=sa.text("nextval('core_seq_general')")),
    sa.Column('created', sa.DateTime(), nullable=False, server_default=func.now()),
    sa.Column('version', sa.DateTime(), nullable=False, server_default=func.now()),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type', 'value')
    )

    connection = op.get_bind()
    t = sa.text('''
        INSERT INTO locale(enabled, type, label, value) VALUES
            (true, 'lang', 'English', 'en'),
            (true, 'lang', 'Français', 'fr'),
            (true, 'lang', '中国', 'cn'),
            (true, 'tz', 'Europe/Paris', 'Europe/Paris')
    ''')
    connection.execute(t)

    op.add_column('contact', sa.Column('lang_id', sa.Integer(), sa.ForeignKey('locale.id'), nullable=True))
    op.add_column('contact', sa.Column('tz_id', sa.Integer(), sa.ForeignKey('locale.id'), nullable=True))


def downgrade():
    op.drop_column('contact', 'tz_id')
    op.drop_column('contact', 'lang_id')
    op.drop_table('locale')
