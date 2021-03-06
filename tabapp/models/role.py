# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import aliased, relationship
from tabapp.models import db

RoleLineage = db.Table('role_lineage',
    db.Column('id', db.Integer, db.Sequence('core_seq_general'), primary_key=True),
    db.Column('created', db.DateTime, nullable=False, default=func.now()),
    db.Column('version', db.DateTime, nullable=False, default=func.now(), onupdate=func.now()),
    db.Column('enabled', db.Boolean, nullable=False, default=True),
    db.Column('parent_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False),
    db.Column('child_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
)


class Role(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)
    roles = relationship('Role', secondary='role_lineage', primaryjoin='Role.id==role_lineage.c.parent_id', secondaryjoin='Role.id==role_lineage.c.child_id')

    def _get_descendants(self):
        descendants = db.session.query(
            RoleLineage.c.child_id
        ).filter(
            RoleLineage.c.parent_id == self.id
        ).cte(name="descendants", recursive=True)

        children = aliased(descendants, name="child")
        parents = aliased(RoleLineage, name="parent")

        descendants = descendants.union(
            db.session.query(
                parents.c.child_id
            ).filter(
                parents.c.parent_id == children.c.child_id
            )
        )

        """
            db.session.query(Role).filter(Role.id == descendants.c.child_id)
            doesn't work, why ?
        """
        q = Role.query.filter(Role.id == descendants.c.child_id)
        _records = q.all()
        return _records
    descendants = property(_get_descendants)
