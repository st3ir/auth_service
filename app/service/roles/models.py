from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.meta import Base


class Role(Base):

    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    rolename = Column(String, nullable=False, unique=True)

    users = relationship(
        "User",
        secondary="user_role",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"{self.rolename}"


class UserRole(Base):

    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
