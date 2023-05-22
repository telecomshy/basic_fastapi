from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Column, ForeignKey, Table
from typing import Optional
from backend.db.base import Base

user_role_relationship = Table(
    "user_role_relationship",
    Base.metadata,
    # 同时设置为primary_key会成为联合主键
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)

role_perm_relationship = Table(
    "role_perm_relationship",
    Base.metadata,
    # 同时设置为primary_key会成为联合主键
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("perm_id", ForeignKey("permission.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str]
    email: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    roles: Mapped[list[Role]] = relationship(secondary=user_role_relationship, back_populates="users")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str]
    users: Mapped[list[User]] = relationship(secondary=user_role_relationship, back_populates="roles")
    perms: Mapped[list[Permission]] = relationship(secondary=role_perm_relationship, back_populates="roles")

    def __repr__(self) -> str:
        return f"Role(role_name ={self.role_name!r})"


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    perm_name: Mapped[str]  # 展示给前端的权限，如：删除用户，添加用户等
    perm_rule: Mapped[str]  # 实际的权限规则
    roles: Mapped[list[Role]] = relationship(secondary=role_perm_relationship, back_populates="perms")

    def __repr__(self) -> str:
        return f"Permission(perm_name ={self.perm_name!r}, perm_rule={self.perm_rule!r})"
