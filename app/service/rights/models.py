from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.meta import Base


class SpecRights(Base):

    __tablename__ = "spec_rights"

    id = Column(Integer, primary_key=True)

    source_id = Column(Integer, nullable=False)
    source_type = Column(String, nullable=False)

    right_type = Column(String, nullable=False)


class UserRights(Base):

    __tablename__ = "user_rights"

    id = Column(Integer, primary_key=True)

    subject_id = Column(Integer, nullable=False)
    right_id = Column(Integer, ForeignKey('spec_rights.id'), nullable=False)

    constraints = Column(JSONB, nullable=False, default={}, server_default='{}')

    spec_right = relationship(
        "SpecRights",
        uselist=False
    )
