from app.core.database import Base
from sqlalchemy import Integer, String, func, Column, ForeignKey, DateTime, Boolean, Table

# Many-to-many association table for user group memberships
user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Column('is_admin', Boolean, default=False),
)
