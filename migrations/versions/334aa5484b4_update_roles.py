"""Update roles

Revision ID: 334aa5484b4
Revises: 2e1bed23b28
Create Date: 2015-02-19 18:57:21.643254

"""

# revision identifiers, used by Alembic.
revision = '334aa5484b4'
down_revision = '2e1bed23b28'

from alembic import op
from sqlalchemy import text
import sqlalchemy as sa


def upgrade():
    op.add_column('role', sa.Column('key', sa.String(), nullable=True))
    connection = op.get_bind()
    t = text('UPDATE role SET key = name')
    connection.execute(t)
    op.alter_column('role', 'key', existing_type=sa.String(), nullable=False)
    op.alter_column('role', 'name',
               existing_type=sa.String(),
               nullable=False)


def downgrade():
    op.alter_column('role', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('role', 'key')
