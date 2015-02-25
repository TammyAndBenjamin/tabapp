"""Add cascading

Revision ID: 2f3b806c4ac
Revises: 115fd802f6a
Create Date: 2015-02-25 14:49:32.666343

"""

# revision identifiers, used by Alembic.
revision = '2f3b806c4ac'
down_revision = '115fd802f6a'

from alembic import op


def upgrade():
    op.drop_constraint('role_lineage_child_id_fkey', 'role_lineage')
    op.create_foreign_key('role_lineage_child_id_fkey', 'role_lineage', 'role', ['child_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('role_lineage_parent_id_fkey', 'role_lineage')
    op.create_foreign_key('role_lineage_parent_id_fkey', 'role_lineage', 'role', ['parent_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('contact_role_contact_id_fkey', 'contact_role')
    op.create_foreign_key('contact_role_contact_id_fkey', 'contact_role', 'contact', ['contact_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('contact_role_role_id_fkey', 'contact_role')
    op.create_foreign_key('contact_role_role_id_fkey', 'contact_role', 'role', ['role_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('retailer_contact_contact_id_fkey', 'retailer_contact')
    op.create_foreign_key('retailer_contact_contact_id_fkey', 'retailer_contact', 'contact', ['contact_id'], ['id'], ondelete='CASCADE')


def downgrade():
    """ No Downgrade """
    pass
