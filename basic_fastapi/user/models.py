from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from typing import Optional
from ..database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str]
    phone_number: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, phone_number={self.phone_number!r})"
