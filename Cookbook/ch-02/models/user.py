from db import Base

from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int]  = mapped_column(primary_key=True)

    name: Mapped[str]

    email: Mapped[str]