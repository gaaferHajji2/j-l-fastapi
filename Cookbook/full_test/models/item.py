from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Item(Base):
    __tablename__ == 'items' # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)